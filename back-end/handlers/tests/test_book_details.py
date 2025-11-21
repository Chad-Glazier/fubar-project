from fastapi.testclient import TestClient
from db.models.Book import Book
from db.models.UserReview import UserReview
from db.persisted_model import PersistedModel
from server import app

def test_book_details_shows_metadata_and_reviews():
    client = TestClient(app)

    # create book and reviews
    tmp_records: list[PersistedModel] = [
        Book(id="bd1", title="Details Book", authors=["Auth"]),
        UserReview(id="rbd1", user_id="user1", book_id="bd1", rating=4.0),
        UserReview(id="rbd2", user_id="user2", book_id="bd1", rating=5.0)
	]
    for record in tmp_records:
        record.put()

    res = client.get("/books/bd1")
    assert res.status_code == 200
    data = res.json()
    assert "book" in data
    assert data["book"]["id"] == "bd1"
    assert "average_rating" in data
    assert abs(data["average_rating"] - 4.5) < 1e-6
    assert data["review_count"] == 2
    assert isinstance(data["reviews"], list)
    
    for record in tmp_records:
        record.delete()
