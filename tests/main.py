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


# Negative Cases


def test_register_missing_fields():
    response = client.post(
        "/register",
        json={
            # Omitting required fields like 'email', 'first_name', etc.
        },
    )
    assert response.status_code == 422  # Unprocessable Entity


def test_register_user_already_exists():
    # Assuming a user "positive@example.com" already exists from the register test
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
    assert response.status_code == 409


def test_login_user_not_found():
    response = client.post(
        "/login", json={"email": "nonexistent@example.com", "password": "any"}
    )
    assert response.status_code == 404  # Not Found


def test_login_wrong_password():
    # Assuming a user "positive@example.com" already exists from the register test
    response = client.post(
        "/login", json={"email": "positive@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401  # Unauthorized
