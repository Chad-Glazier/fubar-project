from typing import List
from fastapi import APIRouter, HTTPException, Query
from db.camelized_model import CamelizedModel

from db.recommend import recommend_for_user
from db.models.Book import Book

class RecommendationItem(CamelizedModel):
	book: Book | None = None
	book_id: str | None = None
	score: float

recommend_router = APIRouter(prefix="/recommendations", tags=["recommendations"])

@recommend_router.get("/{user_id}", response_model=List[RecommendationItem])
async def get_recommendations(user_id: str, n: int = Query(default = 10), k: int = Query(5)) -> List[RecommendationItem]:
	recs = recommend_for_user(user_id, k_neighbors=k, n_recs=n)
	if not recs:
		raise HTTPException(status_code=404, detail="No recommendations available")

	results: List[RecommendationItem] = []
	for book_id, score in recs:
		book = Book.get_by_primary_key(book_id)
		if book:
			results.append(RecommendationItem(book=book, score=score))
			continue

		try:
			enriched = Book.fetch_from_google_books(book_id)
			if enriched:
				try:
					enriched.put()
				except Exception:
					pass
				results.append(RecommendationItem(book=enriched, score=score))
				continue
		except Exception:
			pass

		results.append(RecommendationItem(book_id=book_id, score=score))

	return results
