from tests.utils.test_db import client, test_db

register_url = "/v1/auth/register"
login_url = "/v1/auth/login"
upload_url = "/v1/upload"

file_audio = {'file': ('test_audio.mp3', open(
    'tests/test_audio.mp3', 'rb'), 'audio/mp3')}
file_non_audio = {'file': ('test_image.png' , open(
    'tests/test_image.png', 'rb'), 'audio/jpeg')}


def test_register_user(test_db):
    """Register a user to test upload functionality"""
    data = {
        "email": "upload@example.com",
        "first_name": "Upload",
        "middle_name": "Audio",
        "last_name": "File",
        "password": "StrongPassword123"
    }

    response = client.post(register_url, json=data)
    assert response.status_code == 200
    assert response.json()["email"] == "upload@example.com"


def get_access_token(test_db):
    """Helper function to get the access token by logging in"""
    response_login = client.post(
        login_url, json={"email": "upload@example.com", "password": "StrongPassword123"})
    assert response_login.status_code == 200
    access_token = response_login.cookies.get("access_token")
    assert access_token is not None
    return access_token


def get_headers(test_db):
    access_token = get_access_token(test_db)
    headers = {"Authorization": f"Bearer {access_token}"}
    return headers


def test_positive_upload(test_db):
    """Attempt to upload an audio file"""

    response = client.post(upload_url, files=file_audio,
                           headers=get_headers(test_db))

    assert response.status_code == 200
    assert 'filename' in response.json()


def test_negative_upload(test_db):
    """Attempt to upload a non audio file"""
    access_token = get_access_token(test_db)

    headers = {"Authorization": f"Bearer {access_token}"}

    response = client.post(upload_url, files=file_non_audio,
                           headers=get_headers(test_db))

    assert response.status_code == 200
    expected_payload = {
        "status_code": 400,
        "detail": "Only MP3 or M4A files are allowed",
        "headers": None
    }
    assert response.json() == expected_payload


def logout_user(test_db):
    response = client.post("/logout")
    assert response.status_code == 200

def test_edge_upload(test_db):
    """Attempt to upload but not yet logged in"""
    response = client.post(upload_url)
    assert response.status_code == 401

