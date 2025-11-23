from pytest import MonkeyPatch
from db.models.UserReview import UserReview
from db.models.Book import Book

from .test_utils import client_with_temp_app_state

def test_book_details_shows_metadata_and_reviews():
    client = TestClient(app)

    # create book and reviews
    tmp_records: list[UserReview | Book] = [
        Book(id="bd1", title="Details Book", authors=["Auth"]),
        UserReview(id="rbd1", user_id="user1", book_id="bd1", rating=8),
        UserReview(id="rbd2", user_id="user2", book_id="bd1", rating=10)
	]
    for record in tmp_records:
        record.put()

    res = client.get("/books/bd1")
    assert res.status_code == 200
    data = res.json()
    assert "book" in data
    assert data["book"]["id"] == "bd1"
    assert "average_rating" in data
    assert abs(data["average_rating"] - 9.0) < 1e-6
    assert data["review_count"] == 2
    assert isinstance(data["reviews"], list)
    
    for record in tmp_records:
        record.delete()


def test_list_books_for_guests():
    client = TestClient(app)
    original_dir = Book.data_dir
    Book.data_dir = "./data/testing-data"
    Book._drop_table()

    books = [
        Book(id="b1", title="Browse 1", authors=["A"]),
        Book(id="b2", title="Browse 2", authors=["B"]),
    ]
    for book in books:
        book.put()

    res = client.get("/books?limit=1")
    assert res.status_code == 200
    payload = res.json()
    assert isinstance(payload, list)
    assert len(payload) == 1
    assert payload[0]["id"] in {"b1", "b2"}

    Book._drop_table()
    Book.data_dir = original_dir


def test_book_details_fetches_remote_when_missing(monkeypatch):
    client = TestClient(app)
    original_dir = Book.data_dir
    Book.data_dir = "./data/testing-data"
    Book._drop_table()

    def fake_fetch(cls, query: str, max_results: int = 1):
        book = Book(id=query, title="Remote Book", authors=["Fetcher"])
        book.put()
        return book

    monkeypatch.setattr(Book, "fetch_from_google_books", classmethod(fake_fetch))

    res = client.get("/books/remote-123")
    assert res.status_code == 200
    data = res.json()
    assert data["book"]["id"] == "remote-123"
    assert data["book"]["title"] == "Remote Book"

    Book._drop_table()
    Book.data_dir = original_dir
