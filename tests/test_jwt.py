from jose import jwt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from src.exceptions.users import InvalidFieldName
from tests.utils.test_db import client, test_db

renew_url = "/v1/auth/renew"

# Positive Cases

def test_renew_access_token_positive(test_db):
    refresh_token_payload = {
        "email": "positive@example.com",
        "first_name": "Positive",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
    }
    refresh_token = jwt.encode(refresh_token_payload, "refresh_token_secret")

    authorization_header = {"Authorization": f"Bearer {refresh_token}"}

    response = client.post(renew_url, headers=authorization_header)

    assert response.status_code == 200
    assert "access_token" in response.json()

# Negative Cases

def test_renew_access_token_no_refresh_token(test_db):
    response = client.post(renew_url)

    assert response.status_code == 401

def test_renew_access_token_invalid_refresh_token(test_db):
    authorization_header = {"Authorization": "Bearer invalid_token"}

    response = client.post(renew_url, headers=authorization_header)

    assert response.status_code == 401

def test_renew_access_token_user_not_found(test_db):

    refresh_token_payload = {
        "email": "nonexistent@example.com",
        "first_name": "Nonexistent",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
    }
    refresh_token = jwt.encode(refresh_token_payload, "refresh_token_secret")

    authorization_header = {"Authorization": f"Bearer {refresh_token}"}

    response = client.post(renew_url, headers=authorization_header)

    assert response.status_code == 404
