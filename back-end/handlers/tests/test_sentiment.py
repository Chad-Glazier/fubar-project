import pytest
from fastapi.testclient import TestClient

from server import app
from db.models.Book import Book
from db.models.UserReview import UserReview
from db.models.SentimentCache import SentimentCache


@pytest.fixture(autouse = True)
def reset_sentiment_cache():
	SentimentCache._drop_table()
	yield
	SentimentCache._drop_table()


def test_sentiment_endpoint_caches_results():
	client = TestClient(app)

	book = Book(id = "sentiment-book-1", title = "Sentiment Book", authors = ["Author"])
	book.put()

	# Include one empty review to confirm it is ignored.
	UserReview(id = "r1", user_id = "u1", book_id = book.id, rating = 9, text = "I love this book. It is great!").put()
	UserReview(id = "r2", user_id = "u2", book_id = book.id, rating = 4, text = "Not bad, but could be better.").put()
	UserReview(id = "r3", user_id = "u3", book_id = book.id, rating = 5, text = "").put()

	resp = client.get(f"/sentiment/{book.id}")
	assert resp.status_code == 200
	body = resp.json()
	assert body["book_id"] == book.id
	assert body["review_count"] == 2
	assert "sentiment" in body
	assert "score" in body
	assert "scores" in body

	# Second call should return the cached entry.
	resp2 = client.get(f"/sentiment/{book.id}")
	assert resp2.status_code == 200
	assert resp2.json() == body
	assert SentimentCache.get_cached(book.id) is not None
