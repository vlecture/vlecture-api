from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200


## Authentication Tests ##

# Positive Cases


def test_register_positive():
    response = client.post(
        "/register",
        json={
            "email": "positive@example.com",
            "first_name": "Positive",
            "middle_name": "Test",
            "last_name": "Case",
            "hashed_password": "positivepassword",
        },
    )
    assert response.status_code == 200
    assert response.json()["email"] == "positive@example.com"


def test_login_positive():
    # Assuming a user "positive@example.com" already exists from the register test
    response = client.post(
        "/login", json={"email": "positive@example.com", "password": "positivepassword"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()
