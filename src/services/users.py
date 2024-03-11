from sqlalchemy.orm import Session
from src.exceptions.users import InvalidFieldName

from src.models.users import User
from src.schemas.auth import RegisterSchema


def create_user(session: Session, user: RegisterSchema):
    db_user = User(**user.model_dump())
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user(session: Session, field: str, value: str):
    fields = [
        "email",
        "first_name",
        "middle_name",
        "last_name",
        "hashed_password",
        "is_active",
        "access_token",
        "refresh_token",
    ]
    if field not in fields:
        raise InvalidFieldName("Invalid field name provided")
    return session.query(User).filter(getattr(User, field) == value).one()


def update_refresh_token(session: Session, user, refresh_token: str):
    user.refresh_token = refresh_token
    user.is_active = True
    session.commit()


def update_access_token(session: Session, user, access_token: str):
    user.access_token = access_token
    session.commit()


def update_active_status(session: Session, user):
    user.is_active = not user.is_active
    session.commit()
