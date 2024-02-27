from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200


def test_delete_transcription_positive():
    transcription_id = "valid_transcription_id"
    response = client.delete(f"/transcriptions/{transcription_id}")
    assert response.status_code == 200
    assert response.json() == {"message": "Transcription deleted successfully"}


def test_delete_transcription_invalid_id():
    invalid_transcription_id = "invalid_transcription_id"
    response = client.delete(f"/transcriptions/{invalid_transcription_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Transcription not found"}


def test_delete_transcription_missing_id():
    response = client.delete("/transcriptions/")
    assert response.status_code == 404


def test_delete_transcription_empty_id():
    empty_transcription_id = ""
    response = client.delete(f"/transcriptions/{empty_transcription_id}")
    assert response.status_code == 404


def test_delete_transcription_none_id():
    response = client.delete("/transcriptions/None")
    assert response.status_code == 404


def test_delete_transcription_special_characters_id():
    special_characters_transcription_id = "!@#$%^&*()"
    response = client.delete(f"/transcriptions/{special_characters_transcription_id}")
    assert response.status_code == 404


def test_delete_transcription_long_id():
    long_transcription_id = "a" * 1000
    response = client.delete(f"/transcriptions/{long_transcription_id}")
    assert response.status_code == 404
