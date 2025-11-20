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
    
    