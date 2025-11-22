from collections.abc import Iterator
from typing import Any

import httpx
import pytest

from db.models.Book import Book
from db.models.BookMetadataCache import BookMetadataCache

TEST_DATA_DIR = "./data/testing-data"


class _FakeResponse:
    def __init__(self, payload: dict[str, Any]):
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, Any]:
        return self._payload


def _payload(book_id: str = "vol-1") -> dict[str, Any]:
    return {
        "items": [
            {
                "id": book_id,
                "volumeInfo": {
                    "title": "Test Book",
                    "authors": ["Tester"],
                    "description": "Desc",
                    "imageLinks": {"thumbnail": "http://example.com/image"},
                },
            }
        ],
    }


@pytest.fixture(autouse=True)
def reset_tables():
    original_dir = Book.data_dir
    Book.data_dir = TEST_DATA_DIR
    Book._drop_table()
    BookMetadataCache._drop_table()
    yield
    Book._drop_table()
    BookMetadataCache._drop_table()
    Book.data_dir = original_dir


def test_fetch_book_caches_result(monkeypatch):
    call_count = {"value": 0}

    def fake_get(url: str, params: dict[str, Any], timeout: float):
        call_count["value"] += 1
        return _FakeResponse(_payload("vol-cached"))

    monkeypatch.setattr(httpx, "get", fake_get)

    first = Book.fetch_from_google_books("harry potter")
    assert first is not None
    assert call_count["value"] == 1

    second = Book.fetch_from_google_books("harry potter")
    assert second is not None
    assert call_count["value"] == 1  # result was cached
    assert second.id == first.id


def test_fetch_book_refreshes_stale_cache(monkeypatch):
    calls: list[str] = []

    def response_iterator() -> Iterator[_FakeResponse]:
        yield _FakeResponse(_payload("vol-1"))
        yield _FakeResponse(_payload("vol-2"))

    responses = response_iterator()

    def fake_get(url: str, params: dict[str, Any], timeout: float):
        resp = next(responses)
        calls.append(params["q"])
        return resp

    monkeypatch.setattr(httpx, "get", fake_get)

    book = Book.fetch_from_google_books("cached-query")
    assert book is not None
    assert book.id == "vol-1"
    book.delete()  # remove the stored book but leave cache entry

    book_again = Book.fetch_from_google_books("cached-query")
    assert book_again is not None
    assert book_again.id == "vol-2"
    assert calls.count("cached-query") == 2
