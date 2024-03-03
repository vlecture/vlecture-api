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


# Edge Cases


def test_register_edge_case_email_formats():
    # Testing with unusual but technically valid email formats
    emails = [
        "email@[123.123.123.123]",
        '"email"@example.com',
        "user.name+tag+sorting@example.com",
    ]
    for email in emails:
        response = client.post(
            "/register",
            json={
                "email": email,
                "first_name": "Edge",
                "middle_name": "Test",
                "last_name": "Case",
                "hashed_password": "edgecasepassword",
            },
        )
        assert response.status_code == 200


def test_login_edge_case_sensitive_email():
    # Assuming emails are case-insensitive
    response = client.post(
        "/login",
        json={"email": "TESTlogin@example.com", "password": "loginpassword123"},
    )
    assert response.status_code == 200


def test_register_edge_case_boundary_values():
    # Testing boundary values for fields like 'first_name' and 'last_name'
    response = client.post(
        "/register",
        json={
            "email": "boundary@example.com",
            "first_name": "",  # Empty string
            "middle_name": "Boundary Test Case",
            "last_name": "B" * 255,  # Testing the max length
            "hashed_password": "boundarypassword",
        },
    )
    assert (
        response.status_code == 422
    )  # Assuming empty 'first_name' is invalid and 'last_name' length is validated
