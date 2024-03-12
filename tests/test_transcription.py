import pytest
from httpx import AsyncClient
from tests.utils.test_db import client, test_db
from src.main import app

create_transcription_url = "/v1/transcription/create"
test_server = "http://staging.api.vlecture.tech"

# Positive Case
@pytest.mark.anyio
async def test_transcription_positive(test_db):
  async with AsyncClient(app=app, base_url=test_server) as ac:
    response = await ac.post(
      create_transcription_url,
      json={
        "s3_filename": "47206ded-fed1-4918-9c39-a677fce2ff82_test_audio.mp3",
        "job_name": "ABCDEFGHIJKLM",
        "language_code": "id-ID"
      }
    )

    assert response.status_code == 201 # Created
    assert response.json()['message'] == "Successfully created audio transcription"

# Negative Case
@pytest.mark.anyio
async def test_transcription_file_dne(test_db):
  async with AsyncClient(app=app, base_url=test_server) as ac:
    response = await ac.post(
      create_transcription_url,
      json={
        "s3_filename": "file-does-not-exist777777.mp3",
        "job_name": "ABCDEFGHIJKLM",
        "language_code": "id-ID"
      }
    )
    
    assert response.status_code == 400

    assert response.json()["error"] == "Au`dio Transcription job failed."