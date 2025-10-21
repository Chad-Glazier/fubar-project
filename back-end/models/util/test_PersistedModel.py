from PersistedModel import PersistedModel

class RandomModel(PersistedModel):
	pk: int
	field_1: str
	field_2: int


def test_to_csv_header():
	assert RandomModel.to_csv_header() == "pk,field_1,field_2"

def test_to_csv_row():
	model_instance = RandomModel(pk = 1, field_1 = "apple", field_2 = 1)
	assert model_instance.to_csv_row() == "1,apple,1"

def test_supports_commas():
	model_instance = RandomModel(pk = 1, field_1 = "cheese, bacon, mmm", field_2 = 1)
	assert model_instance.to_csv_row() == "1,cheese%2C bacon%2C mmm,1"
	assert model_instance.field_1 == "cheese, bacon, mmm"
	
	model_instance = RandomModel.from_csv_row("1,cheese%2C bacon%2C mmm,1")
	assert model_instance.field_1 == "cheese, bacon, mmm"
	assert model_instance.to_csv_row() == "1,cheese%2C bacon%2C mmm,1"

def test_from_csv_row():
	model_instance: RandomModel = RandomModel.from_csv_row("1,apple,1")
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
	print(model_instance.primary_key())
	assert model_instance.primary_key() == 1

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

	with RandomModel.read_csv_file() as r:
		assert r.readline() == RandomModel.to_csv_header() + "\n"
		assert r.readline() == model_instance_1.to_csv_row() + "\n"
		assert r.readline() == model_instance_2.to_csv_row() + "\n"
		assert r.readline() == ""

	RandomModel.drop_table()

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

	model_1 = RandomModel.get_by_primary_key(1)
	model_2 = RandomModel.get_by_primary_key(2)

	assert model_1.field_1 == "orange"
	assert model_1.field_2 == 12394
	assert model_1.pk == 1
	assert model_2.field_1 == "apple"
	assert model_2.field_2 == 12394
	assert model_2.pk == 2

	RandomModel.drop_table()

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

	assert RandomModel.get_by_primary_key(1) != None
	assert RandomModel.get_by_primary_key(2) != None

	model_1.delete()

	assert RandomModel.get_by_primary_key(1) == None
	assert RandomModel.get_by_primary_key(2) != None

	RandomModel.drop_table()
