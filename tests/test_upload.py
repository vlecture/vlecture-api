from tests.utils.test_db import client

def test_register_user():
    data = {
        "email": "@example.com",
        "first_name": "first",
        "middle_name": "middle",
        "last_name": "last",
        "password": "StrongPassword123"
    }

    response = client.post("/register", json=data)
    assert response.status_code == 200


def test_positive_upload():
    """Attempt to upload an audio file"""
    test_register_user()
    response_login = client.post(
        "/login", json={"email": "test@example.com", "password": "StrongPassword123"})
    assert response_login.status_code == 200
    access_token = response_login.cookies.get("access_token")
    assert access_token is not None

    files = {'file': ('test_audio.mp3', open(
        'test_audio.mp3', 'rb'), 'audio/mp3')}
    response = client.post("/upload", files=files)
    assert response.status_code == 200
    assert 'filename' in response.json()


def test_negative_upload():
    """Attempt to upload a non audio file"""
    test_register_user()
    response_login = client.post(
        "/login", json={"email": "test@example.com", "password": "StrongPassword123"})
    assert response_login.status_code == 200
    access_token = response_login.cookies.get("access_token")
    assert access_token is not None

    files = {'file': ('test_image.jpg', open(
        'test_image.jpg', 'rb'), 'image/jpeg')}
    response = client.post("/upload", files=files)
    assert response.status_code == 200
    expected_payload = {
        "status_code": 400,
        "detail": "Only MP3 or M4A files are allowed",
        "headers": None
    }
    assert response.json() == expected_payload
