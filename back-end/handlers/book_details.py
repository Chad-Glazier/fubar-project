from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List

from db.models.Book import Book
from db.models.UserReview import UserReview

book_router = APIRouter(prefix="/books", tags=["books"])

class BookDetails(BaseModel):
    book: Book
    average_rating: float
    review_count: int
    reviews: list[UserReview]

@book_router.get("/", response_model=List[Book])
async def list_books(limit: int = Query(50, ge=1)) -> List[Book]:
    """Allow guests to browse available books."""
    books: List[Book] = []
    for book in Book.get_all():
        books.append(book)
        if len(books) >= limit:
            break

    if not books:
        raise HTTPException(status_code=404, detail="No books available")
    return books

@book_router.get("/{book_id}")
async def get_book_details(book_id: str) -> BookDetails:
    """Return book metadata, description, average rating, and reviews."""
    book = Book.get_by_primary_key(book_id)
    if book is None:
        book = Book.fetch_from_google_books(book_id)
        if book is None:
            raise HTTPException(status_code=404, detail="Book not found")

    # Collect reviews for this book
    reviews = list(UserReview.get_where(book_id=book_id))

    # Compute average rating if reviews exist
    avg = 0
    if reviews:
        avg = sum(float(r.rating) for r in reviews) / len(reviews)

    return BookDetails(
        book = book,
        average_rating = avg,
        review_count = len(reviews),
        reviews = reviews,
    )
