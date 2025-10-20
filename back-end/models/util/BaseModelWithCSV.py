from io import TextIOWrapper
from typing import IO
from pydantic import BaseModel
from pathlib import Path

class BaseModelWithCSV(BaseModel):
	"""
	A simple extension to the Pydantic `BaseModel` class which just adds a
	couple of functions that help work with CSV files.
	"""

	def to_csv_row(self) -> str:
		row: str = ""
		for value in self.model_dump().values():
			row += str(value) + ","
		return row[:-1]

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
		with file_path.open("a+", encoding = "utf-8") as w:
			w.write(cls.to_csv_header() + "\n")
		
		return file_path.open("r", encoding = "utf-8")

	@classmethod
	def from_csv_row(cls, csv_row: str):
		fields = {}
		values = csv_row.split(",")
		keys = cls.model_fields.keys()
		i = 0
		for key, value in zip(keys, values):
			fields[key] = value
		return cls.model_validate(fields)
