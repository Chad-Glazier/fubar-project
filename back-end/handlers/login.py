from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
import bcrypt

from db.models.User import User

login_router = APIRouter(prefix="/auth", tags=["auth"])

class LoginBody(BaseModel):
    email: str
    password: str

@login_router.post("/login")
async def login_user(body: LoginBody, response: Response):
    user = User.find_one({"email": body.email})
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials.")

    if not bcrypt.checkpw(body.password.encode(), user.password.encode()):
        raise HTTPException(status_code=401, detail="Invalid credentials.")

    session_token = User.generate_pk()
    User.save_session(user.id, session_token)

    response.set_cookie(
        key="session",
        value=session_token,
        httponly=True,
        max_age=60 * 60 * 24 * 30,
    )

    user_dict = user.to_dict()
    user_dict.pop("password", None)

    return {"message": "Logged in", "user": user_dict}
