from db.persisted_model import PersistedModel
from db.models.BookMetadataCache import BookMetadataCache
from typing import Dict, Optional
import httpx
import uuid
import os
from dotenv import load_dotenv

# Load local .env if present (safe no-op if not)
load_dotenv()

class Book(PersistedModel):
    id: str
    title: str
    authors: list[str]
    categories: list[str] | None = None
    description: str | None = None
    imageLinks: Dict[str, str] | None = None  # e.g. {"thumbnail": "http://..."}
    average_rating: float | None = None

    @classmethod
    def fetch_from_google_books(cls, query: str, max_results: int = 1) -> Optional["Book"]:
        """Fetches metadata from the Google Books API and returns a Book instance

        This will return the first matching volume's metadata as a Book instance
        or `None` when no results or on error.
        """
        if not query:
            return None

        # If the query itself is already a stored book id, return it immediately.
        existing_book = cls.get_by_primary_key(query)
        if existing_book is not None:
            return existing_book

        cache_entry = BookMetadataCache.get_by_primary_key(query)
        if cache_entry is not None:
            cached_book = cls.get_by_primary_key(cache_entry.book_id)
            if cached_book is not None:
                return cached_book
            # If cache is stale, remove entry and continue to fetch fresh data.
            cache_entry.delete()

        params = {"q": query, "maxResults": max_results}
        # prefer explicit API key from environment
        key = os.getenv("GOOGLE_BOOKS_API_KEY")
        if key:
            params["key"] = key

        try:
            resp = httpx.get("https://www.googleapis.com/books/v1/volumes", params=params, timeout=5.0)
            resp.raise_for_status()
            payload = resp.json()
            items = payload.get("items") or []
            if not items:
                return None

            volume = items[0]
            info = volume.get("volumeInfo", {})

            fields: dict = {}
            fields["id"] = volume.get("id") or str(uuid.uuid4())
            fields["title"] = info.get("title")
            fields["authors"] = info.get("authors") or []
            fields["categories"] = info.get("categories")
            fields["description"] = info.get("description")
            fields["imageLinks"] = info.get("imageLinks")
            avg = info.get("averageRating")
            fields["average_rating"] = float(avg) if avg is not None else None

            # publishedDate could be YYYY or YYYY-MM-DD
            pub = info.get("publishedDate")
            if pub:
                try:
                    fields["year"] = int(str(pub).split("-")[0])
                except Exception:
                    pass

            # validate/create model instance
            if hasattr(cls, "model_validate"):
                book = cls.model_validate(fields)
            else:
                book = cls(**fields)

            # persist and cache the book for future lookups
            book.put()
            BookMetadataCache(query = query, book_id = book.id).put()

            return book

        except Exception:
            return None
