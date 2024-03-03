from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200

def test_logout_successful():
    # Login
    client.post("/login", data={"username": "user", "password": "password"})

    # Logout
    response = client.post("/logout")
    assert response.status_code == 200

    # Ensure session token cookie is deleted
    assert "session_token" not in response.cookies

    # Access protected endpoint after logout should be unauthorized
    response = client.get("/transcribe/upload_audio")
    assert response.status_code == 401  

def test_logout_not_logged_in():
    # Attempt to logout when not logged in
    response = client.post("/logout")
    assert response.status_code == 401  
    assert "session_token" not in response.cookies

def test_logout_twice():
    # Login
    client.post("/login", data={"username": "user", "password": "password"})

    # Logout once
    response = client.post("/logout")
    assert response.status_code == 200

    # Attempt to logout again
    response = client.post("/logout")
    assert response.status_code == 404

# TODO: add test for when user is inactive

    

