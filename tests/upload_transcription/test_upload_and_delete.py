from tests.utils.test_db import client, test_db
import os
from pydub.generators import Sine

register_url = "/v1/auth/register"
login_url = "/v1/auth/login"
upload_url = "/v1/upload"
delete_url = "/v1/upload/delete/"

file_audio = {'file': ('test_audio.mp3', open(
    'tests/upload_transcription/test_audio.mp3', 'rb'), 'audio/mp3')}
file_non_audio = {'file': ('test_image.jpg', open(
    'tests/upload_transcription/test_image.jpg', 'rb'), 'audio/jpeg')}

user_id = None
filename_test = None

from pydub.generators import Sine

# Path to the dummy large file
dummy_large_file_path = 'tests/upload_transcription/test_large_audio.mp3'

def create_dummy_large_mp3():
    """Helper function to create a dummy large MP3 file of 100MB"""
    duration_in_seconds = 6000  # 6000 seconds of audio to get approximately 100MB file
    bit_rate = "192k"  # 192 kbps

    # Generate a sine wave audio segment of the specified duration
    sine_wave = Sine(440).to_audio_segment(duration=duration_in_seconds, volume=-3.0)
    
    # Export the audio segment to an MP3 file
    sine_wave.export(dummy_large_file_path, format="mp3", bitrate=bit_rate)

def test_upload_large_file_within_limit(test_db):
    """Attempt to upload an audio file within the 100MB limit"""
    create_dummy_large_mp3()  # Create a 100MB dummy file
    with open(dummy_large_file_path, 'rb') as file:
        file_audio_large = {'file': ('test_large_audio.mp3', file, 'audio/mp3')}
        response = client.post(upload_url, files=file_audio_large,
                               headers=get_headers(test_db))

    assert response.status_code == 200
    assert 'filename' in response.json()

    # Clean up the dummy file after the test
    os.remove(dummy_large_file_path)

def test_upload_large_file_over_limit(test_db, dummy_large_mp3_over_limit):
    """Attempt to upload an audio file over the 100MB limit"""
    with open(dummy_large_mp3_over_limit, 'rb') as file:
        file_audio_large = {'file': ('test_large_audio_over_limit.mp3', file, 'audio/mp3')}
        response = client.post(upload_url, files=file_audio_large,
                               headers=get_headers(test_db))

    assert response.status_code == 400
    expected_payload = {
        "status_code": 400,
        "detail": "File size exceeds the 100MB limit",
        "headers": None
    }
    assert response.json() == expected_payload
    
def test_register_user(test_db):
    """Register a user to test upload and delete functionality"""
    global user_id
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
    user_id = response.json().get("id")


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
    response = client.post(upload_url, files=file_non_audio,
                           headers=get_headers(test_db))
    assert response.status_code == 200
    expected_payload = {
        "status_code": 400,
        "detail": "Only MP3 or M4A files are allowed",
        "headers": None
    }
    assert response.json() == expected_payload


def test_edge_upload(test_db):
    """Attempt to upload but not yet logged in"""
    response = client.post(upload_url)
    assert response.status_code == 401


def test_positive_delete(test_db):
    """Attempt to delete an audio file"""
    post = client.post(upload_url, files=file_audio,
                       headers=get_headers(test_db))
    filename = post.json().get("filename")
    response = client.delete(delete_url + filename,
                             headers=get_headers(test_db))
    assert response.status_code == 200


# def test_delete_nonexistent_audio(test_db):
#     """Attempt to delete a non existing audio file"""

#     filename = user_id + "123456_nonexistentfile.mp3"
#     response = client.delete(delete_url + filename,
#                              headers=get_headers(test_db))
#     assert response.status_code == 404


def test_delete_missing_extension_audio(test_db):
    """Attempt to delete a missing extension audio file"""
    global filename_test
    post_test = client.post(upload_url, files=file_audio,
                           headers=get_headers(test_db))
    filename_test = post_test.json().get('filename')
    filename = filename_test[:-4]
    response = client.delete(delete_url + filename,
                             headers=get_headers(test_db))
    assert response.status_code == 404




def test_delete_someone_elses_file(test_db):
    """Attempt to delete someone's else audio"""
    filename = "43663jsd32823_67890_someoneelsesfile.mp3"
    response = client.delete(delete_url + filename,
                             headers=get_headers(test_db))
    assert response.status_code == 401


def test_delete_not_logged_in(test_db):
    """Attempt to delete when not logged in"""
    response = client.delete(delete_url + filename_test)
    assert response.status_code == 401


def test_delete_with_expired_token(test_db):
    """Attempt to delete with an expired token"""
    filename = "12345_ownfile.mp3"
    response = client.delete(delete_url + filename,
                             headers=get_headers(test_db))
    assert response.status_code == 401
    
# def test_delete_with_invalid_filename(test_db):
#     """Attempt to delete audio file with invalid filename"""
#     filename = user_id + "$$$.mp3"
#     response = client.delete(delete_url + filename,
#                              headers=get_headers(test_db))
#     assert response.status_code == 404
