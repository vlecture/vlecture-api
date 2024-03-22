from fastapi import (
    APIRouter,
    Depends,
    Body,
    HTTPException,
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
def join_waitlist(payload: WaitlistSchema, session: Session = Depends(get_db)):

    if waitlist.join_waitlist(session, payload):
        return {"message": "Joined waitlist successfully"}
    else:
        raise HTTPException(
            status_code=400, detail="Email already exists in the waitlist")
