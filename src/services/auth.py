import bcrypt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Request, Response
from sqlalchemy.orm import Session
from jose import jwt
from src.utils.settings import REFRESH_TOKEN_SECRET, ACCESS_TOKEN_SECRET

from starlette.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_422_UNPROCESSABLE_ENTITY,
)
from src.models.users import User
from src.schemas.auth import LoginSchema, RegisterSchema
from src.services.users import create_user, get_user, update_tokens


def register(session: Session, payload: RegisterSchema):
    user = None
    if (
        len(payload.email) == 0
        or len(payload.first_name) == 0
        or (payload.last_name) == 0
        or (payload.hashed_password) == 0
    ):
        raise HTTPException(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            detail="All required fields must be filled!",
        )
    try:
        user = get_user(session=session, email=payload.email.lower())
    except Exception:
        payload.email = payload.email.lower()
        payload.hashed_password = hash_password(payload.hashed_password)
        return create_user(session=session, user=payload)
    if user:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT, detail="User already exists!"
        )


def login(response: Response, session: Session, payload: LoginSchema):
    user = None
    try:
        user = get_user(session=session, email=payload.email)
    except Exception:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found!")
    is_validated: bool = validate_password(user, payload.password)
    if not is_validated:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid user credentials",
        )
    refresh_token = generate_refresh_token(user)
    access_token = generate_access_token(user)

    update_tokens(session, user, access_token, refresh_token)

    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)
    response.set_cookie(key="access_token", value=access_token, httponly=True)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


def renew_access_token(request: Request):
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token is None:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Unauthorized. Refresh token not provided!",
        )
    try:
        decoded_refresh_token = jwt.decode(refresh_token, REFRESH_TOKEN_SECRET)
        new_access_token = jwt.encode(
            {
                "first_name": decoded_refresh_token.first_name,
                "email": decoded_refresh_token.email,
                "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
            },
            ACCESS_TOKEN_SECRET,
        )
    except Exception:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Unauthorized. Invalid refresh token!",
        )


# Helper functions


def hash_password(password: bytes) -> bytes:
    """Transforms password from it's raw textual form to
    cryptographic hashes
    """
    return bcrypt.hashpw(password, bcrypt.gensalt())


def validate_password(user: User, password: str) -> bool:
    """Confirms password validity"""
    return bcrypt.checkpw(password.encode(), user.hashed_password)


def generate_refresh_token(user: User):
    """Generate refresh token for user"""
    refresh_token = jwt.encode(
        {
            "first_name": user.first_name,
            "email": user.email,
            "exp": datetime.now(timezone.utc) + timedelta(days=7),
        },
        REFRESH_TOKEN_SECRET,
    )
    return refresh_token


def generate_access_token(user: User):
    """Generate access token for user"""
    access_token = jwt.encode(
        {
            "first_name": user.first_name,
            "email": user.email,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
        },
        ACCESS_TOKEN_SECRET,
    )
    return access_token
