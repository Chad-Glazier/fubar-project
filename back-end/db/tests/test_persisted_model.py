from db.persisted_model import PersistedModel

class RandomModel(PersistedModel):
	pk: int
	field_1: str
	field_2: int

RandomModel.data_dir = "./data/testing-data"

RandomModel._drop_table() # type: ignore

def test_to_csv_header():
	assert RandomModel._to_csv_header() == "pk,field_1,field_2" # type: ignore

def test_to_csv_row():
	model_instance = RandomModel(pk = 1, field_1 = "apple", field_2 = 1)
	assert model_instance._to_csv_row() == "1,apple,1" # type: ignore

def test_supports_commas():
	model_instance = RandomModel(pk = 1, field_1 = "cheese, bacon, mmm", field_2 = 1)
	assert model_instance._to_csv_row() == "1,cheese%2C bacon%2C mmm,1" # type: ignore
	assert model_instance.field_1 == "cheese, bacon, mmm"
	
	model_instance = RandomModel._from_csv_row("1,cheese%2C bacon%2C mmm,1") # type: ignore
	assert model_instance.field_1 == "cheese, bacon, mmm"
	assert model_instance._to_csv_row() == "1,cheese%2C bacon%2C mmm,1" # type: ignore

def test_from_csv_row():
	model_instance: RandomModel = RandomModel._from_csv_row("1,apple,1") # type: ignore
	assert model_instance.pk == 1
	assert model_instance.field_1 == "apple"
	assert model_instance.field_2 == 1

def test_primary_key():
	"""
	The first field in any extension of `PersistedModel` is the primary key
	of that model. As with primary keys in SQL, these must uniquely represent
	each record. 
	"""
	model_instance: RandomModel = RandomModel(
		pk = 1,
		field_1 = "apple",
		field_2 = 12
	)
	assert model_instance._primary_key() == 1 # type: ignore

def test_post():
	instances = [
		RandomModel(pk = 1, field_1 = "orange", field_2 = 1234),
		RandomModel(pk = 2, field_1 = "papaya", field_2 = 1234),
		RandomModel(pk = 3, field_1 = "apple", field_2 = 12345),
		RandomModel(pk = 4, field_1 = "banana", field_2 = 123456),
		RandomModel(pk = 5, field_1 = "peach,nectarine", field_2 = 1234567),
	]
	for instance in instances:
		instance.post()

	with RandomModel._read_csv_file() as r: # type: ignore
		assert r.readline() == RandomModel._to_csv_header() + "\n" # type: ignore
		for instance in instances:
			assert r.readline() == instance._to_csv_row() + "\n" # type: ignore
		assert r.readline() == ""

	# attempt a redundant post
	redundant = RandomModel(pk = 1, field_1 = "apple", field_2 = 12345)
	success = redundant.post()
	assert not success
	assert RandomModel.get_by_primary_key(1).field_1 == "orange" # type: ignore

	RandomModel._drop_table() # type: ignore

def test_patch():
	instances = [
		RandomModel(pk = 1, field_1 = "orange", field_2 = 1234),
		RandomModel(pk = 2, field_1 = "papaya", field_2 = 1234),
		RandomModel(pk = 3, field_1 = "apple", field_2 = 12345),
		RandomModel(pk = 4, field_1 = "banana", field_2 = 123456),
		RandomModel(pk = 5, field_1 = "peach,nectarine", field_2 = 1234567),
	]
	for instance in instances:
		instance.put()

	# attempt to `patch` a nonexistent instance
	success = RandomModel(pk = 6, field_1 = "orange", field_2 = 1234).patch()
	assert not success
	assert RandomModel.get_by_primary_key(6) == None # type: ignore

	instances[0].field_1 = "apple"
	instances[3].field_2 = 12345678

	instances[0].patch()
	instances[3].patch()

	assert RandomModel.get_by_primary_key(1).field_1 == "apple" # type: ignore
	assert RandomModel.get_by_primary_key(4).field_2 == 12345678 # type: ignore

	RandomModel._drop_table() # type: ignore

def test_put():
	"""
	Check that the `put` operations can be used to idempotently create and
	update records in a database table. Whether or not a record already exists
	is judged by the primary key.
	"""
	model_instance_1: RandomModel = RandomModel(
		pk = 1,
		field_1 = "apple",
		field_2 = 12394
	)
	model_instance_1.put()

	model_instance_2: RandomModel = RandomModel(
		pk = 2,
		field_1 = "apple",
		field_2 = 12394
	)
	model_instance_2.put()

	model_instance_1.field_1 = "orange"
	model_instance_1.put()

	with RandomModel._read_csv_file() as r: # type: ignore
		assert r.readline() == RandomModel._to_csv_header() + "\n" # type: ignore
		assert r.readline() == model_instance_1._to_csv_row() + "\n" # type: ignore
		assert r.readline() == model_instance_2._to_csv_row() + "\n" # type: ignore
		assert r.readline() == ""

	RandomModel._drop_table() # type: ignore

def test_delete():
	model_1 = RandomModel(
		pk = 1,
		field_1 = "orange",
		field_2 = 12394
	)
	model_2 = RandomModel(
		pk = 2,
		field_1 = "apple",
		field_2 = 12394
	)

	model_1.put()
	model_2.put()

	assert RandomModel.get_by_primary_key(1) != None # type: ignore
	assert RandomModel.get_by_primary_key(2) != None # type: ignore

	model_1.delete()

	assert RandomModel.get_by_primary_key(1) == None # type: ignore
	assert RandomModel.get_by_primary_key(2) != None # type: ignore

	RandomModel._drop_table() # type: ignore

def test_get_by_primary_key():
	"""
	Test that objects which are persisted in storage can be searched for by
	their primary key.
	"""
	RandomModel(
		pk = 1,
		field_1 = "orange",
		field_2 = 12394
	).put()
	RandomModel(
		pk = 2,
		field_1 = "apple",
		field_2 = 12394
	).put()

	model_1 = RandomModel.get_by_primary_key(1) # type: ignore
	model_2 = RandomModel.get_by_primary_key(2) # type: ignore

	assert model_1.field_1 == "orange" # type: ignore
	assert model_1.field_2 == 12394 # type: ignore
	assert model_1.pk == 1 # type: ignore
	assert model_2.field_1 == "apple" # type: ignore
	assert model_2.field_2 == 12394 # type: ignore
	assert model_2.pk == 2 # type: ignore

	RandomModel._drop_table() # type: ignore

def test_get_first_where():
	instances = [
		RandomModel(pk = 1, field_1 = "orange", field_2 = 1234),
		RandomModel(pk = 2, field_1 = "papaya", field_2 = 1234),
		RandomModel(pk = 3, field_1 = "apple", field_2 = 12345),
		RandomModel(pk = 4, field_1 = "banana", field_2 = 123456),
		RandomModel(pk = 5, field_1 = "peach,nectarine", field_2 = 1234567),
	]
	for instance in instances:
		instance.put()

	found = RandomModel.get_first_where(pk = -1) # type: ignore
	assert found == None

	found = RandomModel.get_first_where(pk = 1) # type: ignore
	assert found != None
	assert found.field_1 == "orange"
	assert found.field_2 == 1234

	found = RandomModel.get_first_where(field_2 = 1234) # type: ignore
	assert found != None
	assert found.pk == 1
	assert found.field_1 == "orange"

	found = RandomModel.get_first_where(pk = 1, field_1 = "peach,nectarine") # type: ignore
	assert found == None

	found = RandomModel.get_first_where(field_1 = "peach,nectarine", field_2 = 1234567) # type: ignore
	assert found != None
	assert found.pk == 5

	RandomModel._drop_table() # type: ignore

def test_get_where():
	instances = [
		RandomModel(pk = 1, field_1 = "orange", field_2 = 1234),
		RandomModel(pk = 2, field_1 = "papaya", field_2 = 1234),
		RandomModel(pk = 3, field_1 = "apple", field_2 = 12345),
		RandomModel(pk = 4, field_1 = "banana", field_2 = 123456),
		RandomModel(pk = 5, field_1 = "peach,nectarine", field_2 = 1234567),
	]
	for instance in instances:
		instance.put()

	retrieved_instances = [instance for instance in RandomModel.get_where()] # type: ignore

	for (i, instance) in enumerate(retrieved_instances):
		assert instance.pk == i + 1

	retrieved_instances = [instance for instance in \
						RandomModel.get_where(field_2 = 1234)] # type: ignore

	assert len(retrieved_instances) == 2
	assert retrieved_instances[0].field_1 == "orange"
	assert retrieved_instances[1].field_1 == "papaya"

	retrieved_instances = [instance for instance in \
						RandomModel.get_where(field_1 = "orange", field_2 = 123456)] # type: ignore

	assert len(retrieved_instances) == 0

	RandomModel._drop_table() # type: ignore

def test_get_all():
	instances = [
		RandomModel(pk = 1, field_1 = "orange", field_2 = 1234),
		RandomModel(pk = 2, field_1 = "papaya", field_2 = 1234),
		RandomModel(pk = 3, field_1 = "apple", field_2 = 12345),
		RandomModel(pk = 4, field_1 = "banana", field_2 = 123456),
		RandomModel(pk = 5, field_1 = "peach,nectarine", field_2 = 1234567),
	]
	for instance in instances:
		instance.put()

	retrieved_instances = [instance for instance in RandomModel.get_all()]

	for (i, instance) in enumerate(retrieved_instances):
		assert instance.pk == i + 1

	RandomModel._drop_table() # type: ignore