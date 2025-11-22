from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from pytest import MonkeyPatch

import httpx
import pytest

from db.models.Book import Book
from db.models.BookMetadataCache import BookMetadataCache


class _FakeResponse:
	def __init__(self, payload: dict[str, Any]):
	def __init__(self, payload: dict):
		self._payload = payload

	def raise_for_status(self) -> None:
		return None

	def json(self) -> dict[str, Any]:
		return self._payload


def _payload(book_id: str) -> dict[str, Any]:
	def json(self) -> dict:
		return self._payload


def _payload(book_id: str = "vol-1") -> dict:
	return {
		"items": [
			{
				"id": book_id,
				"volumeInfo": {
					"title": f"Remote {book_id}",
					"authors": ["Fetcher"],
					"description": "Desc",
					"imageLinks": {"thumbnail": "http://example.com/thumb"},
				},
			}
		]
	}


@contextmanager
def _temp_data_dir():
	original = Book.data_dir
	Book.data_dir = "./data/testing-data"
	Book._drop_table()
	BookMetadataCache._drop_table()
	try:
		yield
	finally:
		Book._drop_table()
		BookMetadataCache._drop_table()
		Book.data_dir = original


def test_fetch_book_uses_cache(monkeypatch: MonkeyPatch):
	with _temp_data_dir():
		calls = {"count": 0}

		def fake_get(url: str, params: dict[str, Any], timeout: float):
			calls["count"] += 1
			return _FakeResponse(_payload("cached-volume"))

		monkeypatch.setattr("db.models.Book.httpx.get", fake_get)

		first = Book.fetch_from_google_books("harry potter")
		assert first is not None
		assert calls["count"] == 1

		second = Book.fetch_from_google_books("harry potter")
		assert second is not None
		assert calls["count"] == 1
		assert second.id == "cached-volume"


def test_fetch_book_refreshes_stale_cache(monkeypatch: MonkeyPatch):
	with _temp_data_dir():
		responses: Iterator[_FakeResponse] = iter(
			[
				_FakeResponse(_payload("first-volume")),
				_FakeResponse(_payload("second-volume")),
			]
		)

		def fake_get(url: str, params: dict[str, Any], timeout: float):
			return next(responses)

		monkeypatch.setattr("db.models.Book.httpx.get", fake_get)

		book = Book.fetch_from_google_books("stale-query")
		assert book is not None
		book_id = book.id
		book.delete()

		book2 = Book.fetch_from_google_books("stale-query")
		assert book2 is not None
		assert book2.id != book_id
		assert book2.id == "second-volume"
					"title": "Test Book",
					"authors": ["Tester"],
					"description": "Desc",
					"imageLinks": {"thumbnail": "http://example.com/image"},
				},
			}
		],
	}


@pytest.fixture(autouse = True)
def reset_tables():
	Book._drop_table()
	BookMetadataCache._drop_table()
	yield
	Book._drop_table()
	BookMetadataCache._drop_table()


def test_fetch_book_caches_result(monkeypatch):
	call_count = {"value": 0}

	def fake_get(url: str, params: dict, timeout: float):
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

	def fake_get(url: str, params: dict, timeout: float):
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
