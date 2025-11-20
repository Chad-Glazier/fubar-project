from db.persisted_model import PersistedModel
from typing import Dict, Optional
import httpx
from urllib.parse import quote as _quote
import uuid


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

        url = f"https://www.googleapis.com/books/v1/volumes?q={_quote(query)}&maxResults={max_results}"
        try:
            resp = httpx.get(url, timeout=5.0)
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
                return cls.model_validate(fields)
            return cls(**fields)

        except Exception:
            return None
