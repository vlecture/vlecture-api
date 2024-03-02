from sqlalchemy.orm import Session

from src.models.users import User
from src.schemas.users import CreateUserSchema


def register(session: Session, user: CreateUserSchema):
    db_user = User(**user.model_dump())
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
