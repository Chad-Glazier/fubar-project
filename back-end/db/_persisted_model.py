from io import TextIOWrapper
from pydantic import BaseModel
from pathlib import Path
from typing import ClassVar, Generator, Self
from threading import Lock
import os
import tempfile

from db._encode_str import _encode_str, _decode_str

class _PersistedModel(BaseModel):
	"""
	An extension to the Pydantic `BaseModel` class which adds a handful of 
	functions to persist models in storage. In order to create a table in the 
	database, you should create a class which inherits from this one and then 
	use the methods of this class to manage records in persistent storage.

	NOTE: Each class that inherits from this one (i.e., each table in the
	database) must ensure that each instance has a unique identifier, analogous
	to an SQL primary key. The first field defined in the class is taken to be
	that class's primary key. For example,

	>>> class User(_PersistedModel):
			id: str
			name: str
			# ...

	In this case, `id: str` is taken to be the primary key of the `User` table
	solely because it is the first field defined for the class. This means that
	If any two instances of `User` have the same `id`, it will be assumed that
	they represent the same record in the database.
	"""

	data_dir: ClassVar[str] = "./data"
	"""
	Defines the directory where instances of this model should be stored.
	"""
	_mutex: ClassVar[Lock] = Lock()

	def _primary_key(self) -> any:
		primary_key_field = next(iter(self.__class__.model_fields.keys()))
		return getattr(self, primary_key_field)

	def _to_csv_row(self) -> str:
		row: str = ""
		for value in self.model_dump().values():
			row += _encode_str(str(value)) + ","
		return row[:-1]
	
	def patch(self) -> bool:
		"""
		Searches the persistent storage for a matching record (compared via
		the primary key; i.e. the first field defined on the class) and updates
		it to match this instance if it is found. If an existing is not found,
		then this method does nothing.

		Returns:
			bool: True when a record was successfully updated, and False when
			a matching record couldn't be found.
		"""

		self.__class__._mutex.acquire()

		original_file = self.__class__._read_csv_file()
		updated_file = tempfile.TemporaryFile(
			"w", delete = False, dir = self.__class__.data_dir)
		prev_record_found = False

		primary_key = _encode_str(str(self._primary_key()))

		line = original_file.readline() 
		while line != "":
			if line.startswith(primary_key):
				prev_record_found = True
				updated_file.write(self._to_csv_row() + "\n")
			else:
				updated_file.write(line)
			line = original_file.readline()

		original_file.close()
		updated_file.close()

		if prev_record_found:
			os.replace(updated_file.name, original_file.name)
		else:
			os.unlink(updated_file.name)

		self.__class__._mutex.release()

		return prev_record_found

	def post(self) -> bool:
		"""
		Searches the persistent storage for a matching record (compared via
		the primary key; i.e. the first field defined on the class). If an 
		existing record is not found, then this method creates a new one to
		represent this instance. If an existing record is found, then this
		method does nothing.

		Returns:
			bool: True when a record was successfully created, and False when
			an existing record was found to already exist.
		"""

		self.__class__._mutex.acquire()

		original_file = self.__class__._read_csv_file()
		updated_file = tempfile.TemporaryFile(
			"w", delete = False, dir = self.__class__.data_dir)
		prev_record_found = False

		primary_key = _encode_str(str(self._primary_key()))

		line = original_file.readline() 
		while line != "":
			if line.startswith(primary_key):
				prev_record_found = True
				break
			else:
				updated_file.write(line)
			line = original_file.readline()
		
		if not prev_record_found:
			updated_file.write(self._to_csv_row() + "\n")

		original_file.close()
		updated_file.close()

		if not prev_record_found:
			os.replace(updated_file.name, original_file.name)
		else:
			os.unlink(updated_file.name)

		self.__class__._mutex.release()

		return not prev_record_found
	
	def put(self) -> None:
		"""
		Stores the model instance in persistent storage. If this instance
		exists in storage (as identified by the primary key; i.e. the first
		field defined on the class), then this will update the existing record
		to match the instance's fields. If the instance does not already exist
		in storage, then a new record will be created.

		If you want to ensure that an existing record is not updated, then you
		should use the `post` method instead. If you want to ensure that an
		existing record already exists, then you should use `patch`.

		Returns:
			None.
		"""

		self.__class__._mutex.acquire()

		original_file = self.__class__._read_csv_file()
		updated_file = tempfile.TemporaryFile(
			"w", delete = False, dir = self.__class__.data_dir)
		prev_record_found = False

		primary_key = _encode_str(str(self._primary_key()))

		line = original_file.readline() 
		while line != "":
			if line.startswith(primary_key):
				prev_record_found = True
				updated_file.write(self._to_csv_row() + "\n")
			else:
				updated_file.write(line)
			line = original_file.readline()

		if not prev_record_found:
			updated_file.write(self._to_csv_row() + "\n")

		original_file.close()
		updated_file.close()

		os.replace(updated_file.name, original_file.name)

		self.__class__._mutex.release()

	def delete(self) -> None:
		"""
		Deletes the record of this instance from persistent storage.

		Returns:
			None.
		"""

		self.__class__._mutex.acquire()

		original_file = self.__class__._read_csv_file()
		updated_file = tempfile.TemporaryFile(
			"w", delete = False, dir = self.__class__.data_dir)

		primary_key = _encode_str(str(self._primary_key()))

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
	def _to_csv_header(cls) -> str:
		header: str = ""
		for key in cls.model_fields.keys():
			header += str(key) + ","
		return header[:-1]

	@classmethod
	def _read_csv_file(cls) -> TextIOWrapper:
		file_path = Path(cls.data_dir + "/" + cls.__name__ + ".csv")
		if file_path.exists():
			return file_path.open("r", encoding = "utf-8")

		file_path.parent.mkdir(
			parents = True, 
			exist_ok = True,
		)
		with file_path.open("a+", encoding = "utf-8") as w:
			w.write(cls._to_csv_header() + "\n")
		
		return file_path.open("r", encoding = "utf-8")

	@classmethod
	def _from_csv_row(cls, csv_row: str) -> Self:
		fields = {}
		values = csv_row.split(",")
		keys = cls.model_fields.keys()
		for key, value in zip(keys, values):
			if cls.model_fields[key].annotation is str:
				value = _decode_str(value)
			fields[key] = value
		return cls.model_validate(fields)
	
	@classmethod
	def _drop_table(cls) -> None:
		cls._mutex.acquire()
		file_path = Path(cls.data_dir + "/" + cls.__name__ + ".csv")
		file_path.unlink(missing_ok = True)
		cls._mutex.release()

	@classmethod
	def get_by_primary_key(cls, search_key: any) -> Self | None:
		"""
		Returns the unique persisted instance of this class that has the 
		specified primary key (recall that the primary key of the class is the
		first field defined on it). If no such instance is found, then this
		method returns `None`.

		Args:
			search_key (Any): The value of the target instance's primary key.

		Returns:
			Self | None: The instance of the class which has the matching key
			if it exists. Otherwise, returns `None`.
		"""
		key_str = _encode_str(str(search_key))

		with cls._read_csv_file() as r:
			r.readline() # skip the header
			line = r.readline()
			while line != "":
				if line.startswith(key_str):
					return cls._from_csv_row(line)
				line = r.readline()

		return None
	
	@classmethod
	def get_all(cls) -> Generator[Self, None, None]:
		"""
		Yields each stored instance of this class via a generator.

		Yields:
			Self: Instances of this model class in the order that they appear
			in the persisted table.

		Examples:
			To iterate over all instances,

			>>> for instance in ExampleClass.get_all():
				#...
		"""
		with cls._read_csv_file() as r:
			r.readline() # skip the header
			line = r.readline()
			while line != "":
				yield cls._from_csv_row(line)
				line = r.readline()

	@classmethod
	def get_where(cls, **search_fields) -> Generator[Self, None, None]:
		"""
		Yields each stored instance of this class that matches the conditions
		set by `search_fields` via a generator.
		
		Args:
			**search_fields: Here, you can set values for any number of the
			class fields. The yielded records will match each of those values.

		Yields:
			Self: Instances of this model class that have the specified field
			values, in the order that they appear in the persisted table.

		Examples:
			To iterate over all instances that match `field_name = "value"`,

			>>> for instance in ExampleClass.get_where(field_name = "value"):
				#...

			You can add as many conditions as you need:

			>>> for instance in ExampleClass.get_where(\\
				field_1 = "value",\\
				field_2 = 1,\\
				# ...
			):
				# ...
		"""
		search_values: str = [] 
		for field in cls.model_fields.keys():
			if field in search_fields:
				search_values.append(_encode_str(str(search_fields[field])))
			else:
				search_values.append(None)
		
		with cls._read_csv_file() as r:
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
					yield cls._from_csv_row(line)
				line = r.readline()

	@classmethod
	def get_first_where(cls, **search_fields) -> Self | None:
		"""
		Works the same as `get_where`, but only returns the first instance that
		matches the search conditions (or `None` if no records match).

		Args:
			**search_fields: Here, you can set values for any number of the
			class fields. The returned record will match each of those values.

		Returns:
			Self | None: The first instance of the class that matches the 
			search fields, or `None` if no instances match.

		Examples:
			>>> ExampleClass.get_first_where(field_1 = "value", field_2 = 123)
		"""
		search_values: str = [] 
		for field in cls.model_fields.keys():
			if field in search_fields:
				search_values.append(_encode_str(str(search_fields[field])))
			else:
				search_values.append(None)
		
		with cls._read_csv_file() as r:
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
					return cls._from_csv_row(line)
				line = r.readline()

		return None
