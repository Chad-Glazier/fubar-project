from fastapi import APIRouter, HTTPException

from db.models.User import User
from db.models.Book import Book
from db.models.SavedBook import SavedBook

router = APIRouter()

@router.post("/users/{user_id}/saved/{book_id}")
def save_book(user_id: str, book_id: str):
    # Validate user
    if not User.exists(user_id):
        raise HTTPException(status_code=404, detail="User not found")

    # Validate book
    if not Book.exists(book_id):
        raise HTTPException(status_code=404, detail="Book not found")

    # Save entry
    SavedBook.save_for_user(user_id, book_id)
    return {"message": "Book saved"}


@router.delete("/users/{user_id}/saved/{book_id}")
def unsave_book(user_id: str, book_id: str):
    SavedBook.remove_for_user(user_id, book_id)
    return {"message": "Book removed"}

@router.get("/users/{user_id}/saved")
def get_saved_books(user_id: str):
    if not User.exists(user_id):
        raise HTTPException(status_code=404, detail="User not found")

    saved_books = SavedBook.get_saved_for_user(user_id)
    return saved_books
