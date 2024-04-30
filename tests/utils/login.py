from tests.utils.test_db import (
  client, 
  test_db
)

import asyncio
import pytest

pytest_plugins = ('pytest_asyncio',)

register_url = "/v1/auth/register"
login_url = "/v1/auth/login"

def register_login_and_token(test_db):
  # Register
  register_response = client.post(
      register_url,
      json={
          "email": "positive@example.com",
          "first_name": "Positive",
          "middle_name": "Test",
          "last_name": "Case",
          "password": "positivepassword",
      },
    )
  
  if (register_response.status_code != 200):
    raise RuntimeError("Failed to register")
  
  # Login
  login_response = client.post(
        login_url,
        json={"email": "positive@example.com", "password": "positivepassword"},
    )
  
  access_token = login_response["access_token"]

  return access_token

@pytest.mark.asyncio
async def login_and_token(test_db):
  # NOTE don't forget to check whether jere@email.com user exists in Test/Staging DB

  # Login
  login_response = await client.post(
      login_url,
      json={"email": "jere@email.com", "password": "password"},
  )
  
  print(f"login_response: {login_response}")

  access_token = login_response.json()["access_token"]

  return access_token