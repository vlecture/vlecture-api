from tests.utils.test_db import client, test_db

register_url = "/v1/auth/register"
login_url = "/v1/auth/login"
## Authentication Tests ##

# Positive Cases


def test_register_positive(test_db):
    response = client.post(
        register_url,
        json={
            "email": "positive@example.com",
            "first_name": "Positive",
            "middle_name": "Test",
            "last_name": "Case",
            "password": "StrongPassword123",
        },
    )
    assert response.status_code == 200
    assert response.json()["email"] == "positive@example.com"


def test_login_positive(test_db):
    # Assuming a user "positive@example.com" already exists from the register test
    response = client.post(
        login_url,
        json={"email": "positive@example.com", "password": "StrongPassword123"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()

# def test_logout_successful():
#     # Login
#     client.post("/login", data={"username": "user", "password": "password"})

#     # Logout
#     response = client.post("/logout")
#     assert response.status_code == 200

#     # Ensure session token cookie is deleted
#     assert "access_token" not in response.cookies

#     # Access protected endpoint after logout should be unauthorized
#     response = client.get("/home")
#     assert response.status_code == 401 

# Negative Cases


def test_register_missing_fields(test_db):
    response = client.post(
        register_url,
        json={
            # Omitting required fields like 'email', 'first_name', etc.
        },
    )
    assert response.status_code == 422  # Unprocessable Entity


def test_register_user_already_exists(test_db):
    # Assuming a user "positive@example.com" already exists from the register test
    response = client.post(
        register_url,
        json={
            "email": "positive@example.com",
            "first_name": "Positive",
            "middle_name": "Test",
            "last_name": "Case",
            "password": "StrongPassword123",
        },
    )
    assert response.status_code == 409


def test_register_with_invalid_email(test_db):
    response = client.post(
        register_url,
        json={
            "email": "notanemail",
            "first_name": "Invalid",
            "middle_name": "Test",
            "last_name": "Email",
            "password": "invalidemail",
        },
    )
    assert response.status_code == 422  # Invalid email format


def test_register_with_special_characters_in_name(test_db):
    response = client.post(
        register_url,
        json={
            "email": "specialchar@example.com",
            "first_name": "Speci@l",
            "middle_name": "@wesome",
            "last_name": "Ch@r",
            "password": "StrongPassword123",
        },
    )
    assert response.status_code == 200


def test_register_identical_emails_with_different_cases(test_db):
    # Testing case sensitivity in email uniqueness
    response1 = client.post(
        register_url,
        json={
            "email": "CaseSensitiveEmail@example.com",
            "first_name": "Case",
            "middle_name": "Character",
            "last_name": "Sensitive",
            "password": "StrongPassword123",
        },
    )
    response2 = client.post(
        register_url,
        json={
            "email": "casesensitiveemail@example.com",  # Same email in different case
            "first_name": "Case",
            "middle_name": "Character",
            "last_name": "Insensitive",
            "password": "StrongPassword123",
        },
    )
    assert response1.status_code == 200
    assert response2.status_code == 409


def test_login_user_not_found(test_db):
    response = client.post(
        login_url, json={"email": "nonexistent@example.com", "password": "any"}
    )
    assert response.status_code == 404  # Not Found


def test_login_wrong_password(test_db):
    # Assuming a user "positive@example.com" already exists from the register test
    response = client.post(
        login_url,
        json={"email": "positive@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401  # Unauthorized


def test_register_with_long_values(test_db):
    long_string = "a" * 256  # Testing with exceeding the maximum length of 255
    response = client.post(
        register_url,
        json={
            "email": f"{long_string}@example.com",
            "first_name": long_string,
            "middle_name": long_string,
            "last_name": long_string,
            "password": long_string,
        },
    )
    assert response.status_code == 422  # Data too long for one or more fields

# def test_logout_not_logged_in():
#     # Attempt to logout when not logged in
#     response = client.post("/logout")
#     assert response.status_code == 404  
#     assert "access_token" not in response.cookies


# Edge Cases


def test_register_edge_case_boundary_values(test_db):
    # Testing boundary values for fields like 'first_name' and 'last_name'
    response = client.post(
        register_url,
        json={
            "email": "boundary@example.com",
            "first_name": "",  # Empty string
            "middle_name": "Boundary Test Case",
            "last_name": "B" * 255,  # Testing the max length
            "password": "boundarypassword",
        },
    )
    assert (
        response.status_code == 422
    )  # Assuming empty 'first_name' is invalid and 'last_name' length is validated


# def test_logout_successful():
#     # Login
#     client.post("/login", data={"username": "user", "password": "password"})

#     # Logout
#     response = client.post("/logout")
#     assert response.status_code == 200

#     # Ensure session token cookie is deleted
#     assert "access_token" not in response.cookies

#     # Access protected endpoint after logout should be unauthorized
#     response = client.get("/home")
#     assert response.status_code == 401  

# def test_logout_not_logged_in():
#     # Attempt to logout when not logged in
#     response = client.post("/logout")
#     assert response.status_code == 404  
#     assert "access_token" not in response.cookies

# def test_logout_twice():
#     # Login
#     client.post("/login", data={"username": "user", "password": "password"})

#     # Logout once
#     response = client.post("/logout")
#     assert response.status_code == 200

#     # Attempt to logout again
#     response = client.post("/logout")
#     assert response.status_code == 404

# def test_logout_twice():
#     # Login
#     client.post("/login", data={"username": "user", "password": "password"})

#     # Logout once
#     response = client.post("/logout")
#     assert response.status_code == 200

#     # Attempt to logout again
#     response = client.post("/logout")
#     assert response.status_code == 404


    


    

