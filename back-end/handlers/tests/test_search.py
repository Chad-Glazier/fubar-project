from fastapi.testclient import TestClient

from server import app
from db.models.Book import Book


def test_search_returns_results_without_auth():
    client = TestClient(app)
    original_dir = Book.data_dir
    Book.data_dir = "./data/testing-data"
    Book._drop_table()

    books = [
        Book(id="s1", title="Alpha", authors=["Author"], average_rating=8),
        Book(id="s2", title="Beta", authors=["Author"], average_rating=6),
    ]
    for book in books:
        book.put()

    resp = client.get("/search?limit=1&rating_min=7")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == "s1"

    Book._drop_table()
    Book.data_dir = original_dir
