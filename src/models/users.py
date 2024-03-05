import uuid
import bcrypt
from datetime import datetime, timedelta, timezone
from jose import jwt
from src.utils.db import Base
from src.utils.settings import REFRESH_TOKEN_SECRET, ACCESS_TOKEN_SECRET
from sqlalchemy import (
    Boolean,
    Column,
    UUID,
    LargeBinary,
    PrimaryKeyConstraint,
    String,
    UniqueConstraint,
)


class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True), nullable=False, primary_key=True, default=uuid.uuid4
    )
    email = Column(String(225), nullable=False, unique=True)
    first_name = Column(String(225))
    middle_name = Column(String(225))
    last_name = Column(String(225))
    hashed_password = Column(LargeBinary, nullable=False)
    refresh_token = Column(String(225))
    access_token = Column(String(225))
    is_active = Column(Boolean, default=False)

    UniqueConstraint("email", name="uq_user_email")
    PrimaryKeyConstraint("id", name="pk_user_id")

    def __repr__(self):
        """Returns string representation of model instance"""
        return "<User {first_name}>".format(first_name=self.first_name)

    @staticmethod
    def hash_password(password: bytes) -> bytes:
        """Transforms password from it's raw textual form to
        cryptographic hashes
        """
        return bcrypt.hashpw(password, bcrypt.gensalt())

    def validate_password(self, password: str) -> bool:
        """Confirms password validity"""
        return bcrypt.checkpw(password.encode(), self.hashed_password)

    def generate_token(self):
        """Generate access token and refresh token for user"""
        refresh_token = jwt.encode(
            {
                "first_name": self.first_name,
                "email": self.email,
                "exp": datetime.now(timezone.utc) + timedelta(days=7),
            },
            REFRESH_TOKEN_SECRET,
        )
        access_token = jwt.encode(
            {
                "first_name": self.first_name,
                "email": self.email,
                "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
            },
            ACCESS_TOKEN_SECRET,
        )
        self.refresh_token = refresh_token
        self.access_token = access_token
        return {
            "refresh_token": refresh_token,
            "access_token": access_token,
        }
    
    def is_active(self):
        return self.is_active
    
    def clear_token(self):
        """Deactivate user as well as clear access token and refresh token upon logout"""
        self.is_active = False
        self.access_token = None
        self.refresh_token = None
        return {"message": "Token cleared from user."}
