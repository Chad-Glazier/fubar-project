from db._persisted_model import _PersistedModel
from pydantic import EmailStr, Field

class User(_PersistedModel):
	id: str
	name: str
	email: EmailStr
	password: str = Field(..., description = "An encrypted user password")
