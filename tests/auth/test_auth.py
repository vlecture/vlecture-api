from tests.utils.test_db import client, test_db
from tests.auth.utils import (
    REGISTER_URL,
    LOGIN_URL,
    USER_REG,
    USER_LOGIN,
    USER_LOGIN_NON_EXIST,
    USER_LOGIN_WRONG_PW,
    USER_REG_INV_EMAIL,
    USER_REG_SPEC_CHAR,
    USER_REG_CASE_SENS,
    USER_REG_LONG_STRING,
)

## Authentication Tests ##

# Positive Cases
def test_register_positive(test_db):
    response = client.post(
        REGISTER_URL,
        json = USER_REG,
    )
    assert response.status_code == 200
    assert response.json()["email"] == "positive@example.com"


def test_login_positive(test_db):
    response = client.post(
        LOGIN_URL,
        json = USER_LOGIN,
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
        REGISTER_URL,
        json = {},
    )
    assert response.status_code == 422

def test_register_user_already_exists(test_db):
    response = client.post(
        REGISTER_URL,
        json = USER_REG,
    )
    assert response.status_code == 409

def test_register_with_invalid_email(test_db):
    response = client.post(
        REGISTER_URL,
        json = USER_REG_INV_EMAIL,
    )
    assert response.status_code == 422  # Invalid email format


def test_register_with_special_characters_in_name(test_db):
    response = client.post(
        REGISTER_URL,
        json = USER_REG_SPEC_CHAR,
    )
    assert response.status_code == 200


def test_register_identical_emails_with_different_cases(test_db):
    response1 = client.post(
        REGISTER_URL,
        json = USER_REG_CASE_SENS,
    )
    assert response1.status_code == 409


def test_login_user_not_found(test_db):
    response = client.post(
        LOGIN_URL,
        json = USER_LOGIN_NON_EXIST,
    )
    assert response.status_code == 404


def test_login_wrong_password(test_db):
    response = client.post(
        LOGIN_URL,
        json = USER_LOGIN_WRONG_PW,
    )
    assert response.status_code == 401


def test_register_with_long_values(test_db):
    response = client.post(
        REGISTER_URL,
        json = USER_REG_LONG_STRING,
    )
    assert response.status_code == 422

# def test_logout_not_logged_in():
#     # Attempt to logout when not logged in
#     response = client.post("/logout")
#     assert response.status_code == 404  
#     assert "access_token" not in response.cookies


# Edge Cases

# def test_register_edge_case_boundary_values(test_db):
#     response = client.post(
#         REGISTER_URL,
#         json={
#             "email": "boundary@example.com",
#             "first_name": "",  # Empty string
#             "middle_name": "Boundary Test Case",
#             "last_name": "B" * 255,  # Testing the max length
#             "password": "boundarypassword",
#         },
#     )
#     assert (
#         response.status_code == 422
#     )  # Assuming empty 'first_name' is invalid and 'last_name' length is validated


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


    


    

