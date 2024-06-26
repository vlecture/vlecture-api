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

class Transcription(Base):
  __tablename__ = "transcriptions"

  id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
  created_at = Column(TIMESTAMP(timezone=True), default=get_datetime_now_jkt, nullable=False)
  updated_at = Column(TIMESTAMP(timezone=True), default=get_datetime_now_jkt, onupdate=get_datetime_now_jkt, nullable=False)
  is_deleted = Column(Boolean, default=False, nullable=False)

  ## Foreign Relationships
  # Foreign key to User
  owner_id = Column(UUID, ForeignKey(User.id), nullable=False)
  
  # NOTE in case User gets a `transcriptions` field
  # owner = relationship("User", back_populates="transcriptions")
  
  title = Column(String(255), nullable=False, unique=False)
  
  tags = Column(ARRAY(String), nullable=True, unique=False)

  chunks = relationship("TranscriptionChunk", back_populates="transcription_parent")

  duration = Column(Float(precision=1), default=0, nullable=False)

  # Current use case: "id" | "en", future use case: "id-ID" | ...
  language = Column(String(10), nullable=False)

  @classmethod
  def get_by_id(cls, uuid: UUID) -> TranscriptionSchema:
    base = super().get_by_id(uuid)
    return base.__to_model() if base else None
  
  def __str__(self):
    return f"""
      Transcription\n
      ===
      id: {self.id}\n
      title: {self.title}
    """


class TranscriptionChunk(Base):
  __tablename__ = "transcription_chunks"

  id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
  created_at = Column(TIMESTAMP(timezone=True), default=get_datetime_now_jkt, nullable=False)
  updated_at = Column(TIMESTAMP(timezone=True), default=get_datetime_now_jkt, onupdate=get_datetime_now_jkt, nullable=False)
  is_deleted = Column(Boolean, default=False)

  # Extra fields
  duration = Column(Float(precision=1),nullable=False)

  is_edited = Column(Boolean, default=False)

  ## Foreign Relationships
  # Foreign key to Transcription
  transcription_id = Column(UUID, ForeignKey(Transcription.id), nullable=False)

  # One to many relationship with Transcription
  transcription_parent = relationship("Transcription", back_populates="chunks")

  start_time = Column(Float(precision=1), nullable=False)
  end_time = Column(Float(precision=1), nullable=False)

  content = Column(String(255), nullable=False)

  def __str__(self):
    return f"""
    Transcription Chunk\n
    ===
    id: {self.id}\n
    content: {self.content}
    """

  @classmethod
  def get_by_id(cls, uuid: UUID) -> TranscriptionChunksSchema:
    base = super().get_by_id(uuid)
    return base.__to_model() if base else None

  

  