# back-end/tests/test_admin_reports.py

from fastapi.testclient import TestClient
from server import app

from db.models.User import User
from db.models.UserReview import UserReview
from db.models.Report import Report

client = TestClient(app)


# Helpers
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
    r = UserReview(
        id="review-1",
        user_id="user-1",
        book_id="book-1",
        rating=4,
        text="Good book",
    )
    r.put()
    return r

def login(email: str, password: str):
    return client.post("/user/session", json={"email": email, "password": password})


# -------------------------------------------------------------------
# Tests
# -------------------------------------------------------------------

def test_user_can_submit_report():
    create_user()
    create_review()

    login("user@test.com", "pw")

    res = client.post(
        "/admin/reports",
        json={
            "review_id": "review-1",
            "reason": "Spam content",
            "text": "This review looks suspicious."
        }
    )
    assert res.status_code == 200


def test_admin_can_view_reports():
    create_admin()
    login("admin@test.com", "pw")

    res = client.get("/admin/reports")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_admin_can_delete_report_idempotent():
    create_admin()
    login("admin@test.com", "pw")

    # Delete report even if it doesn't exist
    res1 = client.delete("/admin/reports/does-not-exist")
    res2 = client.delete("/admin/reports/does-not-exist")

    assert res1.status_code == 200
    assert res2.status_code == 200


def test_non_admin_cannot_view_reports():
    create_user()
    login("user@test.com", "pw")

    res = client.get("/admin/reports")
    assert res.status_code == 401
