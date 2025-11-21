from fastapi import FastAPI


from handlers import saved_books,user_router

app = FastAPI()

app.include_router(user_router)
app.include_router(saved_books.router)
