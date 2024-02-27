import uuid
import bcrypt
from datetime import datetime, timedelta, timezone
from src.utils.db import Base
from src.utils.settings import REFRESH_TOKEN_SECRET, ACCESS_TOKEN_SECRET
from sqlalchemy import (
    Boolean,
    Column,
    UUID,
    ARRAY,
    LargeBinary,
    PrimaryKeyConstraint,
    String,
    Float,
    DATETIME,
    UniqueConstraint,
    ForeignKey,
)

from __future__ import annotations
from typing import List

from sqlalchemy.orm import (
  Mapped,
  mapped_column,
  DeclarativeBase,
  relationship
)

class TranscriptionChunk(Base):
  __tablename__ = "transcription_chunk"

  id = mapped_column(
    "id",
    UUID(as_uuid=True),
    nullable = False,
    primary_key = True,
    default = uuid.uuid4
  )

  transcription_id = mapped_column(ForeignKey("transcription.id"))

  transcription_parent = relationship("Transcription", back_populates="chunks")

  duration = mapped_column(Float, nullable=False, default = 0) 

  created_at = mapped_column(DATETIME, nullable=False, default = datetime.now())

  updated_at = mapped_column(DATETIME, nullable=False, default = datetime.now())

  is_edited = mapped_column(Boolean, nullable=False, default = False)

  
  

class Transcription(Base):
  __tablename__ = "transcription"
  
  id = mapped_column(
    "id",
    UUID(as_uuid=True),
    nullable = False,
    primary_key = True,
    default = uuid.uuid4
  )

  title = mapped_column(String(255), nullable=False, unique=False)

  tags = mapped_column(ARRAY(String), nullable=True)

  chunks = relationship("TranscriptionChunk", back_populates="transcription_parent")

  duration = mapped_column(Float, nullable=False, default = 0) 

  created_at = mapped_column(DATETIME, nullable=False, default = datetime.now())

  updated_at = mapped_column(DATETIME, nullable=False, default = datetime.now())

  