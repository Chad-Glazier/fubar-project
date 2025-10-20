from util.BaseModelWithCSV import BaseModelWithCSV
from pydantic import EmailStr, Field
import tempfile
import os

class User(BaseModelWithCSV):
	id: str
	name: str
	email: EmailStr
	password: str = Field(..., description = "An encrypted user password")

	def save(self):
		original_file = User.read_csv_file()
		updated_file = tempfile.TemporaryFile("w", delete = False, dir = "./data")
		prev_record_found = False

		for line in original_file.readlines():
			if line.startswith(self.id):
				prev_record_found = True
				updated_file.write(self.to_csv_row() + "\n")
			else:
				updated_file.write(line)

		if not prev_record_found:
			updated_file.write(self.to_csv_row() + "\n")

		original_file.close()
		updated_file.close()

		os.replace(updated_file.name, original_file.name)
