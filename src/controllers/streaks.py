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

from typing import (
  List
)

from bson.objectid import ObjectId

from src.models.users import User

from src.schemas.streaks import (
  # OBJECTS
  StreaksSchema
)

 
from src.services.users import get_current_user

from src.services.note import (
  NoteService
)

class StreaksRouterTags(Enum):
  streaks = "streaks"

streaks_router = APIRouter(
  prefix="/v1/streaks",
  tags=[StreaksRouterTags],
)

@streaks_router.post(
  "/create",
  response_description="Create or Update an existing Flashcard Streak",
  status_code=http.HTTPStatus.OK,
)
def update_streak(
  request: Request,
  payload = Body(),
  user: User = Depends(get_current_user),
):
  # Ensure user logged in and fetch user

  # Fetch the only active streak

  # Determine whether streak id continued or broken

  # If is broken, then set is_active to false, and create a brand new streak!

  # If not broken, update existing streak

  
  pass