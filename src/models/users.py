import uuid
from uuid import UUID
from pytz import timezone
from datetime import datetime, timedelta

from src.utils.db import Base
from sqlalchemy import (
    Boolean,
    Column,
    UUID,
    LargeBinary,
    PrimaryKeyConstraint,
    String,
    UniqueConstraint,
    TIMESTAMP
)
from sqlalchemy.orm import Session

UTC = timezone("UTC")
def time_now():
    return datetime.now(UTC)

class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True), nullable=False, primary_key=True, default=uuid.uuid4
    )
    created_at = Column(TIMESTAMP(timezone=True), default=time_now, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=time_now, onupdate=time_now, nullable=False)

    email = Column(String(225), nullable=False, unique=True)
    first_name = Column(String(225))
    middle_name = Column(String(225))
    last_name = Column(String(225))
    hashed_password = Column(LargeBinary, nullable=False)
    refresh_token = Column(String(225))
    access_token = Column(String(225))
    is_active = Column(Boolean, default=False)
    reset_token = Column(String(225), nullable=True)
    reset_token_expiration = Column(TIMESTAMP(timezone=True), nullable=True)

    PrimaryKeyConstraint("id", name="pk_user_id")
    UniqueConstraint("email", name="uq_user_email")

    def __repr__(self):
        """Returns string representation of model instance"""
        return "<User {first_name}>".format(first_name=self.first_name)

    def update_refresh_token(self, token):
        self.refresh_token = token

    def update_access_token(self, token):
        self.access_token = token
    
    def clear_token(self, session: Session):
        """Deactivate user as well as clear access token and refresh token upon logout"""
        self.is_active = False
        self.access_token = None
        self.refresh_token = None
        session.commit()
        return {"message": "Token cleared from user."}

    def get_is_active(self):
        return self.is_active

    def set_reset_token(self, token: str):
        self.reset_token = token
        self.reset_token_expiration = time_now() + timedelta(hours=1)

    def validate_reset_token(self, token: str):
        if self.reset_token != token or time_now() > self.reset_token_expiration:
            return False
        else:
            return True

    def update_password(self, session: Session, new_hashed_password: bytes):
        """Updates the user's hashed password and clears reset token fields."""
        self.hashed_password = new_hashed_password
        self.reset_token = None
        self.reset_token_expiration = None
        session.commit()
