from fastapi import FastAPI, HTTPException
from db import User

from handlers import user_router, register_router,login_router

app = FastAPI()

app.include_router(user_router)
app.include_router(register_router)
app.include_router(login_router)