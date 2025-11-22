from typing import Generator, List
from fastapi import APIRouter, HTTPException, Query

from db.models.Book import Book

search_router = APIRouter(prefix="/search", tags=["search"])

DEFAULT_LIMIT = 50


def _matches(book: Book, author: str | None, year: int | None) -> bool:
    if author is not None:
        if not book.authors or author not in book.authors:
            return False
    if year is not None:
        book_year = getattr(book, "year", None)
        if book_year != year:
            return False
    return True


@search_router.get("/", response_model=List[Book])
async def search_books(
    author: str | None = Query(None),
    year: int | None = Query(None),
    rating_min: float | None = Query(None),
    rating_max: float | None = Query(None),
    limit: int = Query(DEFAULT_LIMIT),
):
    results: Generator[Book, None, None] = Book.get_all()

    final_results: List[Book] = []
    for book in results:
        if not _matches(book, author, year):
            continue
        if rating_min is not None and (book.average_rating is None or book.average_rating < rating_min):
            continue
        if rating_max is not None and (book.average_rating is None or book.average_rating > rating_max):
            continue

        final_results.append(book)
        if len(final_results) >= limit:
            break

    if not final_results:
        raise HTTPException(status_code=404, detail="No matching books found.")

    return final_results
