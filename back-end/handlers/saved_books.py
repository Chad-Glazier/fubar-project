from fastapi import APIRouter, HTTPException, Request
from http import HTTPStatus

from db.models.User import User
from db.models.Book import Book
from db.models.SavedBook import SavedBook

saved_book_router = APIRouter(prefix = "/saved_book")

def _require_user(req: Request, action: str) -> User:
	user = User.from_session(req)
	if user == None:
		raise HTTPException(
			status_code = HTTPStatus.UNAUTHORIZED,
			detail = f"You must be logged in to {action} books."
		)
	return user

@saved_book_router.put("/{book_id}")
def save_book(book_id: str, req: Request):
	user = _require_user(req, "save")

	# Validate book
	if not Book.exists(book_id):
		raise HTTPException(status_code=404, detail="Book not found")

	# Save the book (idempotently)
	SavedBook.save_for_user(user.id, book_id)

@saved_book_router.delete("/{book_id}")
def unsave_book(book_id: str, req: Request):
	user = _require_user(req, "unsave")
	
	SavedBook.remove_for_user(user.id, book_id)

@saved_book_router.get("/")
def get_saved_books(req: Request) -> list[Book]:
	user = _require_user(req, "view saved")

	saved_books: list[Book] = []
	for record in SavedBook.get_where(user_id = user.id):
		book = Book.get_by_primary_key(record.book_id)
		if book == None:
			record.delete()
		else:
			saved_books.append(book)

	return saved_books
