"""
This test, unlike the others, attempts to exhaust the main functionality of the
entire system, including:
- Account registration,
- Session management (login, logout),
- Posting reviews,
- Searching reviews,
- Finding recommendations, and
- Searching books.

The main test can also be referred to as a comprehensive example of how the 
Rest API is meant to be used.
"""
from typing import Generator
import pytest
from fastapi.testclient import TestClient
from server import app
from db.models.User import User, UserSession
from db.models.UserReview import UserReview
from db.models.SavedBook import SavedBook
from db.models.Book import Book
from handlers.review import ReviewDetails
from handlers.user import RegistrationDetails, UserDetails, UserCredentials
from handlers.recommendations import RecommendationItem
from http import HTTPStatus
from uuid import uuid4
from random import randint
from pydantic import TypeAdapter

_USER_EMAIL = "jhendrix42@gmail.com"
_USER_RAW_PASSWORD = "stratocaster123"

@pytest.fixture(scope = "module")
def authenticated_client() -> Generator[tuple[TestClient, User, list[Book]], None, None]:
    client = TestClient(app)
    resp = client.post(
        "/user",
        content = RegistrationDetails(
            display_name = "jimi_hendrix",
            email = _USER_EMAIL,
            password = _USER_RAW_PASSWORD
        ).model_dump_json()
    )

    assert resp.status_code == HTTPStatus.CREATED

    user = User.get_first_where(email = "jhendrix42@gmail.com")

    assert user != None
    
    test_books: list[Book] = []
    for _ in range(10):
        book = Book(id = str(uuid4()), title = str(uuid4()), authors = [str(uuid4())])
        book.put()
        assert Book.get_by_primary_key(book.id) != None
        test_books.append(book)

    # Generate random user reviews (there needs to be more than one user review
    # for the recommendation algorithm to work).
    tmp_reviews: list[UserReview] = []
    tmp_user_ids = [
        "test_" + str(uuid4()),
        "test_" + str(uuid4()),
        "test_" + str(uuid4())
    ]
    for test_book in test_books:
        for tmp_user_id in tmp_user_ids:
            if randint(0, 1) == 1:
                tmp_reviews.append(UserReview(
                    id = str(uuid4()),
                    user_id = tmp_user_id,
                    rating = randint(1, 10),
                    book_id = test_book.id,
                ))
    for tmp_review in tmp_reviews:
        tmp_review.put()

    yield (client, user, test_books)

    # After the test, delete everything in the database associated with 
    # the user.

    session = UserSession.get_first_where(user_id = user.id)
    while session != None:
        session.delete()
        session = UserSession.get_first_where(user_id = user.id)

    review = UserReview.get_first_where(user_id = user.id)
    while review != None:
        review.delete()
        review = UserReview.get_first_where(user_id = user.id)

    saved_book = SavedBook.get_first_where(user_id = user.id)
    while saved_book != None:
        saved_book.delete()
        saved_book = SavedBook.get_first_where(user_id = user.id)        

    user.delete() 

    for book in test_books:
        book.delete()

    for tmp_review in tmp_reviews:
        tmp_review.delete()

def test_system(authenticated_client: tuple[TestClient, User, list[Book]]):

    (client, user, test_books) = authenticated_client

    # 
    # Check that the dummy user account and books were set up correctly.
    #

    resp = client.get("/user")
    assert resp.status_code == HTTPStatus.OK
    body = UserDetails.model_validate_json(resp.content)
    assert body.email == user.email
    assert len(test_books) > 0

    #
    # Check that the user can log out and log in.
    #

    resp = client.delete("/user/session")
    assert resp.status_code == HTTPStatus.OK

    resp = client.get("/user")
    assert resp.status_code == HTTPStatus.NOT_FOUND

    resp = client.post(
        "/user/session",
        content = UserCredentials(
            email = _USER_EMAIL,
            password = _USER_RAW_PASSWORD
        ).model_dump_json()   
    )
    assert resp.status_code == HTTPStatus.OK

    resp = client.get("/user")
    assert resp.status_code == HTTPStatus.OK
    body = UserDetails.model_validate_json(resp.content)
    assert body.email == user.email

    #
    # Have the user create a review for a couple books.
    #

    for book in test_books[:2]:
        resp = client.put(
            f"/review/{book.id}",
            content = ReviewDetails(
                rating = randint(1, 10)
            ).model_dump_json()
        )
        assert resp.status_code == HTTPStatus.CREATED

    #
    # Fetch the user's reviews.
    #

    resp = client.get(
        f"/review?author_display_name={user.display_name}"
    )
    assert resp.status_code == HTTPStatus.OK
    reviews = TypeAdapter(list[UserReview]).validate_json(resp.content)
    assert len(reviews) == 2
    for review in reviews:
        assert review.user_id == user.id

    #
    # Fetch the user's top 3 recommendations
    #
    
    REQUESTED_RECOMMENDATIONS = 3

    resp = client.get(f"/recommendations/{user.id}?n={REQUESTED_RECOMMENDATIONS}")
    assert resp.status_code == HTTPStatus.OK
    recommendations = TypeAdapter(list[RecommendationItem]).validate_json(resp.content)
    assert len(recommendations) == REQUESTED_RECOMMENDATIONS

    #
    # Save the recommended books
    #

    for recommendation in recommendations:
        if recommendation.book != None:
            resp = client.put(f"/saved_book/{recommendation.book.id}")
        else:
            resp = client.put(f"/saved_book/{recommendation.book_id}")
        assert resp.status_code == HTTPStatus.OK

    resp = client.get("/saved_book")
    assert resp.status_code == HTTPStatus.OK
    saved_books = TypeAdapter(list[Book]).validate_json(resp.content)
    assert len(saved_books) == REQUESTED_RECOMMENDATIONS

    

