from fastapi.testclient import TestClient

from server import app
from db.User import User
from db.Book import Book
from db.SavedBook import SavedBook

client = TestClient(app)


def setup_function():
    SavedBook._drop_table()


def setup_data():
    user = User.create(
        id="u_test",
        name="Test User",
        display_name="Test User",
        email="test@example.com",
        password="secret",
    )
    book = Book.create(
        id="b_test",
        title="Test Book",
        authors=["Author"],
        description="desc",
    )
    return user, book


def test_save_book():
    user, book = setup_data()

    response = client.post(f"/users/{user.id}/saved/{book.id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Book saved"

    saved_items = SavedBook.get_saved_for_user(user.id)
    assert len(saved_items) == 1
    assert saved_items[0].book_id == book.id


def test_get_saved_books():
    user, book = setup_data()

    client.post(f"/users/{user.id}/saved/{book.id}")

    response = client.get(f"/users/{user.id}/saved")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["book_id"] == book.id


def test_unsave_book():
    user, book = setup_data()

    client.post(f"/users/{user.id}/saved/{book.id}")

    response = client.delete(f"/users/{user.id}/saved/{book.id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Book removed"

    saved_items = SavedBook.get_saved_for_user(user.id)
    assert len(saved_items) == 0
