from fastapi import FastAPI

from handlers import user_router, search_router, recommend_router, book_router


app = FastAPI()

app.include_router(user_router)
app.include_router(search_router)
app.include_router(recommend_router)
app.include_router(book_router)
