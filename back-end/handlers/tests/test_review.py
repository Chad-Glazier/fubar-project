from typing import Any
from fastapi.testclient import TestClient
from http import HTTPStatus

from handlers.user import RegistrationDetails
from handlers.review import ReviewDetails
from db.models.User import User, UserSession, TOKEN_NAME
from db.models.UserReview import UserReview
from db.models.Book import Book
from server import app

def setup():
	client = TestClient(app)

	resp = client.post(
		"/user",
		content = RegistrationDetails(
			display_name = "eric_johnson",
			email = "ejohnson54@gmail.com",
			password = "stratocaster123"
		).model_dump_json()
	)
	assert resp.status_code == HTTPStatus.CREATED

	test_user = User.get_first_where(email = "ejohnson54@gmail.com")
	assert test_user != None

	test_books: list[Book] = []
	for i in range(4):
		test_books.append(Book(
			id = f"test_book_id_{i}",
			title = "test book title {i}",
			authors = ["john cena the {i}th"]
		))
	
	for book in test_books:
		book.put()
		retrieved = Book.get_by_primary_key(book.id)
		assert retrieved != None

	return client, test_user, test_books

def cleanup(client: TestClient, test_user: User, test_books: list[Book]):
	session = UserSession.get_first_where(user_id = test_user.id)
	while session != None:
		session.delete()
		session = UserSession.get_first_where(user_id = test_user.id)

	review = UserReview.get_first_where(user_id = test_user.id)
	while review != None:
		review.delete()
		review = UserReview.get_first_where(user_id = test_user.id)

	test_user.delete()
	for test_book in test_books:
		test_book.delete()
	client.cookies.delete(TOKEN_NAME)

def test_create_review():
	client, test_user, test_book = setup()

	resp = client.put(
		f"/review/{test_book[0].id}",
		content = ReviewDetails(
			rating = 4,
			text = "kinda mid tbh"
		).model_dump_json()
	)

	assert resp.status_code == HTTPStatus.CREATED

	body: UserReview = UserReview.model_validate_json(resp.content)

	assert body.book_id == test_book[0].id
	assert body.user_id == test_user.id

	# Check that redundant `put`s are treated as updates
	resp = client.put(
		f"/review/{test_book[0].id}",
		content = ReviewDetails(
			rating = 7,
			text = "it grew on me"
		).model_dump_json()
	)

	assert resp.status_code == HTTPStatus.CREATED

	body: UserReview = UserReview.model_validate_json(resp.content)

	assert body.book_id == test_book[0].id
	assert body.user_id == test_user.id
	assert body.rating == 7

	cleanup(client, test_user, test_book)

def test_get_review():
	client, test_user, test_books = setup()

	reviews = [
		ReviewDetails(rating = 4, text = "kinda mid tbh"),
		ReviewDetails(rating = 1, text = "terrible"),
		ReviewDetails(rating = 10),
		ReviewDetails(rating = 7),
	]
	for review, test_book in zip(reviews, test_books):
		resp = client.put(
			f"/review/{test_book.id}",
			content = review.model_dump_json()
		)
		assert resp.status_code == HTTPStatus.CREATED

	search_resp = client.get(
		f"/review?author_display_name={test_user.display_name}"
	)
	assert search_resp.status_code == HTTPStatus.OK
	body: list[Any] = search_resp.json()
	assert isinstance(body, list)
	assert len(body) == 4

	search_resp = client.get(
		f"/review?author_display_name={test_user.display_name}&limit=2"
	)
	assert search_resp.status_code == HTTPStatus.OK
	body: list[Any] = search_resp.json()
	assert isinstance(body, list)
	assert len(body) == 2

	search_resp = client.get(
		f"/review?author_display_name={test_user.display_name}&require_text=True"
	)
	assert search_resp.status_code == HTTPStatus.OK
	body: list[Any] = search_resp.json()
	assert isinstance(body, list)
	assert len(body) == 2

	cleanup(client, test_user, test_books)

def test_delete_review():
	client, test_user, test_book = setup()

	resp = client.put(
		f"/review/{test_book[0].id}",
		content = ReviewDetails(
			rating = 4,
			text = "kinda mid tbh"
		).model_dump_json()
	)

	assert resp.status_code == HTTPStatus.CREATED

	body: UserReview = UserReview.model_validate_json(resp.content)

	assert body.book_id == test_book[0].id
	assert body.user_id == test_user.id

	resp = client.delete(
		f"/review/{test_book[0].id}"
	)

	assert resp.status_code == HTTPStatus.OK

	resp = client.get(
		f"/review/{test_book[0].id}"
	)

	assert resp.status_code == HTTPStatus.NOT_FOUND

	cleanup(client, test_user, test_book)
