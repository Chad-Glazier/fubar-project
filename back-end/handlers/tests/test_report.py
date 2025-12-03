import pytest
from fastapi.testclient import TestClient

from server import app
from db.models.User import User
from db.models.UserReview import UserReview
from db.models.Report import Report
from db.models.Penalty import Penalty
from db.models.AuditLog import AuditLog

client = TestClient(app)


# -------------------------------------------------------------
# Helper functions
# -------------------------------------------------------------

def login(email: str, password: str):
    """Logs in and stores cookies on the client."""
    response = client.post("/user/session", json={
        "email": email,
        "password": password
    })
    assert response.status_code in (200, 201)
    return client


def create_admin():
    admin = User(
        id="admin123",
        display_name="Admin",
        email="admin@test.com",
        password="$argon2id$v=19$m=65536,t=3,p=4$abc$abc",  # dummy hash
        is_admin=True
    )
    admin.post()
    return admin


def create_user():
    user = User(
        id="user123",
        display_name="User",
        email="user@test.com",
        password="$argon2id$v=19$m=65536,t=3,p=4$abc$abc",
        is_admin=False
    )
    user.post()
    return user


def create_review():
    review = UserReview(
        id="rev1",
        user_id="user123",
        book_id="book1",
        rating=8,
        text="Nice book!"
    )
    review.post()
    return review


# -------------------------------------------------------------
# TESTS
# -------------------------------------------------------------

def test_non_logged_in_user_cannot_view_reports():
    """Unauthenticated users cannot access admin endpoints."""
    response = client.get("/admin/reports")
    assert response.status_code == 401


def test_normal_user_cannot_view_reports():
    """Regular users cannot access admin endpoints."""
    create_user()
    login("user@test.com", "pw")

    response = client.get("/admin/reports")
    assert response.status_code == 401


def test_user_can_submit_report():
    """User can report a review."""
    create_user()
    create_review()

    login("user@test.com", "pw")

    response = client.post("/admin/reports/rev1", json={
        "text": "This review contains spoilers"
    })

    assert response.status_code == 200

    reports = list(Report.get_all())
    assert len(reports) == 1
    assert reports[0].review_id == "rev1"
    assert reports[0].user_id == "user123"


def test_admin_can_view_reports():
    """Admin can view all submitted reports."""
    create_admin()
    login("admin@test.com", "pw")

    response = client.get("/admin/reports")
    assert response.status_code == 200
    assert type(response.json()) is list


def test_delete_reports_is_idempotent():
    """DELETE /admin/reports/{review_id} always succeeds."""
    create_admin()
    login("admin@test.com", "pw")

    # First delete (maybe exists)
    r1 = client.delete("/admin/reports/rev1")
    assert r1.status_code == 200

    # Second delete (should still succeed even if nothing was deleted)
    r2 = client.delete("/admin/reports/rev1")
    assert r2.status_code == 200


def test_apply_penalty_creates_penalty_and_log():
    """Admin can apply penalty; audit log is generated."""
    create_admin()
    create_user()
    login("admin@test.com", "pw")

    response = client.post("/admin/penalty/user123", json={
        "penalty_type": "ban",
        "reason": "abusive behavior",
        "duration_days": 7
    })

    assert response.status_code == 200

    penalties = list(Penalty.get_where(user_id="user123"))
    assert len(penalties) == 1
    assert penalties[0].penalty_type == "ban"

    logs = list(AuditLog.get_all())
    assert len(logs) == 1
    assert logs[0].action == "apply_penalty"
    assert logs[0].target_id == "user123"
