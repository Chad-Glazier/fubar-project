from contextlib import contextmanager
from fastapi.testclient import TestClient

from db.models.Book import Book
from db.models.UserReview import UserReview
from server import app

@contextmanager
def client_with_temp_app_state(include_reviews: bool = False):
    client = TestClient(app)
    original_book_dir = Book.data_dir
    Book.data_dir = "./data/testing-data"
    Book._drop_table()
    if include_reviews:
        UserReview._drop_table()
    try:
        yield client
    finally:
        Book._drop_table()
        if include_reviews:
            UserReview._drop_table()
        Book.data_dir = original_book_dir
