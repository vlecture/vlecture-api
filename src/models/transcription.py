import uuid
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
    DateTime,
    UniqueConstraint,
    ForeignKey,
)

from sqlalchemy.sql import func

from sqlalchemy.orm import (
  Mapped,
  mapped_column,
  DeclarativeBase,
  relationship,
)

from __future__ import annotations
from typing import List


class TranscriptionChunk(Base):
  __tablename__ = "transcription_chunk"

  id: Mapped[UUID] = mapped_column(
    "id",
    UUID(as_uuid=True),
    nullable = False,
    primary_key = True,
    default = uuid.uuid4
  )

  transcription_id: Mapped[UUID] = mapped_column(ForeignKey("transcription.id"))

  transcription_parent: Mapped["Transcription"] = relationship("Transcription", back_populates="chunks")

  duration: Mapped[float] = mapped_column(Float, min=0, nullable=False, default=0) 

  created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), server_default=func.now()
  )

  updated_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), server_default=func.now()
  )

  is_edited: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

  
  

class Transcription(Base):
  __tablename__ = "transcription"
  
  id: Mapped[UUID] = mapped_column(
    "id",
    UUID(as_uuid=True),
    nullable = False,
    primary_key = True,
    default = uuid.uuid4
  )

  title: Mapped[String] = mapped_column(String(255), nullable=False, unique=False)

  tags: Mapped[ARRAY] = mapped_column(ARRAY(String), nullable=True)

  chunk: Mapped[List["TranscriptionChunk"]] = relationship("TranscriptionChunk", back_populates="transcription_parent")

  duration: Mapped[Float] = mapped_column(Float, nullable=False, default = 0) 

  created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), server_default=func.now()
  )

  updated_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), server_default=func.now()
  )

  