import pytest
from fastapi.testclient import TestClient

from server import app
from db.models.User import User
from db.models.UserReview import UserReview
from db.models.Penalty import Penalty
from db.models.AuditLog import AuditLog
from db.models.Report import Report

client = TestClient(app)


# -------------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------------

def login_as(email, password):
    """Log in and return the TestClient with session cookies set."""
    response = client.post("/user/session", json={
        "email": email,
        "password": password
    })
    assert response.status_code == 200
    return client


def create_admin_user():
    """Create an admin user in the database."""
    admin = User(
        id="admin123",
        display_name="Admin",
        email="admin@test.com",
        password="$argon2id$v=19$m=65536,t=3,p=4$abc$abc",  # dummy hash
        is_admin=True
    )
    admin.post()
    return admin


def create_normal_user():
    user = User(
        id="user123",
        display_name="RegularUser",
        email="user@test.com",
        password="$argon2id$v=19$m=65536,t=3,p=4$abc$abc",
        is_admin=False
    )
    user.post()
    return user


def create_review():
    review = UserReview(
        id="rev123",
        user_id="user123",
        book_id="book1",
        rating=8,
        text="Good book!"
    )
    review.post()
    return review


# -------------------------------------------------------------------------
# TESTS
# -------------------------------------------------------------------------

def test_admin_cannot_access_without_login():
    response = client.get("/admin/reports")
    assert response.status_code == 401


def test_admin_cannot_access_as_normal_user():
    create_normal_user()

    # log in as normal user
    response = client.post("/user/session", json={
        "email": "user@test.com",
        "password": "pw"
    })
    # session cookie applied to client automatically

    response = client.get("/admin/reports")
    assert response.status_code == 401


def test_admin_can_view_reports_after_login():
    create_admin_user()
    create_normal_user()
    create_review()

    # User submits a report
    client.post("/user/session", json={
        "email": "user@test.com",
        "password": "pw"
    })
    client.post("/admin/report/rev123", json={
        "text": "This review contains spoilers"
    })

    # Admin logs in
    client.post("/user/session", json={
        "email": "admin@test.com",
        "password": "pw"
    })

    response = client.get("/admin/reports")
    assert response.status_code == 200
    reports = response.json()
    assert len(reports) == 1
    assert reports[0]["review_id"] == "rev123"


def test_delete_report_is_idempotent():
    create_admin_user()
    create_normal_user()
    create_review()

    # User reports
    client.post("/user/session", json={
        "email": "user@test.com",
        "password": "pw"
    })
    client.post("/admin/report/rev123", json={"text": "spam"})

    # Admin logs in
    client.post("/user/session", json={
        "email": "admin@test.com",
        "password": "pw"
    })

    # First delete
    r1 = client.delete("/admin/reports/rev123")
    assert r1.status_code == 200

    # Second delete (should ALSO return 200)
    r2 = client.delete("/admin/reports/rev123")
    assert r2.status_code == 200


def test_apply_penalty_creates_penalty_entry():
    create_admin_user()
    create_normal_user()

    # login as admin
    client.post("/user/session", json={
        "email": "admin@test.com",
        "password": "pw"
    })

    response = client.post("/admin/penalty/user123", json={
        "penalty_type": "ban",
        "reason": "abuse",
        "duration_days": 5
    })

    assert response.status_code == 200

    penalties = list(Penalty.get_where(user_id="user123"))
    assert len(penalties) == 1
    assert penalties[0].penalty_type == "ban"


def test_admin_actions_are_logged():
    create_admin_user()
    create_normal_user()

    # admin logs in
    client.post("/user/session", json={
        "email": "admin@test.com",
        "password": "pw"
    })

    # apply penalty
    client.post("/admin/penalty/user123", json={
        "penalty_type": "warning",
        "reason": "spam",
        "duration_days": 0
    })

    logs = list(AuditLog.get_all())
    assert len(logs) == 1
    assert logs[0].action == "apply_penalty"
    assert logs[0].target_id == "user123"
