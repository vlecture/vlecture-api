import bcrypt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse
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
from src.schemas.auth import (
  LoginSchema, 
  RegisterSchema, 
  LogoutSchema,
  UpdatePasswordSchema,
)
from src.services.users import (
    create_user,
    get_user,
    get_user_by_refresh_token,
    update_access_token,
    update_active_status,
    update_user_after_logout,
    update_refresh_token,
    get_user_by_access_token,
)
from src.services.usages import UsageService

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
    if (password_char_constraint(payload.hashed_password)):
        raise HTTPException(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY, detail="Password must be a combination of uppercase letters, lowercase letters, and numbers!"
        )
    if (password_len_constraint(payload.hashed_password)):
        raise HTTPException(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY, detail="Password must be longer than 8 characters!"
        )
    if (password_sim_constraint(payload.hashed_password, payload.first_name, payload.middle_name, payload.last_name)):
        raise HTTPException(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY, detail="Password must not be the same as your first name, middle name, or last name!"
        )
    try:
        user = get_user(session=session, email=payload.email.lower())
    except Exception:
        payload.email = payload.email.lower()
        payload.hashed_password = hash_password(payload.hashed_password)
        create_user(session=session, user=payload)
        return JSONResponse(
                status_code=HTTP_200_OK,
                content={
                    "message": "User successfully registered!"
                }
            )
    if user:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT, detail="User already exists!"
        )


def login(response: Response, session: Session, payload: LoginSchema):
    user = None
    try:
        user = get_user(session=session, email=payload.email.lower())
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

    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)
    response.set_cookie(key="access_token", value=access_token, httponly=True)

    usage_service = UsageService()
    usage = usage_service.get_current_usage(session, user.id)
    usage.renew_quota(session)
    session.refresh(usage)
    session.commit()

    update_access_token(session, user, access_token)
    update_refresh_token(session, user, refresh_token)
    update_active_status(session, user)

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
            user = get_user_by_access_token(session=session, access_token=access_token)

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
    authorization_header = request.headers.get("Authorization")
    refresh_token = authorization_header[len("Bearer "):] 
    if authorization_header is None:
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
            user = get_user_by_refresh_token(session=session, refresh_token=refresh_token)

            update_access_token(session, user, new_access_token)
            
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

        update_user_after_logout(session, user)

        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return {"message": "Logout successful."}

    except Exception:
        if user is None:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND, detail="User is not logged in!"
            )


# Helper functions

def password_sim_constraint(password: str, first_name: str, middle_name: str, last_name: str):
    password = password.decode("utf-8")
    if first_name.lower() in password.lower() or middle_name.lower() in password.lower() or last_name.lower() in password.lower():
        return True
    return False

def password_len_constraint(password: str):
    password = password.decode("utf-8")
    if len(password) < 8:
        return True
    return False

def password_char_constraint(password: str):
    password = password.decode("utf-8")
    num_of_upp = 0
    num_of_low = 0
    num_of_num = 0

    for i in password:
        if i.isupper():
            num_of_upp += 1
        if i.islower():
            num_of_low += 1
        if i.isnumeric():
            num_of_num += 1
    
    if num_of_low > 0 and num_of_num > 0 and num_of_upp > 0:
        return False

    return True


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

def update_password(session: Session, payload: UpdatePasswordSchema):
    """Updates a user's password"""
    user = get_user(session=session, email=payload.email.lower())

    if user:
        hashed_password = hash_password(payload.hashed_password)
        
        user.hashed_password = hashed_password
        session.commit()

        return user.email