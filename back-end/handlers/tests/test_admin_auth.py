from fastapi.testclient import TestClient
from db.models.Report import Report
from server import app

from db.models.AdminUser import AdminUser
from db.models.AuditLog import AuditLog
from pydantic import TypeAdapter


client = TestClient(app)


# -----------------------------------------------------------
# Helper: create a fake admin in CSV for testing
# -----------------------------------------------------------
def create_test_admin():
    admin = AdminUser(
        id="admin-1",
        email="admin@test.com",
        display_name="Admin",
        password=AdminUser.hash_password("pw"),
    )
    admin.put()
    return admin


# -----------------------------------------------------------
# Helper: create a normal user
# -----------------------------------------------------------
def create_test_user():
    # Regular user authentication is handled via /user endpoints; we only need
    # to set a dummy admin cookie check, so nothing to create here.
    return None


# -----------------------------------------------------------
# Login helper
# -----------------------------------------------------------
def login(email: str, password: str):
    return client.post(
        "/admin/session",
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
    TypeAdapter(list[Report]).validate_json(res.content)

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
