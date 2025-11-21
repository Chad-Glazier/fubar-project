from typing import Generator, List
from fastapi import APIRouter, HTTPException, Query

from db.models.Book import Book

search_router = APIRouter(prefix="/search", tags=["search"])

DEFAULT_LIMIT = 50

@search_router.get("/", response_model=List[Book])
async def search_books(
	author: str | None = Query(None),
	year: int | None = Query(None),
	rating_min: float | None = Query(None),
	rating_max: float | None = Query(None),
	limit: int = Query(DEFAULT_LIMIT)
):
	results: Generator[Book, None, None] = Book.get_all()
	if author and year:
		results = Book.get_where(
			author = author,
			year = year
		)
	elif author:
		results	= Book.get_where(
			author = author
		)
	elif year:
		results = Book.get_where(
			year = year
		)

	final_results: List[Book] = []
	result_count = 0

	if rating_min and rating_max:
		for book in results:
			if book.average_rating is None:
				continue
			if book.average_rating >= rating_min and book.average_rating <= rating_max:
				final_results.append(book)
				result_count += 1
				if result_count >= limit:
					break
	elif rating_min:
		for book in results:
			if book.average_rating is None:
				continue
			if book.average_rating >= rating_min:
				final_results.append(book)
				result_count += 1
				if result_count >= limit:
					break
	elif rating_max:
		for book in results:
			if book.average_rating is None:
				continue
			if book.average_rating <= rating_max:
				final_results.append(book)
				result_count += 1
				if result_count >= limit:
					break
	else:
		for book in results:
			final_results.append(book)
			result_count += 1
			if result_count >= limit:
				break

	if len(final_results) == 0:
		raise HTTPException(status_code = 404, detail = "No matching books found.")

	return results
