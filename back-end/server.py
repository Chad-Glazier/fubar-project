from fastapi import FastAPI, HTTPException
from db.models import User

from handlers import user_router, search_router, recommend_router, book_router


app = FastAPI()

app.include_router(user_router)
app.include_router(search_router)
app.include_router(recommend_router)
app.include_router(book_router)
