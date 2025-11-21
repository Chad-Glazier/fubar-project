from fastapi import FastAPI


from handlers import saved_books,user_router
from handlers import user_router, search_router, recommend_router, book_router


app = FastAPI()

app.include_router(user_router)
app.include_router(saved_books.router)
app.include_router(search_router)
app.include_router(recommend_router)
app.include_router(book_router)
