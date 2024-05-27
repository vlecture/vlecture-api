from tests.utils.test_db import client, test_db
from tests.auth.utils import (
    REGISTER_URL,
    LOGIN_URL,
    LOGOUT_URL,
    USER_REG,
    USER_LOGIN,
    USER_LOGIN_NON_EXIST,
    USER_LOGIN_WRONG_PW,
    USER_REG_INV_EMAIL,
    USER_REG_SPEC_CHAR,
    USER_REG_CASE_SENS,
    USER_REG_LONG_STRING,
    USER_REG_SAME_FN,
    USER_REG_SAME_MN,
    USER_REG_SAME_LN,
    USER_REG_BOUNDARY_VAL,
    RANDOM_ACCESS_TOKEN,
)

## Authentication Tests ##

# Positive Cases
def test_register_positive(test_db):
    response = client.post(
        REGISTER_URL,
        json = USER_REG,
    )
    assert response.status_code == 200
    # assert response.json()["email"] == "positive@example.com"


def test_login_positive(test_db):
    response = client.post(
        LOGIN_URL,
        json = USER_LOGIN,
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()

def test_logout_successful(test_db):
    # Login
    login_response = client.post(
        LOGIN_URL,
        json = USER_LOGIN,
    )

    # Logout
    response = client.post(
        LOGOUT_URL,
        json = {
            "access_token": login_response.json()["access_token"]
        }
    )

    assert response.status_code == 200
    assert "access_token" not in response.cookies

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

def test_register_with_pw_similar_with_fn(test_db):
    response = client.post(
        REGISTER_URL,
        json = USER_REG_SAME_FN,
    )
    assert response.status_code == 422

def test_register_with_pw_similar_with_mn(test_db):
    response = client.post(
        REGISTER_URL,
        json = USER_REG_SAME_MN,
    )
    assert response.status_code == 422

def test_register_with_pw_similar_with_ln(test_db):
    response = client.post(
        REGISTER_URL,
        json = USER_REG_SAME_LN,
    )
    assert response.status_code == 422

def test_logout_not_logged_in(test_db):
    response = client.post(
        LOGOUT_URL,
        json = {
            "access_token": RANDOM_ACCESS_TOKEN,
        }
    )

    assert response.status_code == 404  
    assert "access_token" not in response.cookies

# Edge Cases

def test_register_edge_case_boundary_values(test_db):
    response = client.post(
        REGISTER_URL,
        json = USER_REG_BOUNDARY_VAL,
    )
    assert response.status_code == 422

def test_logout_twice(test_db):
    # Login
    login_response = client.post(
        LOGIN_URL,
        json = USER_LOGIN,
    )

    # Logout once
    response = client.post(
        LOGOUT_URL,
        json = {
            "access_token": login_response.json()["access_token"]
        }
    )
    assert response.status_code == 200

    # Attempt to logout again
    response = client.post(
        LOGOUT_URL,
        json = {
            "access_token": login_response.json()["access_token"]
        }
    )
    assert response.status_code == 404