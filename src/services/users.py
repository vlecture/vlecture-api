from sqlalchemy.orm import Session

from src.models.users import User
from src.schemas.auth import RegisterSchema


def create_user(session: Session, user: RegisterSchema):
    db_user = User(**user.model_dump())
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

def get_user(session: Session, email: str):
    return session.query(User).filter(User.email == email).one()

def get_user_by_access_token(session: Session, access_token:str):
    return session.query(User).filter(User.access_token == access_token).one()

def update_tokens(session: Session, user, access_token: str, refresh_token: str):
    user.access_token = access_token
    user.refresh_token = refresh_token
    user.is_active = True
    session.commit()
