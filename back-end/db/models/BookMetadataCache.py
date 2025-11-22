from time import time
from pydantic import Field

from db.persisted_model import PersistedModel


class BookMetadataCache(PersistedModel):
	query: str
	book_id: str
	cached_at: int = Field(default_factory=lambda: int(time()))

	@classmethod
	def get_cached_book_id(cls, query: str) -> str | None:
		entry = cls.get_by_primary_key(query)
		if entry is None:
			return None
		return entry.book_id

	@classmethod
	def upsert(cls, query: str, book_id: str) -> None:
		cls(query = query, book_id = book_id).put()
