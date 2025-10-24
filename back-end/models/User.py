from models import PersistedModel
from pydantic import EmailStr, Field

class User(PersistedModel):
	id: str
	name: str
	email: EmailStr
	password: str = Field(..., description = "An encrypted user password")
