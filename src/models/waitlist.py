import datetime
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Waitlist(Base):
    __tablename__ = "waitlist"

    email = Column(String(225), nullable=False, unique=True)
    date_waitlist = Column(DateTime, default=func.now())
    is_sent = Column(Boolean, default=False)
    date_sent = Column(DateTime)

    def __init__(self, email: str, date_waitlist: datetime, is_sent: bool = False, date_sent: datetime = None):
        self.email = email
        self.date_waitlist = date_waitlist
        self.is_sent = is_sent
        self.date_sent = date_sent
