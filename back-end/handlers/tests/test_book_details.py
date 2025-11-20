from fastapi.testclient import TestClient
from db.models.Book import Book
from db.models.UserReview import UserReview
from server import app


def setup_module(module):
    UserReview._drop_table()
    Book._drop_table()


def teardown_module(module):
    UserReview._drop_table()
    Book._drop_table()


def test_book_details_shows_metadata_and_reviews():
    client = TestClient(app)

    # create book and reviews
    b = Book(id="bd1", title="Details Book", authors=["Auth"]) ; b.post()
    UserReview(id="rbd1", user_id="user1", book_id="bd1", rating=4.0).post()
    UserReview(id="rbd2", user_id="user2", book_id="bd1", rating=5.0).post()

    res = client.get("/books/bd1")
    assert res.status_code == 200
    data = res.json()
    assert "book" in data
    assert data["book"]["id"] == "bd1"
    assert "average_rating" in data
    assert abs(data["average_rating"] - 4.5) < 1e-6
    assert data["review_count"] == 2
    assert isinstance(data["reviews"], list)
