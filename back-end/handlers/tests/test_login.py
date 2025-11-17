from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_login_success():
    # Create user 
    client.post("/auth/register", json={
        "name": "Login User",
        "email": "login@test.com",
        "password": "123456"
    })

    # Login
    response = client.post("/auth/login", json={
        "email": "login@test.com",
        "password": "123456"
    })
    assert response.status_code == 200
    body = response.json()
    assert "user" in body
    assert body["user"]["email"] == "login@test.com"
    assert "session" in response.headers.get("set-cookie", "")


def test_login_wrong_password():
    # Create user
    client.post("/auth/register", json={
        "name": "Wrong PW",
        "email": "wrong@test.com",
        "password": "correctpw"
    })

    # Wrong password
    response = client.post("/auth/login", json={
        "email": "wrong@test.com",
        "password": "incorrectpw"
    })

    assert response.status_code == 401
