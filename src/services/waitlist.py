
from sqlalchemy.orm import Session

from src.models.waitlist import Waitlist
from src.schemas.waitlist import WaitlistSchema
from src.utils.db import get_db


def join_waitlist(session: Session, waitlist: WaitlistSchema):
    db_waitlist = Waitlist(waitlist.email)
    session.add(db_waitlist)
    session.commit()
    session.refresh(db_waitlist)
    return db_waitlist

def email_exists(db: Session, email: str):
    return db.query(Waitlist).filter(Waitlist.email == email).first()
