from db.persisted_model import PersistedModel
from pydantic import EmailStr


class User(PersistedModel):
    id: str
    name: str
    email: EmailStr


class UserCredentials(PersistedModel):
    user_id: str
    email: EmailStr
    password: str
