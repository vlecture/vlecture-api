from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from src.models.users import User
from src.schemas.auth import RegisterSchema
from src.utils.db import get_db
from starlette.status import HTTP_401_UNAUTHORIZED


def create_user(session: Session, user: RegisterSchema):
    db_user = User(**user.model_dump())
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user(session: Session, email: str):
    return session.query(User).filter(User.email == email).one()


def update_tokens(session: Session, user, access_token: str, refresh_token: str):
    user.access_token = access_token
    user.refresh_token = refresh_token
    user.is_active = True
    session.commit()


def get_current_user(request: Request, session: Session = Depends(get_db)):
    access_token = request.cookies.get("access_token")
    if access_token:
        user = session.query(User).filter(
            User.access_token == access_token).first()
        if user:
            return user
    raise HTTPException(
        status_code=HTTP_401_UNAUTHORIZED, detail="Not authenticated"
    )
