from datetime import datetime

import uuid as uuid
from pytz import timezone
from typing import Any

from sqlalchemy import Column, TIMESTAMP, Boolean, Integer, create_engine
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import UUID

from src.utils.db import get_db


UTC = timezone("UTC")
def time_now():
    return datetime.now(UTC)

class DBBase:
  """
  Base Class for all DB models
  """

  id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
  created_at = Column(TIMESTAMP(timezone=True), default=time_now, nullable=False)
  updated_at = Column(TIMESTAMP(timezone=True), default=time_now, onupdate=time_now, nullable=False)
  is_deleted = Column(Boolean, default=False)

  @classmethod
  def get_by_uuid(cls, uuid: UUID) -> Any:
     db: Session = get_db()
     return db.query(cls).filter(cls.id == uuid, cls.is_deleted._is_(False)).first()
