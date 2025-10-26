from fastapi import FastAPI, HTTPException
from db import User

from handlers import user_router

app = FastAPI()

app.include_router(user_router)
