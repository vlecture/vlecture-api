import pytest
from httpx import AsyncClient
from tests.utils.test_db import (
  client, 
  test_db
)

from src.main import app
from unittest.mock import AsyncMock, patch

test_server = "http://staging.api.vlecture.tech"
send_email_verification_url = "/v1/auth/verify"
verify_token_url = "/v1/auth/verify/check"

# Mock API Call
@pytest.mark.asyncio
async def mock_test_send_email_verification_positive(ac: AsyncClient):
  with patch('httpx.AsyncClient') as mock_client:
    mock_post = AsyncMock()
    mock_client.return_value.__aenter__.return_value.post = mock_post

    response = await ac.post(
      url=f"{test_server}{send_email_verification_url}",
      json={
        "email": "vlectureteam@gmail.com",
      }
    )

    mock_post.assert_called_once()
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_send_email_email_dne(test_db):
  async with AsyncClient(app=app) as ac:
    response = await ac.post(
      url=f"{test_server}{send_email_verification_url}",
      json={
        "email": "",
      }
    )

    assert response.status_code == 422

@pytest.mark.asyncio
async def test_send_email_invalid_input(test_db):
  async with AsyncClient(app=app) as ac:
    response = await ac.post(
      url=f"{test_server}{send_email_verification_url}",
      json={
        "email": "thisisnotanemailaddress",
      }
    )

    assert response.status_code == 422

