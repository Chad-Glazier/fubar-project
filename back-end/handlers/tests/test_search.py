from typing import Callable
from fastapi.testclient import TestClient

from server import app
from db.models.Book import Book


def with_temp_books(func: Callable[[TestClient], None]):
    def wrapper():
        client = TestClient(app)
        original_dir = Book.data_dir
        Book.data_dir = "./data/testing-data"
        Book._drop_table()
        try:
            func(client)
        finally:
            Book._drop_table()
            Book.data_dir = original_dir
    return wrapper


@with_temp_books
def test_search_returns_results_without_auth(client: TestClient):
    Book(id="s1", title="Alpha", authors=["Author"], average_rating=8).put()
    Book(id="s2", title="Beta", authors=["Author"], average_rating=6).put()
    resp = client.get("/search?limit=1&rating_min=7")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == "s1"


@with_temp_books
def test_search_rating_boundaries(client: TestClient):
    Book(id="b-low", title="Low", authors=["Author"], average_rating=5).put()
    Book(id="b-mid", title="Mid", authors=["Author"], average_rating=7).put()
    Book(id="b-high", title="High", authors=["Author"], average_rating=9).put()

    resp = client.get("/search?rating_min=7&rating_max=9")
    assert resp.status_code == 200
    ids = {book["id"] for book in resp.json()}
    assert "b-low" not in ids
    assert "b-mid" in ids
    assert "b-high" in ids


@with_temp_books
def test_search_returns_404_when_no_match(client: TestClient):
    Book(id="only", title="Only", authors=["Solo"], average_rating=9).put()

    resp = client.get("/search?author=Missing")
    assert resp.status_code == 404
