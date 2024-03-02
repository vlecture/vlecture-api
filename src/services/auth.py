from sqlalchemy.orm import Session

from src.models.users import User
from src.schemas.auth import RegisterSchema


def register(session: Session, user: RegisterSchema):
    db_user = User(**user.model_dump())
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
