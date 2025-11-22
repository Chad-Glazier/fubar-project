from contextlib import contextmanager
from fastapi.testclient import TestClient

from db.models.Book import Book
from server import app


@contextmanager
def client_with_temp_app_state():
	client = TestClient(app)
	original_book_dir = Book.data_dir
	Book.data_dir = "./data/testing-data"
	Book._drop_table()
	try:
		yield client
	finally:
		Book._drop_table()
		Book.data_dir = original_book_dir
