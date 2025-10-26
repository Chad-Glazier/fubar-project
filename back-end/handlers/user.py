from fastapi import APIRouter
from pydantic import BaseModel

from db import User

user_router = APIRouter(prefix = "/user", tags = ["users"])

@user_router.get("/")
async def _get_user_root():
	pass
