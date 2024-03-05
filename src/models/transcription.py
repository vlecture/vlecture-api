import uuid
from datetime import datetime, timedelta, timezone
from __future__ import annotations
from typing import List

from src.utils.db import Base
from src.models.base import DBBase
from src.models.users import User
from src.schemas.transcription import TranscriptionSchema, TranscriptionChunksSchema
from src.utils.settings import REFRESH_TOKEN_SECRET, ACCESS_TOKEN_SECRET


from sqlalchemy import (
    Column,
    UUID,
    Integer,
    String,
    Float,
    Boolean,
    LargeBinary,
    PrimaryKeyConstraint,
    DateTime,
    UniqueConstraint,
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

class Transcription(Base):
  __tablename__ = "transcription"

  ## Foreign Relationships
  # Foreign key to User
  owner_id = Column(UUID, ForeignKey(User.id), nullable=False)
  
  # NOTE in case User gets a `transcriptions` field
  # owner = relationship("User", back_populates="transcriptions")
  
  title = Column(String(255), nullable=False, unique=False)
  
  tags = Column(ARRAY(String), nullable=True, unique=False)

  chunks = relationship("TranscriptionChunk", back_populates="transcription_parent")

  duration = Column(Float(precision=1), default=0, nullable=False)

  def __to_model(self) -> TranscriptionSchema:
    """ Converts DB ORM object to Pydantic Model ('schema') """
    return TranscriptionSchema.model_validate(self)
  
  @classmethod
  def get_by_id(cls, uuid: UUID) -> TranscriptionSchema:
    base = super().get_by_id(uuid)
    return base.__to_model() if base else None


class TranscriptionChunk(Base, DBBase):
  __tablename__ = "transcription_chunk"

  # Extra fields
  duration = Column(Float(precision=1), default=0, nullable=False)

  is_edited = Column(Boolean, default=False)

  ## Foreign Relationships
  # Foreign key to Transcription
  transcription_id = Column(UUID, ForeignKey(Transcription.id), nullable=False)

  # One to many relationship with Transcription
  transcription_parent = relationship("Transcription", back_populates="chunks")

  def __to_model(self) -> TranscriptionChunksSchema:
    """ Converts DB ORM object to Pydantic Model ('schema') """
    return TranscriptionChunksSchema.model_validate(self)
  
  @classmethod
  def get_by_id(cls, uuid: UUID) -> TranscriptionChunksSchema:
    base = super().get_by_id(uuid)
    return base.__to_model() if base else None

  

  