from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_register_success():
    response = client.post("/auth/register", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    body = response.json()
    assert "user" in body
    assert body["user"]["email"] == "test@example.com"


def test_register_duplicate_email():
    # Register first time
    client.post("/auth/register", json={
        "name": "Test User",
        "email": "duplicate@example.com",
        "password": "pass123"
    })

    # Register same email again
    response = client.post("/auth/register", json={
        "name": "Another User",
        "email": "duplicate@example.com",
        "password": "pass123"
    })

    assert response.status_code in [400, 409]
