from collections import OrderedDict
from threading import RLock
from typing import ClassVar, Dict, Optional
import httpx
import uuid
import os
from dotenv import load_dotenv

from db.persisted_model import PersistedModel
from db.models.BookMetadataCache import BookMetadataCache


def _cache_limit_from_env() -> int:
    raw = os.getenv("BOOK_CACHE_MAX_ENTRIES")
    if not raw:
        return 2048
    try:
        value = int(raw)
        return value if value > 0 else 2048
    except ValueError:
        return 2048

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

    _cache_lock: ClassVar[RLock] = RLock()
    _cache: ClassVar[OrderedDict[str, "Book | None"]] = OrderedDict()
    _cache_hits: ClassVar[int] = 0
    _cache_misses: ClassVar[int] = 0
    _cache_max_entries: ClassVar[int] = _cache_limit_from_env()

    @classmethod
    def _cache_remember(cls, key: str, value: "Book | None") -> None:
        with cls._cache_lock:
            cls._cache[key] = value
            cls._cache.move_to_end(key)
            if len(cls._cache) > cls._cache_max_entries:
                cls._cache.popitem(last=False)

    @classmethod
    def _cache_evict(cls, key: str) -> None:
        with cls._cache_lock:
            cls._cache.pop(key, None)

    @classmethod
    def clear_cache(cls) -> None:
        with cls._cache_lock:
            cls._cache.clear()
            cls._cache_hits = 0
            cls._cache_misses = 0

    @classmethod
    def get_by_primary_key(cls, search_key: str):
        with cls._cache_lock:
            if search_key in cls._cache:
                cls._cache_hits += 1
                value = cls._cache[search_key]
                cls._cache.move_to_end(search_key)
                return value

        record = super().get_by_primary_key(search_key)
        cls._cache_misses += 1
        cls._cache_remember(search_key, record)
        return record

    @classmethod
    def cache_info(cls) -> Dict[str, int]:
        with cls._cache_lock:
            return {
                "entries": len(cls._cache),
                "hits": cls._cache_hits,
                "misses": cls._cache_misses,
                "max_entries": cls._cache_max_entries,
            }

    def post(self) -> bool:
        created = super().post()
        if created:
            self.__class__._cache_remember(self.id, self)
        return created

    def put(self) -> None:
        super().put()
        self.__class__._cache_remember(self.id, self)

    def delete(self) -> None:
        super().delete()
        self.__class__._cache_evict(self.id)

    @classmethod
    def _drop_table(cls) -> None:
        super()._drop_table()
        cls.clear_cache()

    @classmethod
    def fetch_from_google_books(cls, query: str, max_results: int = 1) -> Optional["Book"]:
        """Fetches metadata from the Google Books API and returns a Book instance

        This will return the first matching volume's metadata as a Book instance
        or `None` when no results or on error.
        """
        if not query:
            return None

        cached = BookMetadataCache.get_by_primary_key(query)
        if cached is not None:
            book = cls.get_by_primary_key(cached.book_id)
            if book is not None:
                return book
            cached.delete()
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

            book = cls._create_from_volume(items[0])
            BookMetadataCache(query=query, book_id=book.id).put()
            # persist and cache the book for future lookups
            book.put()
            BookMetadataCache(query = query, book_id = book.id).put()

            return book

        except Exception:
            return None

    @classmethod
    def _create_from_volume(cls, volume: dict) -> "Book":
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

        pub = info.get("publishedDate")
        if pub:
            try:
                fields["year"] = int(str(pub).split("-")[0])
            except Exception:
                pass

        if hasattr(cls, "model_validate"):
            book = cls.model_validate(fields)
        else:
            book = cls(**fields)

        book.put()
        return book
