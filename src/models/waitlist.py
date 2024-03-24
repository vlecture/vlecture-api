from pytz import timezone
from sqlalchemy import TIMESTAMP, Column, String, Boolean
from datetime import datetime
from pytz import timezone
from src.utils.db import Base

UTC = timezone("UTC")


def time_now():
    return datetime.now(UTC)


class Waitlist(Base):
    __tablename__ = "waitlist"

    email = Column(String(225), nullable=False, unique=True, primary_key=True)
    date_waitlist = Column(TIMESTAMP(timezone=True),
                           default=time_now, nullable=False)
    is_sent = Column(Boolean, default=False, nullable=False)
    date_sent = Column(TIMESTAMP(timezone=True),
                       default=None)

    def __init__(self, email: str, is_sent: bool = False, date_sent: datetime = None):
        self.email = email
        self.is_sent = is_sent
        self.date_sent = date_sent
