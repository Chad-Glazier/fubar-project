from fastapi.testclient import TestClient
from server import app

from db.models.User import User
from db.models.AuditLog import AuditLog

client = TestClient(app)


# -----------------------------------------------------------
# Helper: create a fake admin in CSV for testing
# -----------------------------------------------------------
def create_test_admin():
    admin = User(
        id="admin-1",
        email="admin@test.com",
        display_name="Admin",
        password_hash=User.hash_password("pw"),
        is_admin=True,
    )
    admin.put()
    return admin


# -----------------------------------------------------------
# Helper: create a normal user
# -----------------------------------------------------------
def create_test_user():
    user = User(
        id="user-1",
        email="user@test.com",
        display_name="NormalUser",
        password_hash=User.hash_password("pw"),
        is_admin=False,
    )
    user.put()
    return user


# -----------------------------------------------------------
# Login helper
# -----------------------------------------------------------
def login(email: str, password: str):
    return client.post(
        "/user/session",
        json={"email": email, "password": password}
    )


# -----------------------------------------------------------
# 1. Unauthenticated users CANNOT access admin routes
# -----------------------------------------------------------
def test_admin_requires_login():
    res = client.get("/admin/dashboard")
    assert res.status_code == 401
    assert res.json()["detail"] == "Administrator access required."


# -----------------------------------------------------------
# 2. Normal user CANNOT access admin routes
# -----------------------------------------------------------
def test_non_admin_forbidden():
    create_test_user()

    # login as normal user
    login("user@test.com", "pw")

    res = client.get("/admin/dashboard")
    assert res.status_code == 401
    assert res.json()["detail"] == "Administrator access required."


# -----------------------------------------------------------
# 3. Admin CAN access admin routes
# -----------------------------------------------------------
def test_admin_can_access_dashboard():
    create_test_admin()

    # login as admin
    login("admin@test.com", "pw")

    res = client.get("/admin/dashboard")
    assert res.status_code == 200
    assert "flagged_reviews" in res.json()


# -----------------------------------------------------------
# 4. Admin can access audit logs
# -----------------------------------------------------------
def test_admin_can_view_audit_logs():
    create_test_admin()
    login("admin@test.com", "pw")

    # Admin must be able to fetch audit logs
    res = client.get("/admin/audit")
    assert res.status_code == 200
    assert isinstance(res.json(), list)
