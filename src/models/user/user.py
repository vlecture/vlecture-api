from src.utils.database import Base
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, TIMESTAMP, text


class UserBase(BaseModel):
    username: str

    class Config:
        orm_mode = True


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
