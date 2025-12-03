from contextlib import contextmanager

from fastapi.testclient import TestClient
from pytest import MonkeyPatch

from db.models.UserReview import UserReview
from db.models.Book import Book
from db.persisted_model import PersistedModel
from server import app

@contextmanager
def _test_client_with_temp_data():
    client = TestClient(app)
    original_dir = Book.data_dir
    Book.data_dir = "./data/testing-data"
    Book._drop_table()
    UserReview.data_dir = Book.data_dir
    UserReview._drop_table()
    try:
        yield client
    finally:
        Book._drop_table()
        UserReview._drop_table()
        Book.data_dir = original_dir
        UserReview.data_dir = original_dir


def test_recommendations_endpoint_cold_start():
    with _test_client_with_temp_data() as client:
        tmp_records: list[PersistedModel] = [
            Book(id="b1", title="Book One", authors=["A"]),
            Book(id="b2", title="Book Two", authors=["B"]),
            UserReview(id="r1", user_id="X", book_id="b1", rating=10),
            UserReview(id="r2", user_id="Y", book_id="b2", rating=8),
        ]
        for record in tmp_records:
            record.put()

        res = client.get("/recommendations/NEW_USER?n=2&k=2")
        assert res.status_code == 200
        data = res.json()
        assert isinstance(data, list)
        assert len(data) >= 1


def test_recommendations_enrichment_failure_returns_id(monkeypatch: MonkeyPatch):
    with _test_client_with_temp_data() as client:
        Book(id="known", title="Known", authors=["Author"]).put()
        # target user has only rated "known"
        UserReview(id="r1", user_id="target", book_id="known", rating=10).put()
        # neighbor user rated same known book plus the missing book
        UserReview(id="r2", user_id="neighbor", book_id="known", rating=9).put()
        UserReview(id="r3", user_id="neighbor", book_id="missing-1", rating=8).put()

        def fake_fetch(cls, query: str, max_results: int = 1):
            return None

        monkeypatch.setattr(Book, "fetch_from_google_books", classmethod(fake_fetch))

        res = client.get("/recommendations/target?n=1&k=1")
        assert res.status_code == 200
        payload = res.json()
        assert payload[0]["bookId"] == "missing-1"
