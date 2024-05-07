from enum import Enum
import http
from datetime import datetime
import pytz

from fastapi import (
    APIRouter,
    Request,
    Response,
    Depends,
    Body,
)

from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from typing import (
  List
)

from bson.objectid import ObjectId

from src.models.users import User

from src.schemas.streaks import (
  # OBJECTS
  StreaksSchema
)
from src.utils.db import get_db
 
from src.services.users import get_current_user

from src.services.streaks import (
  StreaksService,
  StreakDecisionEnum
)

from src.utils.time import get_datetime_now_jkt

class StreaksRouterTags(Enum):
  streaks = "streaks"

streaks_router = APIRouter(
  prefix="/v1/streaks",
  tags=[StreaksRouterTags.streaks],
)

@streaks_router.post(
  "/check",
  response_description="Create or Update an existing Flashcard Streak",
  status_code=http.HTTPStatus.OK,
)
def check_streak(
  # request: Request,
  # payload = Body(),
  session: Session = Depends(get_db),
  user: User = Depends(get_current_user),
):
  service = StreaksService()
  current_time = get_datetime_now_jkt()

  # Fetch the only active streak
  latest_streak = service.fetch_latest_streak(
    session=session,
    user_id=user.id,
  )

  if not latest_streak:
    new_streak_obj = service.create_streak_and_store_db(
      session=session,
      user_id=user.id,
      time_created=current_time,
    )

    return JSONResponse(
      status_code=http.HTTPStatus.CREATED,
      content=jsonable_encoder(new_streak_obj),
    )

  # Determine whether streak is continued or broken
  streak_decision = service.determine_streak_decision(
    current_time=current_time,
    streak_last_updated=latest_streak.updated_at
  )

  if streak_decision == StreakDecisionEnum.ERROR:
    return JSONResponse(
      status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
      content="Error while determining streak decision."
    )

  # If streak is broken, then set is_active to false, 
  # and create a brand new streak!
  if streak_decision == StreakDecisionEnum.TERMINATE:
    service.make_streak_inactive(
      streak=latest_streak,
      session=session,
    )

    new_streak_obj = service.create_streak_and_store_db(
      session=session,
      user_id=user.id,
      time_created=current_time,
    )

    return JSONResponse(
      status_code=http.HTTPStatus.CREATED,
      content=jsonable_encoder(new_streak_obj),
    )
  

  # If streak continues, update existing streak
  is_streak_length_updated = service.update_streak_length(
    streak=latest_streak,
    time_updated=current_time,
    session=session,
  )

  if not is_streak_length_updated:
    return JSONResponse(
      status_code=http.HTTPStatus.OK,
      content="Streak length is not incremented."
    )
  
  return JSONResponse(
    status_code=http.HTTPStatus.OK,
    content="Streak continues and is incremented!"
  )

@streaks_router.get(
  "/all",
  response_description="Fetch all the user's Flashcard Streak",
  status_code=http.HTTPStatus.OK,
)
def fetch_all_streak(
  session: Session = Depends(get_db),
  user: User = Depends(get_current_user),
):
  service = StreaksService()
  
  all_streaks = service.fetch_all_my_streak(session=session, user_id=user.id)
  
  if not all_streaks:
    return JSONResponse(
      status_code=http.HTTPStatus.NOT_FOUND,
      content="No streaks found for user"
    )
  
  return JSONResponse(
    status_code=http.HTTPStatus.OK,
    content=jsonable_encoder(all_streaks)
  )
  