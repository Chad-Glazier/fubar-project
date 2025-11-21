from fastapi.testclient import TestClient
from db.models.UserReview import UserReview
from db.models.Book import Book
from db.persisted_model import PersistedModel
from server import app

def test_recommendations_endpoint_cold_start():
    client = TestClient(app)

    # add some persisted books and reviews
    tmp_records: list[PersistedModel] = [
        Book(id="b1", title="Book One", authors=["A"]),
		Book(id="b2", title="Book Two", authors=["B"]),
		UserReview(id="r1", user_id="X", book_id="b1", rating=5.0),
		UserReview(id="r2", user_id="Y", book_id="b2", rating=4.0),
	]
    for record in tmp_records:
        record.put()

    # call endpoint for a user with no reviews
    res = client.get("/recommendations/NEW_USER?n=2&k=2")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 1 #type: ignore
    
    for record in tmp_records:
        record.delete()
