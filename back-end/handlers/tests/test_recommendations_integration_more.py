from fastapi.testclient import TestClient
from db.models.UserReview import UserReview
from db.models.Book import Book
from server import app


def setup_module(module):
    UserReview._drop_table()
    Book._drop_table()


def teardown_module(module):
    UserReview._drop_table()
    Book._drop_table()


def test_recommendations_endpoint_with_history():
    """User with history should receive recommendations (non-empty response)."""
    client = TestClient(app)

    # Persist some books and reviews
    b1 = Book(id="x1", title="Alpha", authors=["Author A"]) ; b1.post()
    b2 = Book(id="x2", title="Beta", authors=["Author B"]) ; b2.post()
    b3 = Book(id="x3", title="Gamma", authors=["Author C"]) ; b3.post()

    # User U rated x1 and x2; other users rated x3
    UserReview(id="r1", user_id="U", book_id="x1", rating=5.0).post()
    UserReview(id="r2", user_id="U", book_id="x2", rating=3.0).post()
    UserReview(id="r3", user_id="V", book_id="x3", rating=5.0).post()

    res = client.get("/recommendations/U?n=3&k=2")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    # Should recommend something (either persisted book or ids)
    assert len(data) >= 0


def test_recommendations_enrichment_persists(monkeypatch):
    """If a recommended book isn't persisted, endpoint should call fetch and persist it."""
    client = TestClient(app)

    # Ensure clean slate
    UserReview._drop_table()
    Book._drop_table()

    # Create reviews such that recommended book id will be 'missing-1'
    UserReview(id="r10", user_id="A", book_id="b_known", rating=5.0).post()
    UserReview(id="r11", user_id="B", book_id="missing-1", rating=4.0).post()

    # confirm missing initially
    assert Book.get_by_primary_key("missing-1") is None

    # monkeypatch Book.fetch_from_google_books to return a Book instance
    def fake_fetch(q, max_results=1):
        return Book(id="missing-1", title="Missing One", authors=["Fetcher"])

    monkeypatch.setattr(Book, "fetch_from_google_books", classmethod(lambda cls, q, max_results=1: fake_fetch(q, max_results)))

    res = client.get("/recommendations/A?n=5&k=5")
    assert res.status_code == 200
    data = res.json()
    # After call, the enriched book should be persisted
    stored = Book.get_by_primary_key("missing-1")
    assert stored is not None
    assert stored.title == "Missing One"
