import os
import uuid
from typing import Dict, Optional
from urllib.parse import quote as _quote

import httpx
from dotenv import load_dotenv

from db.persisted_model import PersistedModel

# Load local .env if present (safe no-op if not)
load_dotenv()


class Book(PersistedModel):
    id: str
    title: str
    authors: list[str]
    categories: list[str] | None = None
    description: str | None = None
    imageLinks: Dict[str, str] | None = None
    average_rating: float | None = None

    @classmethod
    def fetch_from_google_books(cls, query: str, max_results: int = 1) -> Optional["Book"]:
        """Fetch the first matching volume from Google Books as a Book instance."""
        if not query:
            return None

        params = {"q": _quote(query), "maxResults": max_results}
        key = os.getenv("GOOGLE_BOOKS_API_KEY")
        if key:
            params["key"] = key

        try:
            resp = httpx.get(
                "https://www.googleapis.com/books/v1/volumes",
                params=params,
                timeout=5.0,
            )
            resp.raise_for_status()
        except Exception:
            return None

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

        pub = info.get("publishedDate")
        if pub:
            try:
                fields["year"] = int(str(pub).split("-")[0])
            except Exception:
                pass

        return cls(**fields)
