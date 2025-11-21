from typing import Dict, Any
from fastapi import APIRouter, HTTPException

from db.models.Book import Book
from db.models.UserReview import UserReview

book_router = APIRouter(prefix="/books", tags=["books"])


@book_router.get("/{book_id}")
async def get_book_details(book_id: str) -> Dict[str, Any]:
    """Return book metadata, description, average rating, and reviews."""
    book = Book.get_by_primary_key(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    # Collect reviews for this book
    reviews = list(UserReview.get_where(book_id=book_id))
    review_list = [r.model_dump() for r in reviews]

    # Compute average rating if reviews exist
    avg = None
    if reviews:
        avg = sum(float(r.rating) for r in reviews) / len(reviews)

    result = {
        "book": book.model_dump(),
        "average_rating": avg,
        "review_count": len(reviews),
        "reviews": review_list,
    }

    return result
