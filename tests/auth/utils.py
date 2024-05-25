REGISTER_URL = "/v1/auth/register"
LOGIN_URL = "/v1/auth/login"

# CONST
LONG_STRING = "a" * 256

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
},