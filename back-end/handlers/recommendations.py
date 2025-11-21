from typing import List
from fastapi import APIRouter, HTTPException, Query

from db.recommend import recommend_for_user
from db.models.Book import Book

recommend_router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@recommend_router.get("/{user_id}")
async def get_recommendations(user_id: str, n: int = Query(10), k: int = Query(5)) -> List:
    recs = recommend_for_user(user_id, k_neighbors=k, n_recs=n)
    if not recs:
        raise HTTPException(status_code=404, detail="No recommendations available")

    out = []
    for book_id, score in recs:
        book = Book.get_by_primary_key(book_id)
        if book:
            out.append({"book": book, "score": score})
        else:
            # Attempt to enrich from Google Books API using the book_id as a query
            try:
                enriched = Book.fetch_from_google_books(book_id)
                if enriched:
                    # persist the enriched book so future requests are local
                    try:
                        enriched.post()
                    except Exception:
                        # if persisting fails, continue without blocking the response
                        pass
                    out.append({"book": enriched, "score": score})
                    continue
            except Exception:
                # ignore enrichment errors and fall back to returning id
                pass

            out.append({"book_id": book_id, "score": score})

    return out
