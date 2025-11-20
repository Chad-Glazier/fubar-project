from fastapi import APIRouter, HTTPException, Query
search_router = APIRouter(prefix="/search", tags=["search"])

@search_router.get("/")
async def search_books(
    author: str | None = None,
    year: int | None = None,
    rating_min: float | None = None,
    rating_max: float | None = None
):
    # Load all stored books from CSV/JSON via PersistedModel
    all_books = Book.get_all()

    if not all_books:
        raise HTTPException(status_code=404, detail="No books found")
    
     # Filter step-by-step
    results = all_books

    if author:
        results = [book for book in results if author.lower() in book.author.lower()]
    
    if year:
        results = [book for book in results if book.year == year]

    if rating_min:
        results = [book for book in results if book.average_rating >= rating_min]

    if rating_max:
        results = [book for book in results if book.average_rating <= rating_max]

    if len(results) == 0:
        raise HTTPException(status_code=404, detail="No matching books found")

    return results