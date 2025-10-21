from util.PersistedModel import PersistedModel
from pydantic import EmailStr, Field

class User[str](PersistedModel):
	id: str
	name: str
	email: EmailStr
	password: str = Field(..., description = "An encrypted user password")


