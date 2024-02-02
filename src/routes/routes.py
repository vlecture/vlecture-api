from typing import List
from fastapi import Depends
from sqlalchemy.orm import Session
from starlette import status
from fastapi import APIRouter
from src.models.user import user
from src.utils import database

router = APIRouter(prefix="/api/v1", tags=["Users"])


@router.get("/", response_model=List[user.UserBase])
def users(db: Session = Depends(database.get_db)):
    users = db.query(user.User).all()

    return users


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=List[user.UserBase]
)
def createUser(post_user: user.UserBase, db: Session = Depends(database.get_db)):
    new_user = user.User(username=post_user.username)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return [new_user]
