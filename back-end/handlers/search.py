from typing import Generator, List
from fastapi import APIRouter, HTTPException, Query

from db.models.Book import Book

search_router = APIRouter(prefix="/search", tags=["search"])

DEFAULT_LIMIT = 50
DEFAULT_PAGE_LIMIT = 20

def _matches(book: Book, author: str | None, year: int | None) -> bool:
	if author is not None:
		if not book.authors or author not in book.authors:
			return False
	if year is not None:
		book_year = getattr(book, "year", None)
		if book_year != year:
			return False
	return True

def _matches_rating(book: Book, rating_min: float | None, rating_max: float | None) -> bool:
	if rating_min is not None:
		if book.average_rating is None or book.average_rating < rating_min:
			return False
	if rating_max is not None:
		if book.average_rating is None or book.average_rating > rating_max:
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
		if not _matches_rating(book, rating_min, rating_max):
			continue

		final_results.append(book)
		if len(final_results) >= limit:
			break

	if not final_results:
		raise HTTPException(status_code=404, detail="No matching books found.")

	return final_results

@search_router.get("/book/{book_title}")
async def search_book_title(
	book_title: str, 
	per_page: int = DEFAULT_LIMIT, 
	page_index: int = 0,
) -> list[Book]:
	"""
	Searches the book records for one whos title roughly matches the 
	`book_title`. For example, using `GET /search/book/frankenstein`
	might return books with the titles "Frankenstein", "Frankenstein;
	or The Modern Prometheus", and so on.

	If no results are found, this endpoint still returns an empty list
	with a status code of 200 (instead of 404).
	"""
	books: list[Book] = []
	
	current_book_idx = 0

	for book in Book.get_where_like(title = book_title):
		current_book_idx += 1
		current_page_idx = current_book_idx // per_page
		if current_page_idx > page_index:
			break
		if current_page_idx < page_index:
			continue
		books.append(book)
		
	return books