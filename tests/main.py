from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200


def test_logout():
    # Logout
    response = client.post("/logout")
    assert response.status_code == 200

    # Ensure session token cookie is deleted
    assert "session_token" not in response.cookies

    # Access protected endpoint after logout should be unauthorized
    response = client.get("/transcribe/upload_audio")
    assert response.status_code == 401  