import jwt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from tests.utils.test_db import client, test_db
from app.auth import renew_access_token, get_user, update_access_token, InvalidFieldName

renew_url = "/v1/auth/renew"

# Positive Cases

def test_renew_access_token_positive(test_db):
    # Assuming a user with a valid refresh token exists in the database
    # Generate a refresh token
    refresh_token_payload = {
        "email": "positive@example.com",
        "first_name": "Positive",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30),  # Assuming the refresh token is not expired
    }
    refresh_token = jwt.encode(refresh_token_payload, "refresh_token_secret")

    # Mock the Authorization header with the refresh token
    authorization_header = {"Authorization": f"Bearer {refresh_token}"}

    # Call the renew endpoint
    response = client.post(renew_url, headers=authorization_header)

    # Check if the response is successful and contains a new access token
    assert response.status_code == 200
    assert "access_token" in response.json()

# Negative Cases

def test_renew_access_token_no_refresh_token(test_db):
    # Call the renew endpoint without providing a refresh token
    response = client.post(renew_url)

    # Check if the response status code is 401 Unauthorized
    assert response.status_code == 401

def test_renew_access_token_invalid_refresh_token(test_db):
    # Mock the Authorization header with an invalid refresh token
    authorization_header = {"Authorization": "Bearer invalid_token"}

    # Call the renew endpoint with the invalid refresh token
    response = client.post(renew_url, headers=authorization_header)

    # Check if the response status code is 401 Unauthorized
    assert response.status_code == 401

def test_renew_access_token_user_not_found(test_db, monkeypatch):
    # Mocking get_user function to simulate user not found scenario
    def mock_get_user(session, field, value):
        raise InvalidFieldName("User not found")

    monkeypatch.setattr("app.auth.get_user", mock_get_user)

    # Assuming a valid refresh token is provided
    refresh_token_payload = {
        "email": "nonexistent@example.com",
        "first_name": "Nonexistent",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
    }
    refresh_token = jwt.encode(refresh_token_payload, "refresh_token_secret")

    # Mock the Authorization header with the refresh token
    authorization_header = {"Authorization": f"Bearer {refresh_token}"}

    # Call the renew endpoint
    response = client.post(renew_url, headers=authorization_header)

    # Check if the response status code is 404 Not Found
    assert response.status_code == 404
