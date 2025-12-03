# back-end/tests/test_review_delete.py

from fastapi.testclient import TestClient
from server import app

from db.models.User import User
from db.models.UserReview import UserReview

client = TestClient(app)


def create_admin():
    admin = User(
        id="admin-1",
        email="admin@test.com",
        display_name="Admin",
        password_hash=User.hash_password("pw"),
        is_admin=True,
    )
    admin.put()
    return admin


def create_user():
    user = User(
        id="user-1",
        email="user@test.com",
        display_name="User",
        password_hash=User.hash_password("pw"),
        is_admin=False,
    )
    user.put()
    return user


def create_review():
    review = UserReview(
        id="rev-1",
        user_id="user-1",
        book_id="book-1",
        rating=3,
        text="Nice book"
    )
    review.put()
    return review


def login(email, pw):
    return client.post("/user/session", json={"email": email, "password": pw})


# -------------------------------------------------------------------
# Tests
# -------------------------------------------------------------------

def test_admin_can_delete_review():
    create_admin()
    create_user()
    create_review()
    login("admin@test.com", "pw")

    res = client.delete("/admin/reviews/rev-1")
    assert res.status_code == 200


def test_delete_review_idempotent():
    create_admin()
    login("admin@test.com", "pw")

    # Review does not exist but delete should still succeed
    r1 = client.delete("/admin/reviews/not-here")
    r2 = client.delete("/admin/reviews/not-here")

    assert r1.status_code == 200
    assert r2.status_code == 200


def test_non_admin_cannot_delete_review():
    create_user()
    login("user@test.com", "pw")

    res = client.delete("/admin/reviews/rev-1")
    assert res.status_code == 401
