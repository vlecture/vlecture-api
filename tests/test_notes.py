from tests.utils.test_db import client, test_db

register_url = "/v1/auth/register"
login_url = "/v1/auth/login"
view_notes_url = "/v1/notes/view"


def test_register_user(test_db):
    """Register a user to test notes viewing functionality"""
    data = {
        "email": "notesviewer@example.com",
        "first_name": "Notes",
        "middle_name": "Viewer",
        "last_name": "Example",
        "password": "VeryStrongPassword456"
    }

    response = client.post(register_url, json=data)
    assert response.status_code == 200
    assert response.json()["email"] == "notesviewer@example.com"


def get_access_token(test_db):
    """Helper function to get the access token by logging in"""
    response_login = client.post(
        login_url, json={"email": "notesviewer@example.com", "password": "VeryStrongPassword456"})
    assert response_login.status_code == 200
    access_token = response_login.cookies.get("access_token")
    assert access_token is not None
    return access_token


def get_headers(test_db):
    access_token = get_access_token(test_db)
    headers = {"Authorization": f"Bearer {access_token}"}
    return headers


def test_view_notes_success(test_db):
    """User successfully views their notes when authenticated"""
    access_token = get_access_token(test_db)
    headers = {"Authorization": f"Bearer {access_token}"}

    response = client.get(view_notes_url, headers=headers)

    assert response.status_code == 200


def test_view_notes_unauthenticated(test_db):
    """Unauthenticated user attempts to view notes"""
    response = client.get(view_notes_url)

    assert response.status_code == 401, "Expected 401 Unauthorized"


def test_view_specific_note_not_found(test_db):
    """Attempt to view a specific note that does not exist in the database"""
    access_token = get_access_token(test_db)
    headers = {"Authorization": f"Bearer {access_token}"}

    non_existent_note_id = "some_non_existent_note_id"

    response = client.get(f"{view_notes_url}/{non_existent_note_id}", headers=headers)

    assert response.status_code == 404, "Expected 404 Not Found for a non-existent note ID"
    assert "error" in response.json(), "Expected an error message indicating the note was not found"
    assert response.json()["error"] == "Note not found", "Expected 'Note not found' error message"


def logout_user(test_db):
    response = client.post("/v1/auth/logout")
    assert response.status_code == 200
