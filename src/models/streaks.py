import uuid
from pytz import timezone
from datetime import datetime

from src.utils.db import Base
from src.models.base import DBBase
from src.models.users import User
from src.schemas.transcription import TranscriptionSchema, TranscriptionChunksSchema

from sqlalchemy import (
    Column,
    UUID,
    TIMESTAMP,
    Integer,
    String,
    Float,
    Boolean,
    ForeignKey,
)

from sqlalchemy.dialects.postgresql import ARRAY

from sqlalchemy.sql import func

from sqlalchemy.orm import (
  Mapped,
  mapped_column,
  DeclarativeBase,
  relationship,
)

from src.utils.time import get_datetime_now_jkt

class Streaks(Base):
  __tablename__ = "streaks"

  id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4(), unique=True)
  owner_id = Column(UUID, ForeignKey(User.id), nullable=False)
  
  is_deleted = Column(Boolean, default=False, nullable=False)

  length_days = Column(Integer, default=1, nullable=False)
  is_active = Column(Boolean, default=True, nullable=False)

  # Each streak update, also update updated_at to eliminate the need to create regular CRON jobs -- refer to the last updated moment instead!
  created_at = Column(TIMESTAMP(timezone=True), default=get_datetime_now_jkt, nullable=False)
  updated_at = Column(TIMESTAMP(timezone=True), default=get_datetime_now_jkt, nullable=False)



