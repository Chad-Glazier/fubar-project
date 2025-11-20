from fastapi import FastAPI

from handlers import user_router, search_router

app = FastAPI()

app.include_router(search_router)
app.include_router(user_router)
