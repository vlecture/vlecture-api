from tests.utils.test_db import client, test_db

access_token = None

register_url = "/v1/auth/register"
login_url = "/v1/auth/login"
delete_note_url = "/v1/notes/delete/{note_id}"

def test_register_user(test_db):
    """Register a user to test delete functionality"""
    data = {
        "email": "delete@example.com",
        "first_name": "Delete",
        "middle_name": "Note",
        "last_name": "User",
        "password": "StrongPassword123"
    }

    response = client.post(register_url, json=data)
    assert response.status_code == 200
    assert response.json()["email"] == "delete@example.com"


def get_access_token(test_db):
    """Helper function to get the access token by logging in"""
    global access_token
    response_login = client.post(
        login_url, json={"email": "delete@example.com", "password": "StrongPassword123"})
    assert response_login.status_code == 200
    access_token = response_login.cookies.get("access_token")
    assert access_token is not None


def get_headers():
    """Helper function to get the headers with the access token"""
    assert access_token is not None
    headers = {"Authorization": f"Bearer {access_token}"}
    return headers


# def test_delete_note_positive(test_db):
#     """Test to delete your own existing note"""
#     get_access_token(test_db)
#     response = client.delete(delete_note_url.format(note_id="YOUR_NOTE_ID"), headers=get_headers())
#     assert response.status_code == 200
#     assert response.json() == {"message": "Note deleted successfully"}


# def test_delete_note_invalid_id(test_db):
#     """Test to delete an invalid note ID"""
#     get_access_token(test_db)
#     response = client.delete(delete_note_url.format(note_id="999"), headers=get_headers())
#     assert response.status_code == 404
#     assert response.json() == {"detail": "Note not found or already deleted"}


# def test_delete_note_missing_id(test_db):
#     """Test to delete a note without specifying note ID"""
#     get_access_token(test_db)
#     response = client.delete(delete_note_url.format(note_id=""), headers=get_headers())
#     assert response.status_code == 404
#     assert response.json() == {"detail": "Not Found"}


# def test_delete_note_negative(test_db):
#     """Test to delete someone else's note"""
#     get_access_token(test_db)
#     response = client.delete(delete_note_url.format(note_id="SOME_OTHER_USER_NOTE_ID"), headers=get_headers())
#     assert response.status_code == 403
#     assert response.json() == {"detail": "Note not found or already deleted"}


# def test_delete_note_unauthenticated(test_db):
#     """Test to delete a note without authentication"""
#     response = client.delete(delete_note_url.format(note_id="SOME_NOTE_ID"))
#     assert response.status_code == 401
#     assert response.json() == {"detail": "Not authenticated"}


# def test_delete_note_expired_token(test_db):
#     """Test to delete a note with an expired token"""
#     # Set up a mock expired token
#     expired_token = "expired_token"
#     headers = {"Authorization": f"Bearer {expired_token}"}
#     response = client.delete(delete_note_url.format(note_id="SOME_NOTE_ID"), headers=headers)
#     assert response.status_code == 401
#     assert response.json() == {"detail": "Signature has expired"}
