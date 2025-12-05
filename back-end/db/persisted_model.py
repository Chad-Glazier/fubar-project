from io import TextIOWrapper
import json
import os
from pathlib import Path
from threading import Lock
from typing import Any, ClassVar, Generator, Self, Union, get_args, get_origin
from types import UnionType
import uuid
from db.camelized_model import CamelizedModel
import ast

from db.loose_compare import loose_compare
from db.encode_str import encode_str, decode_str

class PersistedModel(CamelizedModel):
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

	def _primary_key(self) -> Any: # type: ignore
		primary_key_field: str = next(iter(self.__class__.model_fields.keys()))
		return getattr(self, primary_key_field)

	@classmethod
	def generate_primary_key(cls) -> str:
		"""
		Generates a unique primary key for this model.
		"""
		new_key = uuid.uuid4().hex
		while cls.exists(new_key):
			new_key = uuid.uuid4().hex
		return new_key

	def _to_csv_row(self) -> str:
		row_values: list[str] = []
		for field_name, value in self.model_dump().items():
			field_info = self.__class__.model_fields[field_name]
			annotation = field_info.annotation
			origin = get_origin(annotation)

			if origin in (list, dict, tuple, set):
				serialized_value = json.dumps(value)
			else:
				serialized_value = str(value)

			row_values.append(encode_str(serialized_value))
		return ",".join(row_values)
	
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
		updated_file = open(
			f"{self.__class__.data_dir}/tmp_{self.__class__.__name__}_{uuid.uuid4().hex}",
			"w"
		)

		prev_record_found = False

		primary_key = encode_str(str(self._primary_key())) # type: ignore

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
		updated_file = open(
			f"{self.__class__.data_dir}/tmp_{self.__class__.__name__}_{uuid.uuid4().hex}",
			"w"
		)
		prev_record_found = False

		primary_key = encode_str(str(self._primary_key())) # type: ignore

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
		
	@classmethod
	def create(cls, **fields: Any) -> Self:
		"""
		Convenience helper that constructs an instance with the provided fields,
		persists it immediately, and then returns the instance.
		"""
		instance = cls(**fields)
		instance.put()
		return instance
	
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
		updated_file = open(
			f"{self.__class__.data_dir}/tmp_{self.__class__.__name__}_{uuid.uuid4().hex}",
			"w"
		)
		prev_record_found = False

		primary_key = encode_str(str(self._primary_key())) # type: ignore

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
		updated_file = open(
			f"{self.__class__.data_dir}/tmp_{self.__class__.__name__}_{uuid.uuid4().hex}",
			"w"
		)

		primary_key = encode_str(str(self._primary_key())) # type: ignore

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
			return file_path.open("r", encoding = "latin-1")

		file_path.parent.mkdir(
			parents = True, 
			exist_ok = True,
		)
		with file_path.open("a+", encoding = "latin-1") as w:
			w.write(cls._to_csv_header() + "\n")
		
		return file_path.open("r", encoding = "latin-1")
	
	@classmethod
	def _append_csv_file(cls) -> TextIOWrapper:
		"""
		Open a file writer to append to the raw CSV file.
		"""
		file_path = Path(cls.data_dir + "/" + cls.__name__ + ".csv")
		if file_path.exists():
			return file_path.open("a", encoding = "latin-1")

		file_path.parent.mkdir(
			parents = True, 
			exist_ok = True,
		)
		with file_path.open("a+", encoding = "latin-1") as w:
			w.write(cls._to_csv_header() + "\n")
		
		return file_path.open("a", encoding = "latin-1")


	@classmethod
	def _from_csv_row(cls, csv_row: str) -> Self:
		if csv_row.endswith("\n"):
			csv_row = csv_row[:-1]
		fields = {}
		values = csv_row.split(",")
		keys = cls.model_fields.keys()
		for key, value in zip(keys, values):
			field_info = cls.model_fields[key]
			annotation = field_info.annotation
			origin = get_origin(annotation)
			decoded_value = decode_str(value)

			args = get_args(annotation)
			allows_none = any(arg is type(None) for arg in args)

			# unwrap Optional/Union types that include None
			if origin in (UnionType, Union):
				non_none_args = [arg for arg in args if arg is not type(None)]
				if len(non_none_args) == 1:
					annotation = non_none_args[0]
					origin = get_origin(annotation)
				else:
					origin = None

			if decoded_value == "None" and allows_none:
				fields[key] = None
				continue

			if origin in (list, dict, tuple, set):
				try:
					json_value = json.loads(decoded_value)
				except json.JSONDecodeError:
					json_value = decoded_value

				if origin is tuple:
					fields[key] = tuple(json_value) if isinstance(json_value, list) else json_value # pyright: ignore[reportUnknownArgumentType]
				elif origin is set:
					fields[key] = set(json_value) if isinstance(json_value, list) else json_value # pyright: ignore[reportUnknownArgumentType]
				else:
					fields[key] = json_value
			else:
				fields[key] = decoded_value
		# strip trailing newline then split
		values = csv_row.removesuffix("\n").split(",")
		keys = cls.model_fields.keys()
		for key, value in zip(keys, values):
			# decode any encoded commas/newlines
			decoded = decode_str(value)
			ann = cls.model_fields[key].annotation
			# strings should remain decoded strings
			if ann is str:
				fields[key] = decoded
			else:
				# handle explicit None
				if decoded == "None" or decoded == "":
					fields[key] = None
				else:
					# try literal eval for lists/dicts/numbers
					try:
						val = ast.literal_eval(decoded)
					except Exception:
						# fallback: try numeric conversion
						try:
							val = float(decoded)
							# if it's an int-valued float, cast to int when annotation expects int
							if ann is int:
								val = int(val)
						except Exception:
							val = decoded
					fields[key] = val
		return cls.model_validate(fields)
	
	@classmethod
	def _drop_table(cls) -> None:
		cls._mutex.acquire()
		file_path = Path(cls.data_dir + "/" + cls.__name__ + ".csv")
		file_path.unlink(missing_ok = True)
		cls._mutex.release()

	@classmethod
	def get_by_primary_key(cls, search_key: Any) -> Self | None:
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
		key_str = encode_str(str(search_key)) # type: ignore

		with cls._read_csv_file() as r:
			r.readline() # skip the header
			line = r.readline()
			while line != "":
				if line.startswith(key_str):
					return cls._from_csv_row(line)
				line = r.readline()

		return None
	
	@classmethod
	def exists(cls, search_key: Any) -> bool:
		"""
		Returns True if a record with the provided primary key exists.
		"""
		return cls.get_by_primary_key(search_key) is not None
	
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
	def get_where_like(cls, **search_fields: Any) -> Generator[Self, None, None]: # type: ignore
		"""
		Yields each stored instance of this class where the conditions roughly
		match those set in `search_fields`. If you want a literal search, then
		use `get_where` instead.

		The "loose" comparison treats the fields as strings. It's recommended
		that you only do this kind of loose search on fields that truly are
		strings, but it's not required.

		Args:
			**search_fields: Here, you can set values for any number of the 
			class fields. The values will be loosely checked against each
			record's values.

		Yields:
			Self: Instances of this model class that have fields which loosely
			match the specified values, in the order that they appear in the
			persisted table.

		Examples:
			Suppose you had `Book` as a table. You could do the following:

			>>> for book in Book.get_where_like(title = "frankenstein"):
					# You might get books where the title is "Frankenstein",
					# or "Frankenstein; or, The Modern Prometheus"`
		"""
		search_values: list[str | None] = [] 
		for field in cls.model_fields.keys():
			if field in search_fields:
				search_values.append(encode_str(str(search_fields[field]))) # type: ignore
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
					if not loose_compare(values[i], search_values[i]): # type: ignore
						match_found = False
						break
				if match_found:
					yield cls._from_csv_row(line)
				line = r.readline()

	@classmethod
	def get_where(cls, **search_fields: Any) -> Generator[Self, None, None]: # type: ignore
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
		search_values: list[str | None] = [] 
		for field in cls.model_fields.keys():
			if field in search_fields:
				search_values.append(encode_str(str(search_fields[field]))) # type: ignore
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
	def get_first_where(cls, **search_fields: Any) -> Self | None: # type: ignore
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
		search_values: list[str | None] = [] 
		for field in cls.model_fields.keys():
			if field in search_fields:
				search_values.append(encode_str(str(search_fields[field]))) # type: ignore
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
