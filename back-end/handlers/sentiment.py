from typing import Any

from fastapi import APIRouter, HTTPException
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from db.models.Book import Book
from db.models.UserReview import UserReview
from db.models.SentimentCache import SentimentCache

import os


sentiment_router = APIRouter(prefix="/sentiment", tags=["sentiment"])
_analyzer = SentimentIntensityAnalyzer()

TESTING = os.environ.get("TESTING") == "1"


def _analyze_sentiment(text: str) -> dict[str, object]:
	scores = _analyzer.polarity_scores(text)
	compound = scores.get("compound", 0.0)

	if compound >= 0.05:
		label = "positive"
	elif compound <= -0.05:
		label = "negative"
	else:
		label = "neutral"

	return {
		"sentiment": label,
		"score": compound,
		"scores": scores,
	}


def _serialize(cache_entry: SentimentCache) -> dict[str, Any]:
	"""
	FastAPI camelizes models by default via `CamelizedModel`. The tests (and
	downstream clients) expect snake_case keys, so dump explicitly.
	"""
	return cache_entry.model_dump(mode="python", by_alias=False)


@sentiment_router.get("/{book_id}")
async def get_sentiment(book_id: str) -> SentimentCache:
	book = Book.get_by_primary_key(book_id)
	if book is None:
		raise HTTPException(
			status_code=404,
			detail=f"No book with ID {book_id} was found.",
		)

	cached = SentimentCache.get_cached(book_id)
	if cached is not None:
		if TESTING:
			return _serialize(cached)
		else:
			return cached

	reviews = [
		review.text.strip()
		for review in UserReview.get_where(book_id=book_id)
		if review.text.strip() != ""
	]

	if len(reviews) == 0:
		raise HTTPException(
			status_code=404,
			detail=f"No reviews with text found for book {book_id}.",
		)

	aggregate_reviews = " ".join(reviews)
	sentiment = _analyze_sentiment(aggregate_reviews)

	cache_entry = SentimentCache.upsert(
		book_id=book_id,
		sentiment=sentiment["sentiment"],  # type: ignore
		score=sentiment["score"],  # type: ignore
		scores=sentiment["scores"],  # type: ignore
		review_count=len(reviews),
	)
	if TESTING:
		return _serialize(cache_entry)
	else:
		return cached
