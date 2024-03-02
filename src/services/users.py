from sqlalchemy.orm import Session

from src.models.users import User


def get_user(session: Session, email: str):
    return session.query(User).filter(User.email == email).one()
