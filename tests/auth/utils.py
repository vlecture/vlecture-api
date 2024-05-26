REGISTER_URL = "/v1/auth/register"
LOGIN_URL = "/v1/auth/login"
LOGOUT_URL = "/v1/auth/logout"

# CONST
LONG_STRING = "a" * 256
RANDOM_ACCESS_TOKEN = "S1ZHmoMPAjEUiDfaW8MmR2ToLGzCvb5YbmFqWKhYIJi1W7hCgiGdLa6jH9pI6C9x"

# Positive Users
USER_REG = {
    "email": "positive@example.com",
    "first_name": "Positive",
    "middle_name": "Test",
    "last_name": "Case",
    "password": "StrongPassword123"
}

USER_LOGIN = {
    "email": "positive@example.com",
    "password": "StrongPassword123"
}

USER_LOGIN_NON_EXIST = {
    "email": "nonexistent@example.com",
    "password": "any"
}

USER_LOGIN_WRONG_PW = {
    "email": "positive@example.com",
    "password": "StrongPassword12"
}

USER_REG_SPEC_CHAR = {
    "email": "specialchar@example.com",
    "first_name": "Speci@l",
    "middle_name": "@wesome",
    "last_name": "Ch@r",
    "password": "StrongPassword123"
}

USER_REG_INV_EMAIL = {
    "email": "invalidemail",
    "first_name": "Email",
    "middle_name": "Is",
    "last_name": "Invalid",
    "password": "StrongPassword123"
}

USER_REG_CASE_SENS = {
    "email": "PosiTivE@example.com",
    "first_name": "Case",
    "middle_name": "Character",
    "last_name": "Sensitive",
    "password": "StrongPassword123"
}

USER_REG_LONG_STRING = {
    "email": f"{LONG_STRING}@example.com",
    "first_name": LONG_STRING,
    "middle_name": LONG_STRING,
    "last_name": LONG_STRING,
    "password": LONG_STRING
}

USER_REG_SAME_FN = {
    "email": "firstname@example.com",
    "first_name": "FirstName",
    "middle_name": "MiddleName",
    "last_name": "LastName",
    "password": "FirstName123"
}

USER_REG_SAME_MN = {
    "email": "middlename@example.com",
    "first_name": "FirstName",
    "middle_name": "MiddleName",
    "last_name": "LastName",
    "password": "MiddleName123"
}

USER_REG_SAME_LN = {
    "email": "lastname@example.com",
    "first_name": "FirstName",
    "middle_name": "MiddleName",
    "last_name": "LastName",
    "password": "LastName123"
}

USER_REG_BOUNDARY_VAL = {
    "email": "boundary@example.com",
    "first_name": "",  # Empty string
    "middle_name": "Boundary Test Case",
    "last_name": "B" * 255,  # Testing the max length
    "password": "boundarypassword",
}