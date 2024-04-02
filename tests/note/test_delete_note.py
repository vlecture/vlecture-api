from tests.utils.login import login_and_token, register_login_and_token
from tests.utils.test_db import client, test_db

access_token = None

register_url = "/v1/auth/register"
generate_note_url = "/v1/notes/generate"
delete_note_url = "/v1/notes/delete/{note_id}"


def get_headers(test_db):
    """Helper function to get the headers with the access token"""
    global access_token
    access_token = register_login_and_token(test_db)
    assert access_token is not None
    headers = {"Authorization": f"Bearer {access_token}"}
    return headers


def test_generate_note(test_db):
    """Generate a test note to get its note_id"""

    note_title = "Test Note"

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    payload = {
        "title": note_title,
        "language": "English",
        "transcript": "This is a test transcript.",
    }

    response = client.post(
        url=generate_note_url,
        headers=headers,
        json=payload,
    )

    result = response.json()

    assert result["title"] == note_title
    print(response.json())


def test_delete_note_positive(test_db):
    """Test to delete the generated note"""
    note_id = test_generate_note(test_db)
    response = client.delete(delete_note_url.format(
        note_id=note_id), headers=get_headers(test_db))
    assert response.status_code == 200
    assert response.json() == {"message": "Note deleted successfully"}


def test_delete_note_invalid_id(test_db):
    """Test to delete an invalid note ID"""
    response = client.delete(delete_note_url.format(
        note_id=999), headers=get_headers(test_db))
    assert response.status_code == 404
    assert response.json() == {"detail": "Note not found or already deleted."}


def test_delete_note_missing_id(test_db):
    """Test to delete a note without specifying note ID"""
    response = client.delete(delete_note_url.format(
        note_id=""), headers=get_headers(test_db))
    assert response.status_code == 404
    assert response.json() == {"detail": "Note not found or already deleted."}


def test_delete_note_negative(test_db):
    """Test to delete someone else's note"""
    response = client.delete(delete_note_url.format(
        note_id="12345"), headers=get_headers(test_db))
    assert response.status_code == 404
    assert response.json() == {"detail": "Note not found or already deleted."}


def test_delete_note_unauthenticated(test_db):
    """Test to delete a note without authentication"""
    note_id = test_generate_note(test_db)
    response = client.delete(delete_note_url.format(note_id=note_id))
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_delete_note_expired_token(test_db):
    """Test to delete a note with an expired token (invalid token)"""
    expired_token = "expired_token"
    note_id = test_generate_note(test_db)
    headers = {"Authorization": f"Bearer {expired_token}"}
    response = client.delete(delete_note_url.format(
        note_id=note_id), headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
