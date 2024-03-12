from tests.utils.test_db import client, test_db

register_url = "/v1/auth/register"
login_url = "/v1/auth/login"
view_url = "/v1/transcription/view"


def test_register_user(test_db):

    data = {
        "email": "upload@example.com",
        "first_name": "View",
        "middle_name": "Transcription",
        "last_name": "File",
        "password": "StrongPassword123",
    }

    response = client.post(register_url, json=data)
    assert response.status_code == 200
    assert response.json()["email"] == "upload@example.com"


def get_access_token(test_db):
    response_login = client.post(
        login_url, json={"email": "upload@example.com", "password": "StrongPassword123"}
    )
    assert response_login.status_code == 200
    access_token = response_login.cookies.get("access_token")
    assert access_token is not None
    return access_token


def view_transcription(test_db):
    response_view = client.post(
        view_url, json={"job_name": "67208f3b-fec6-4dd0-b9c7-711b5159c761"}
    )
    assert response_view.status_code == 200
    data = response_view.cookies.get("data")
    assert data is not None
    return data


def test_positive_view(test_db):

    access_token = get_access_token(test_db)

    headers = {"Authorization": f"Bearer {access_token}"}

    response_view = client.post(
        view_url,
        json={"job_name": "67208f3b-fec6-4dd0-b9c7-711b5159c761"},
        headers=headers,
    )

    # Assertions
    assert response_view.status_code == 200
    assert "data" in response_view.json()


def test_negative_upload(test_db):
    """Attempt to upload a non audio file"""
    access_token = get_access_token(test_db)

    headers = {"Authorization": f"Bearer {access_token}"}

    response = client.post(
        view_url,
        json={"job_name": "67208f3b-fec6-4dd0-b9c7-711b5159c761"},
        headers=headers,
    )

    assert response.status_code == 200
    expected_payload = {
        "status_code": 400,
        "detail": "Only job_name are allowed",
        "headers": None,
    }
    assert response.json() == expected_payload


def test_view_transcription_with_invalid_job_name(test_db):

    _, access_token = get_access_token(test_db)
    headers = {"Authorization": f"Bearer {access_token}"}

    response = client.get(
        view_url,
        headers=headers,
        params={"job_name": "invalid_job_name"},  # Using an invalid job_name
    )

    assert (
        response.status_code == 404
    )  # Assuming the endpoint returns a 404 for non-existent job names
    assert "error" in response.json()
    assert response.json()["error"] == "Transcription job not found."


def test_view_transcription_without_authentication(test_db):
    response = client.get(
        view_url,
        params={
            "job_name": "67208f3b-fec6-4dd0-b9c7-711b5159c761"
        },  # Using a valid job_name for this test
    )

    assert (
        response.status_code == 401
    )  # Expecting unauthorized access due to missing credentials
    assert "detail" in response.json()
    assert response.json()["detail"] == "Not authenticated"


def test_view_transcription_with_expired_token(test_db):
    _, access_token = get_access_token(
        test_db, expire_token=True
    )  # Assuming this helper can simulate an expired token
    headers = {"Authorization": f"Bearer {access_token}"}

    response = client.get(
        view_url,
        headers=headers,
        params={"job_name": "67208f3b-fec6-4dd0-b9c7-711b5159c761"},
    )

    assert (
        response.status_code == 403
    )  # Assuming the API returns 403 for expired tokens
    assert "detail" in response.json()
    assert response.json()["detail"] == "Token has expired"
