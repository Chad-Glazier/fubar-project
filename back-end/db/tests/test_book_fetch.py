from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from pytest import MonkeyPatch

from db.models.Book import Book
from db.models.BookMetadataCache import BookMetadataCache


class _FakeResponse:
	def __init__(self, payload: dict[str, Any]):
		self._payload = payload

	def raise_for_status(self) -> None:
		return None

	def json(self) -> dict[str, Any]:
		return self._payload


def _payload(book_id: str) -> dict[str, Any]:
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
