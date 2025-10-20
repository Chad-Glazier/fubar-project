from BaseModelWithCSV import BaseModelWithCSV

class RandomModel(BaseModelWithCSV):
	field_1: str
	field_2: int

random_instance = RandomModel(field_1 = "apple", field_2 = 1)

def test_to_csv_header():
	assert RandomModel.to_csv_header() == "field_1,field_2"

def test_to_csv_row():
	assert random_instance.to_csv_row() == "apple,1"

def test_from_csv_row():
	model_instance: RandomModel = RandomModel.from_csv_row("apple,1")
	assert model_instance.field_1 == "apple"
	assert model_instance.field_2 == 1
