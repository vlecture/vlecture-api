import uuid

import asyncio
import pytest
from httpx import AsyncClient
from tests.utils.test_db import client, test_db
from src.main import app

test_server = "https://staging.api.vlecture.tech"

register_url = "/v1/auth/register"
login_url = "/v1/auth/login"

create_transcription_url = "/v1/transcription/create"
view_transcription_url = "/v1/transcription/view"


pytest_plugins = ('pytest_asyncio',)


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



# Positive Case
@pytest.mark.anyio
async def test_transcription_positive(test_db):
  async with AsyncClient(app=app, base_url=test_server) as ac:
    job_name = "test-" + uuid.uuid4()
    payload = {
      "title": "My Transcription",
      "s3_filename": "test_audio.mp3",
      "job_name": job_name,
      "language_code": "id-ID"
    }

    try:
      token = register_login_and_token()

      response = await ac.post(
        url=create_transcription_url,
        headers={
          'Content-Type': 'application/json', 
          'Authorization': f'Bearer {token}'
        },
        json=payload
      )

      assert response.status_code == 201 # Created
    except RuntimeError:
      pytest.fail()

# Negative Cases

# File does not exist
@pytest.mark.asyncio
async def test_transcription_file_dne(test_db):
  async with AsyncClient(app=app, base_url=test_server) as ac:
    job_name = "test-" + uuid.uuid4()
    payload = {
        "title": "My Transcription",
        "s3_filename": "file-does-not-exist777777.mp3",
        "job_name": job_name,
        "language_code": "id-ID"
    }

    try:
      token = register_login_and_token()

      response = await ac.post(
        url=create_transcription_url,
        headers={
          'Content-Type': 'application/json', 
          'Authorization': f'Bearer {token}'
        },
        json=payload,
      )

      assert response.status_code == 400 # Bad Request
    except RuntimeError:
      pytest.fail()


# Job name already exists
@pytest.mark.asyncio
async def test_transcription_jobname_exists(test_db):
  async with AsyncClient(app=app, base_url=test_server) as ac:
    existing_job_name = "ABCDEFGHIJKLM_1"
    payload = {
      "s3_filename": "test_audio.mp3",
      "job_name": existing_job_name,
      "language_code": "id-ID"
    }

    try:
      token = register_login_and_token()

      response = await ac.post(
        url=create_transcription_url,
        headers={
          'Content-Type': 'application/json', 
          'Authorization': f'Bearer {token}'
        },
        json=payload,
      )

      assert response.status_code == 400 # Bad Request
    except RuntimeError:
      pytest.fail()

@pytest.mark.anyio
async def test_create_transcription_without_login(test_db):
    async with AsyncClient(app=app, base_url=test_server) as ac:
      job_name = "test-" + uuid.uuid4()
      payload = {
        "s3_filename": "test_audio.mp3",
        "job_name": job_name,
        "language_code": "id-ID"
      }

      response = await ac.post(
        url=create_transcription_url,
        json=payload,
      )

      assert response.status_code == 401 # Unauthorized

@pytest.mark.anyio
async def test_view_transcription_success(test_db):
    async with AsyncClient(app=app, base_url=test_server) as ac:
      job_name = "test-" + uuid.uuid4()
      payload = {
        "title": "My Transcription",
        "s3_filename": "test_audio.mp3",
        "job_name": job_name,
        "language_code": "id-ID"
      }

      try:
        token = register_login_and_token()

        response = await ac.post(
          url=create_transcription_url,
          headers={
            'Content-Type': 'application/json', 
            'Authorization': f'Bearer {token}'
          },
          json=payload
        )

        view_tsc_payload = {
          "job_name": job_name
        }

        view_response = await ac.post(
          url=view_transcription_url,
          json=view_tsc_payload
        )

        assert view_response.status_code == 200 # OK
      except RuntimeError:
        pytest.fail()

@pytest.mark.anyio
async def test_view_transcription_dne(test_db):
    async with AsyncClient(app=app, base_url=test_server) as ac:
      job_name = "test-" + uuid.uuid4()
      payload = {
        "title": "My Transcription",
        "s3_filename": "test_audio_not_exists2394828.mp3",
        "job_name": job_name,
        "language_code": "id-ID"
      }

      try:
        token = register_login_and_token()

        view_tsc_payload = {
          "job_name": job_name
        }

        view_response = await ac.post(
          url=view_transcription_url,
          json=view_tsc_payload
        )

        assert view_response.status_code == 400 # BAD REQUEST
      except RuntimeError:
        pytest.fail()