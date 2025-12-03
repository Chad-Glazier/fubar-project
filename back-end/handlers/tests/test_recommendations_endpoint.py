import asyncio
from contextlib import contextmanager

from pytest import MonkeyPatch

from db.models.UserReview import UserReview
from db.models.Book import Book
from db.persisted_model import PersistedModel
from handlers.recommendations import get_recommendations, RecommendationItem


def _run_recommendations(user_id: str, n: int, k: int) -> list[RecommendationItem]:
    return asyncio.run(get_recommendations(user_id, n=n, k=k))


@contextmanager
def _temp_data_dir():
    original_book_dir = Book.data_dir
    original_review_dir = UserReview.data_dir
    Book.data_dir = "./data/testing-data"
    UserReview.data_dir = Book.data_dir
    Book.clear_cache()
    Book._drop_table()
    UserReview._drop_table()
    try:
        yield
    finally:
        Book._drop_table()
        UserReview._drop_table()
        Book.data_dir = original_book_dir
        UserReview.data_dir = original_review_dir
        Book.clear_cache()


def test_recommendations_endpoint_cold_start():
    with _temp_data_dir():
        tmp_records: list[PersistedModel] = [
            Book(id="b1", title="Book One", authors=["A"]),
            Book(id="b2", title="Book Two", authors=["B"]),
            UserReview(id="r1", user_id="X", book_id="b1", rating=10),
            UserReview(id="r2", user_id="Y", book_id="b2", rating=8),
        ]
        for record in tmp_records:
            record.put()

        data = _run_recommendations("NEW_USER", n=2, k=2)
        assert isinstance(data, list)
        assert len(data) >= 1


def test_recommendations_enrichment_failure_returns_id(monkeypatch: MonkeyPatch):
    with _temp_data_dir():
        Book(id="known", title="Known", authors=["Author"]).put()
        # target user has only rated "known"
        UserReview(id="r1", user_id="target", book_id="known", rating=10).put()
        # neighbor user rated same known book plus the missing book
        UserReview(id="r2", user_id="neighbor", book_id="known", rating=9).put()
        UserReview(id="r3", user_id="neighbor", book_id="missing-1", rating=8).put()

        def fake_fetch(cls, query: str, max_results: int = 1):
            return None

        monkeypatch.setattr(Book, "fetch_from_google_books", classmethod(fake_fetch))

        payload = _run_recommendations("target", n=1, k=1)
        assert payload[0].book_id == "missing-1"
