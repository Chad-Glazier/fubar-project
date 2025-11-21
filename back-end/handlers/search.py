from typing import List
from fastapi import APIRouter, HTTPException, Query

from db.models.Book import Book

search_router = APIRouter(prefix="/search", tags=["search"])


@search_router.get("/", response_model=List[Book])
async def search_books(
    author: str | None = Query(None),
    year: int | None = Query(None),
    rating_min: float | None = Query(None),
    rating_max: float | None = Query(None),
):
    # Load all stored books from persistence
    all_books = Book.get_all()

    if not all_books:
        raise HTTPException(status_code=404, detail="No books found")

    results = all_books

    if author:
        results = [book for book in results if any(author.lower() in a.lower() for a in (book.authors or []))]

    if year is not None:
        results = [book for book in results if getattr(book, "year", None) == year]

    if rating_min is not None:
        results = [book for book in results if (book.average_rating or 0) >= rating_min]

    if rating_max is not None:
        results = [book for book in results if (book.average_rating or 0) <= rating_max]

    if len(results) == 0:
        raise HTTPException(status_code=404, detail="No matching books found")

    return results
