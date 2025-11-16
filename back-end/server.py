from fastapi import FastAPI

from handlers import user_router

app = FastAPI()

app.include_router(user_router)
