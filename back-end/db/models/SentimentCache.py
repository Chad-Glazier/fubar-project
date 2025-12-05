from time import time
from typing import Self
from pydantic import Field

from db.persisted_model import PersistedModel


class SentimentCache(PersistedModel):
	book_id: str
	sentiment: str
	score: float
	scores: dict[str, float]
	review_count: int
	cached_at: int = Field(default_factory = lambda: int(time()))

	@classmethod
	def get_cached(cls, book_id: str) -> "SentimentCache | None":
		return cls.get_by_primary_key(book_id)

	@classmethod
	def upsert(
		cls,
		book_id: str,
		sentiment: str,
		score: float,
		scores: dict[str, float],
		review_count: int
	) -> Self:
		entry = cls(
			book_id = book_id,
			sentiment = sentiment,
			score = score,
			scores = scores,
			review_count = review_count
		)
		entry.put()
		return entry
