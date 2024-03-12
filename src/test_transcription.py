from fastapi.testclient import TestClient

from .main import app

client = TestClient(app)

# Positive Case
def test_transcription_positive():
  response = client.post(
    "/v1/transcription/test_audio.mp3",
  )

  assert response.status_code == 201 # Created
  assert response.json()['message'] == "Successfully created audio transcription"

# Negative Case
def test_transcription_file_dne():
  response = client.post(
    "/v1/transcription/file_doesnt_exist.mp3",
  )
  
  assert response.status_code == 400

  assert response.json()["error"] == "Audio Transcription job failed."