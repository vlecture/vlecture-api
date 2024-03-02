from fastapi import HTTPException
from sqlalchemy.orm import Session

from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
)
from src.models.users import User
from src.schemas.auth import LoginSchema, RegisterSchema
from src.services.users import get_user


def register(session: Session, payload: RegisterSchema):
    user = None
    if (
        len(payload.email) == 0
        or len(payload.first_name) == 0
        or (payload.last_name) == 0
        or (payload.hashed_password) == 0
    ):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="All required fields must be filled!",
        )
    try:
        user = get_user(session=session, email=payload.email)
    except Exception:
        payload.hashed_password = User.hash_password(payload.hashed_password)
        db_user = User(**payload.model_dump())
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user
    if user:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT, detail="User already exists!"
        )


def login(session: Session, payload: LoginSchema):
    user = None
    try:
        user = get_user(session=session, email=payload.email)
    except Exception:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found!")
    is_validated: bool = user.validate_password(payload.password)
    if not is_validated:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid user credentials",
        )

    return user.generate_token()
