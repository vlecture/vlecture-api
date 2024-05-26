import bcrypt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Request, Response
from sqlalchemy.orm import Session
from jose import jwt
from src.exceptions.users import InvalidFieldName
from src.utils.settings import REFRESH_TOKEN_SECRET, ACCESS_TOKEN_SECRET

from starlette.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_422_UNPROCESSABLE_ENTITY,
)
from src.models.users import User
from src.schemas.auth import LoginSchema, RegisterSchema, LogoutSchema
from src.services.users import (
    create_user,
    get_user,
    update_access_token,
    update_active_status,
    update_refresh_token,
    get_user_by_access_token,
)


def register(session: Session, payload: RegisterSchema):
    user = None
    if (
        len(payload.email) == 0
        or len(payload.first_name) == 0
        # NOTE - should this be len() == 0?
        or (payload.last_name) == 0
        or (payload.hashed_password) == 0
    ):
        raise HTTPException(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            detail="All required fields must be filled!",
        )
    try:
        user = get_user(session=session, field="email", value=payload.email.lower())
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
        user = get_user(session=session, field="email", value=payload.email.lower())
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

    update_access_token(session, user, access_token)
    update_refresh_token(session, user, refresh_token)
    update_active_status(session, user)

    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)
    response.set_cookie(key="access_token", value=access_token, httponly=True)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


def verify_access_token(request: Request, session: Session):
    access_token = request.cookies.get("access_token")
    if access_token is None:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Unauthorized. Token not provided!",
        )
    try:
        decoded_access_token = jwt.decode(access_token, ACCESS_TOKEN_SECRET)
        try:
            user = get_user(session=session, field="access_token", value=access_token)

            if int(datetime.now(timezone.utc).timestamp()) > decoded_access_token.get(
                "exp"
            ):
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Unauthorized. Token expired!",
                )
            else:
                return {
                    "status_code": HTTP_200_OK,
                    "content": "Access token authorized!",
                }
        except InvalidFieldName as e:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e)) from e
        except Exception as e:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND, detail="User not found!"
            ) from e
    except Exception:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Unauthorized. Invalid access token!",
        )


def renew_access_token(request: Request, response: Response, session: Session):
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
                "first_name": decoded_refresh_token.get("first_name"),
                "email": decoded_refresh_token.get("email"),
                "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
            },
            ACCESS_TOKEN_SECRET,
        )
        try:
            user = get_user(session=session, field="refresh_token", value=refresh_token)

            update_access_token(session, user, new_access_token)
            response.set_cookie(
                key="access_token", value=new_access_token, httponly=True
            )
            return new_access_token
        except InvalidFieldName as e:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e)) from e
        except Exception as e:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND, detail="User not found!"
            ) from e
    except Exception:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Unauthorized. Invalid refresh token!",
        )


def logout(response: Response, session: Session, payload: LogoutSchema):
    user = None
    try:
        user = get_user_by_access_token(
            session=session, access_token=payload.access_token
        )
        is_active: bool = user.get_is_active()
        if not is_active:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND, detail="User is not logged in!"
            )

        user.clear_token(session)
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return {"message": "Logout successful."}

    except Exception:
        if user is None:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND, detail="User is not logged in!"
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

def update_password(session: Session, user: User, payload: RegisterSchema):
    """Updates a user's password"""
    hashed_password = hash_password(payload.hashed_password)
    
    user.hashed_password = hashed_password
    session.commit()