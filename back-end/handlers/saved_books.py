from fastapi import APIRouter, HTTPException, Request
from http import HTTPStatus
from pydantic import BaseModel

from db.models.User import User
from db.models.Book import Book
from db.models.SavedBook import SavedBook


class SavedBookAction(BaseModel):
	message: str


saved_book_router = APIRouter(prefix="/saved_book")


def _require_user(req: Request, action: str) -> User:
	user = User.from_session(req)
	if user is None:
		raise HTTPException(
			status_code=HTTPStatus.UNAUTHORIZED,
			detail=f"You must be logged in to {action} books.",
		)
	return user


@saved_book_router.put("/{book_id}", response_model=SavedBookAction)
def save_book(book_id: str, req: Request) -> SavedBookAction:
	user = _require_user(req, "save")

	if not Book.exists(book_id):
		raise HTTPException(status_code=404, detail="Book not found")

	SavedBook.save_for_user(user.id, book_id)
	return SavedBookAction(message="Book saved")


@saved_book_router.delete("/{book_id}", response_model=SavedBookAction)
def unsave_book(book_id: str, req: Request) -> SavedBookAction:
	user = _require_user(req, "unsave")
	SavedBook.remove_for_user(user.id, book_id)
	return SavedBookAction(message="Book removed")


@saved_book_router.get("/", response_model=list[Book])
def get_saved_books(req: Request) -> list[Book]:
	user = _require_user(req, "view saved")

	saved_books: list[Book] = []
	for record in SavedBook.get_where(user_id=user.id):
		book = Book.get_by_primary_key(record.book_id)
		if book is None:
			record.delete()
		else:
			saved_books.append(book)

	return saved_books
