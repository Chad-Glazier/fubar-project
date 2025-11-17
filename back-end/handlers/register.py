from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import bcrypt

from db import User

register_router = APIRouter(prefix="/auth", tags=["auth"])

class RegisterBody(BaseModel):
    name: str
    email: str
    password: str

@register_router.post("/register")
async def register_user(body: RegisterBody):
    existing_user = User.find_one({"email": body.email})
    if existing_user:
        raise HTTPException(status_code=404, detail="Email already registered.")

    hashed_pw = bcrypt.hashpw(body.password.encode(), bcrypt.gensalt()).decode()

    new_user = User(
        id=User.generate_pk(),
        name=body.name,
        email=body.email,
        password=hashed_pw,
    )

    new_user.save()

    user_dict = new_user.to_dict()
    user_dict.pop("password", None)

    return {"message": "User registered", "user": user_dict}
