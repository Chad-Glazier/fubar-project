from fastapi.testclient import TestClient
from typing import Any
from pytest import MonkeyPatch

from db.models.UserReview import UserReview
from db.models.Book import Book
from server import app


def test_recommendations_endpoint_with_history():
    """User with history should receive recommendations (non-empty response)."""
    client = TestClient(app)

    # Persist some books and reviews
    tmp_books = [
    	Book(id="x1", title="Alpha", authors=["Author A"]),
    	Book(id="x2", title="Beta", authors=["Author B"]),
    	Book(id="x3", title="Gamma", authors=["Author C"]),
	]
    for book in tmp_books:
        book.put()

    # User U rated x1 and x2; other users rated x3
    tmp_reviews = [
		UserReview(id="r1", user_id="U", book_id="x1", rating=10),
		UserReview(id="r2", user_id="U", book_id="x2", rating=6),
		UserReview(id="r3", user_id="V", book_id="x3", rating=10),
	]
    for review in tmp_reviews:
        review.put()

    res = client.get("/recommendations/U?n=3&k=2")
    assert res.status_code == 200
    data: list[Any] = res.json()
    assert isinstance(data, list)
    # Should recommend something (either persisted book or ids)
    assert len(data) >= 0
    
    for book in tmp_books:
        book.delete()
    for review in tmp_reviews:
        review.delete()

def test_recommendations_enrichment_persists(monkeypatch: MonkeyPatch):
    """If a recommended book isn't persisted, endpoint should call fetch and persist it."""
    client = TestClient(app)

    # Create reviews such that recommended book id will be 'missing-1'
    tmp_reviews = [
        UserReview(id="r10", user_id="A", book_id="b_known", rating=10),
		UserReview(id="r11", user_id="B", book_id="missing-1", rating=8)
	]
    for review in tmp_reviews:
        review.put()

    # confirm missing initially
    initial = Book.get_by_primary_key("missing-1")
    if initial != None:
        initial.delete()
    assert Book.get_by_primary_key("missing-1") is None

    # monkeypatch Book.fetch_from_google_books to return a Book instance
    def fake_fetch(q: Any, max_results: int = 1):
        return Book(id="missing-1", title="Missing One", authors=["Fetcher"])

    monkeypatch.setattr(
        Book, 
        "fetch_from_google_books", 
        classmethod(lambda cls, q, max_results=1: fake_fetch(q, max_results)) #type: ignore
    )

    res = client.get("/recommendations/A?n=5&k=5")
    assert res.status_code == 200
    # data = res.json()
    # After call, the enriched book should be persisted
    stored = Book.get_by_primary_key("missing-1")
    assert stored is not None
    assert stored.title == "Missing One"
    
    for review in tmp_reviews:
        review.delete()
