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

from utils.time import get_datetime_now_jkt

class Streaks(Base):
  __tablename__ = "streaks"

  id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4(), unique=True)
  owner_id = Column(UUID, ForeignKey(User.id), nullable=False)
  
  created_at = Column(TIMESTAMP(timezone=True), default=get_datetime_now_jkt, nullable=False)
  updated_at = Column(TIMESTAMP(timezone=True), default=get_datetime_now_jkt, onupdate=get_datetime_now_jkt, nullable=False)
  is_deleted = Column(Boolean, default=False, nullable=False)

  length_days = Column(Integer, default=0, nullable=False)
  is_active = Column(Boolean, default=True, nullable=False)

  started_at = Column(TIMESTAMP(timezone=True), default=get_datetime_now_jkt, nullable=False)

  # Each streak update, also update ended_at to eliminate the need to create regular CRON jobs -- refer to the last updated moment instead!
  ended_at = Column(TIMESTAMP(timezone=True), default=get_datetime_now_jkt, nullable=False)






