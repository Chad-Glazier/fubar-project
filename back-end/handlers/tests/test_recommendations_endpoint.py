from fastapi.testclient import TestClient
from db.models.UserReview import UserReview
from db.models.Book import Book
from server import app


def setup_module(module):
    # clear persisted tables
    UserReview._drop_table()
    Book._drop_table()


def teardown_module(module):
    UserReview._drop_table()
    Book._drop_table()


def test_recommendations_endpoint_cold_start():
    client = TestClient(app)

    # add some persisted books and reviews
    b1 = Book(id="b1", title="Book One", authors=["A"])
    b1.post()
    b2 = Book(id="b2", title="Book Two", authors=["B"])
    b2.post()

    r1 = UserReview(id="r1", user_id="X", book_id="b1", rating=5.0)
    r1.post()
    r2 = UserReview(id="r2", user_id="Y", book_id="b2", rating=4.0)
    r2.post()

    # call endpoint for a user with no reviews
    res = client.get("/recommendations/NEW_USER?n=2&k=2")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 1
