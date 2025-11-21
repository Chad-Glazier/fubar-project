from fastapi import FastAPI

from handlers.user import user_router
from handlers.recommendations import recommend_router
from handlers.book_details import book_router
from handlers.search import search_router
from handlers.saved_books import saved_book_router
from handlers.review import review_router

app = FastAPI()

app.include_router(user_router)
app.include_router(saved_book_router)
app.include_router(search_router)
app.include_router(recommend_router)
app.include_router(book_router)
app.include_router(review_router)
