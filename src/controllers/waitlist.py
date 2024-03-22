import http
from fastapi import (
    APIRouter,
    Depends,
    Body,
)
from sqlalchemy import Enum
from sqlalchemy.orm import Session

from src.utils.db import get_db
from src.schemas.waitlist import WaitlistSchema


from src.services import waitlist


class WaitlistRouterTags(Enum):
    waitlist = "waitlist"


waitlist_router = APIRouter(prefix="/v1/waitlist",
                            tags=[WaitlistRouterTags.waitlist])


@waitlist_router.post("/", tags=[WaitlistRouterTags.waitlist])
def join_waitlist(payload: WaitlistSchema = Body(), session: Session = Depends(get_db)):
    email = payload.email
    return waitlist.join_waitlist(session, payload=payload)

# @router.post("/join_waitlist/")
# async def join_waitlist(wl_req: WaitlistRegistrationRequest, db: Session = Depends(get_db)):
#     email = wl_req.email

#     # Check if the email already exists in the waitlist
#     if email_exists(db, email):
#         raise HTTPException(status_code=400, detail="Email already exists in the waitlist")

#     # If email doesn't exist, add it to the waitlist
#     join_waitlist(db, email)

#     return {"message": "Joined waitlist successfully"}
