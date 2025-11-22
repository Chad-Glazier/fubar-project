from typing import Any
from fastapi.testclient import TestClient
from secrets import token_urlsafe
from time import time_ns

from server import app
from db.models.User import User, UserSession, TOKEN_NAME, TOKEN_DURATION_NS
from db.models.Book import Book
from db.models.SavedBook import SavedBook

client = TestClient(app)

def cleanup():
	client.cookies.clear()

	for session in list(UserSession.get_all()):
		session.delete()

	tmp_user = User.get_first_where(email = "test@example.com")
	if tmp_user != None:
		tmp_user.delete()

	tmp_book = Book.get_by_primary_key("b_test")
	if tmp_book != None:
		tmp_book.delete()

	tmp_save = SavedBook.get_first_where(book_id = "b_test")
	while tmp_save != None:
		tmp_save.delete()
		tmp_save = SavedBook.get_first_where(book_id = "b_test")

def setup_data():
	cleanup()

	user = User.create(
		id = "u_test",
		display_name= "Test User",
		email = "test@example.com",
		password = "secret"
	)
	
	book = Book.create(
		id="b_test",
		title="Test Book",
		authors=["Author"],
		description="desc",
	)

	session_token = token_urlsafe(32)
	UserSession(
		session_id = session_token,
		user_id = user.id,
		original_creation_timestamp = time_ns(),
		expiration_timestamp = time_ns() + TOKEN_DURATION_NS
	).post()
	client.cookies.set(TOKEN_NAME, session_token)

	return user, book

def test_save_book():
	user, book = setup_data()

	response = client.put(f"/saved_book/{book.id}")
	assert response.status_code == 200

	saved_items = SavedBook.get_saved_for_user(user.id)
	assert len(saved_items) == 1
	assert saved_items[0].book_id == book.id
	
	cleanup()

def test_get_saved_books():
	_, book = setup_data()

	response = client.put(f"/saved_book/{book.id}")
	assert response.status_code == 200

	response = client.get(f"/saved_book")
	assert response.status_code == 200

	data: list[Any] = response.json()
	assert isinstance(data, list)
	assert len(data) == 1
	assert Book.model_validate(data[0]).id == book.id

	cleanup()

def test_unsave_book():
	user, book = setup_data()

	client.put(f"/saved_book/{book.id}")

	response = client.delete(f"/saved_book/{book.id}")
	assert response.status_code == 200

	saved_items = SavedBook.get_saved_for_user(user.id)
	assert len(saved_items) == 0
	
	cleanup()
