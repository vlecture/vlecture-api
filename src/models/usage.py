import uuid
from uuid import UUID
from pytz import timezone
from datetime import datetime

from src.utils.db import Base
from sqlalchemy import (
    Column,
    UUID,
    TIMESTAMP,
    Integer
)
from sqlalchemy.orm import Session

UTC = timezone("UTC")
def time_now():
    return datetime.now(UTC)

class Usage(Base):
    __tablename__ = "usages"

    id = Column(
        UUID(as_uuid=True), nullable=False, primary_key=True, default=uuid.uuid4
    )
    created_at = Column(TIMESTAMP(timezone=True), default=time_now, nullable=False)

    user_id = Column(UUID(as_uuid=True), nullable=False)
    quota = Column(Integer, nullable=False, default=5)

    def update_quota(self, session: Session):
        self.quota = self.quota - 1
        session.commit()