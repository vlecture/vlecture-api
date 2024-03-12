import uuid
from datetime import datetime, timedelta
from pytz import timezone
from src.utils.settings import OTP_LIFESPAN_SEC
from src.utils.db import Base
from sqlalchemy import (
    Boolean,
    Column,
    UUID,
    TIMESTAMP,
    LargeBinary,
    PrimaryKeyConstraint,
    String,
    UniqueConstraint,
)

UTC = timezone("UTC")


def time_now():
    return datetime.now(UTC)

def time_expiry():
   return datetime.now(UTC) + timedelta(seconds=int(OTP_LIFESPAN_SEC))

class OTP(Base):
  __tablename__ = "otps"

  id = Column(
          UUID(as_uuid=True), nullable=False, primary_key=True, default=uuid.uuid4
  )

  email = Column(String(225), nullable=False, unique=True)
  token = Column(String(6), nullable=False)
  created_at = Column(TIMESTAMP(timezone=True), default=time_now, nullable=False)
  expires_at = Column(TIMESTAMP(timezone=True), default=time_expiry, nullable=False)

  def __str__(self):
     return f"id: {self.id}\nemail: {self.email}\ntoken: {self.token}\ncreated_at: {self.created_at}\nexpires_at: {self.expires_at}\n"


