from io import TextIOWrapper
from pydantic import BaseModel
from pathlib import Path
from typing import ClassVar, Generator, Self
from threading import Lock
import os
import tempfile

from models._encode_str import _encode_str, _decode_str

class PersistedModel(BaseModel):
	"""
	An extension to the Pydantic `BaseModel` class which adds a handful of 
	functions to persist models in storage.
	"""

	_mutex: ClassVar[Lock] = Lock()

	def primary_key(self) -> any:
		primary_key_field = next(iter(self.__class__.model_fields.keys()))
		return getattr(self, primary_key_field)

	def to_csv_row(self) -> str:
		row: str = ""
		for value in self.model_dump().values():
			row += _encode_str(str(value)) + ","
		return row[:-1]
	
	def put(self, data_dir: str = "./data") -> None:
		self.__class__._mutex.acquire()

		original_file = self.__class__.read_csv_file(data_dir = data_dir)
		updated_file = tempfile.TemporaryFile("w", delete = False, dir = data_dir)
		prev_record_found = False

		primary_key = str(self.primary_key())

		line = original_file.readline() 
		while line != "":
			if line.startswith(primary_key):
				prev_record_found = True
				updated_file.write(self.to_csv_row() + "\n")
			else:
				updated_file.write(line)
			line = original_file.readline()

		if not prev_record_found:
			updated_file.write(self.to_csv_row() + "\n")

		original_file.close()
		updated_file.close()

		os.replace(updated_file.name, original_file.name)

		self.__class__._mutex.release()

	def delete(self, data_dir: str = "./data") -> None:
		self.__class__._mutex.acquire()

		original_file = self.__class__.read_csv_file(data_dir = data_dir)
		updated_file = tempfile.TemporaryFile("w", delete = False, dir = data_dir)

		primary_key = str(self.primary_key())

		line = original_file.readline() 
		while line != "":
			if not line.startswith(primary_key):
				updated_file.write(line)
			line = original_file.readline()

		original_file.close()
		updated_file.close()

		os.replace(updated_file.name, original_file.name)

		self.__class__._mutex.release()

	@classmethod
	def to_csv_header(cls) -> str:
		header: str = ""
		for key in cls.model_fields.keys():
			header += str(key) + ","
		return header[:-1]

	@classmethod
	def read_csv_file(cls, data_dir: str = "./data") -> TextIOWrapper:
		file_path = Path(data_dir + "/" + cls.__name__ + ".csv")
		if file_path.exists():
			return file_path.open("r", encoding = "utf-8")

		file_path.parent.mkdir(
			parents = True, 
			exist_ok = True,
		)
		w = file_path.open("a+", encoding = "utf-8")
		w.write(cls.to_csv_header() + "\n")
		w.close()
		
		return file_path.open("r", encoding = "utf-8")

	@classmethod
	def from_csv_row(cls, csv_row: str) -> Self:
		fields = {}
		values = csv_row.split(",")
		keys = cls.model_fields.keys()
		i = 0
		for key, value in zip(keys, values):
			if cls.model_fields[key].annotation is str:
				value = _decode_str(value)
			fields[key] = value
		return cls.model_validate(fields)
	
	@classmethod
	def drop_table(cls, data_dir: str = "./data") -> None:
		cls._mutex.acquire()
		file_path = Path(data_dir + "/" + cls.__name__ + ".csv")
		file_path.unlink(missing_ok = True)
		cls._mutex.release()

	@classmethod
	def get_by_primary_key(cls, search_key: any, data_dir: str = "./data") -> Self | None:
		key_str = str(search_key)

		with cls.read_csv_file(data_dir = data_dir) as r:
			r.readline() # skip the header
			line = r.readline()
			while line != "":
				if line.startswith(key_str):
					return cls.from_csv_row(line)
				line = r.readline()

		return None

	@classmethod
	def get_where(cls, data_dir = "./data", **search_fields) -> Generator[Self, None, None]:
		search_values: str = [] 
		for field in cls.model_fields.keys():
			if field in search_fields:
				search_values.append(_encode_str(str(search_fields[field])))
			else:
				search_values.append(None)
		
		with cls.read_csv_file(data_dir = data_dir) as r:
			r.readline() # skip the header
			line = r.readline()
			while line != "":
				values: list[str] = line.\
					removesuffix("\n").\
					split(",")
				match_found = True
				for i in range(len(values)):
					if search_values[i] == None:
						continue
					if search_values[i] != values[i]:
						match_found = False
						break
				if match_found:
					yield cls.from_csv_row(line)
				line = r.readline()

	@classmethod
	def get_first_where(cls, data_dir = "./data", **search_fields) -> Self | None:
		search_values: str = [] 
		for field in cls.model_fields.keys():
			if field in search_fields:
				search_values.append(_encode_str(str(search_fields[field])))
			else:
				search_values.append(None)
		
		with cls.read_csv_file(data_dir = data_dir) as r:
			r.readline() # skip the header
			line = r.readline()
			while line != "":
				values: list[str] = line.\
					removesuffix("\n").\
					split(",")
				match_found = True
				for i in range(len(values)):
					if search_values[i] == None:
						continue
					if search_values[i] != values[i]:
						match_found = False
						break
				if match_found:
					return cls.from_csv_row(line)
				line = r.readline()

		return None
