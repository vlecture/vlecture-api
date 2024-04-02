from sqlalchemy.orm import Session
from src.models.waitlist import Waitlist
from src.schemas.waitlist import WaitlistSchema


def email_exists(db: Session, email: str):
    return db.query(Waitlist).filter(Waitlist.email == email).first()


def join_waitlist(db: Session, waitlist: WaitlistSchema):
    email = waitlist.email

    # Check if the email already exists in the waitlist
    if email_exists(db, email):
        return False
    else:
        # Create a new Waitlist instance
        db_waitlist = Waitlist(email=email)
        db.add(db_waitlist)
        db.commit()
        db.refresh(db_waitlist)
        return True
