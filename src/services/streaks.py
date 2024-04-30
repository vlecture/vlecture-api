import uuid
from typing import List, Optional

from fastapi import (
  Request,
)

from enum import Enum
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session

from src.models.users import User

from src.models.streaks import Streaks

from src.schemas.streaks import (
  StreaksSchema
)

from src.utils.settings import (
  OPENAI_MODEL_NAME,
  OPENAI_API_KEY,
)

from src.utils.time import get_datetime_now_jkt

class StreakDecisionEnum(str, Enum):
  CONTINUE = "CONTINUE"
  TERMINATE = "TERMINATE"
  ERROR = "ERROR"

class StreaksService:
  SECONDS_IN_HOUR = 3600

  def determine_streak_decision(
    self, 
    current_time: datetime, 
    streak_last_updated: datetime
  ) -> StreakDecisionEnum:
    if (current_time <= streak_last_updated):
      return StreakDecisionEnum.ERROR
    
    seconds_diff = (current_time - streak_last_updated).total_seconds()

    hours_diff = round(seconds_diff / self.SECONDS_IN_HOUR, 1)
    
    if (hours_diff >= 24.0):
      return StreakDecisionEnum.TERMINATE

    return StreakDecisionEnum.CONTINUE

  def save_streak_to_db(
    self,
    session: Session,
    user_id: UUID,
    time_created: datetime,
  ) -> StreaksSchema:
    streak_obj = self.create_new_streak(
      user_id=user_id,
      time_created=time_created,
    )

    try:
      session.add(streak_obj)
      session.commit()
      session.refresh(streak_obj)
    except Exception as e:
      session.rollback()
      raise RuntimeError(f"Error while creating new Streak: ${e}")
    finally:
      session.close()

    return streak_obj
  
  def create_new_streak(
    self,
    user_id: UUID,
    time_created: datetime,
  ) -> StreaksSchema:
    return StreaksSchema(
      id=uuid.uuid4(),
      created_at=time_created,
      updated_at=time_created,
      is_deleted=False,
      owner_id=user_id,
      length_days=1, # initial length_days value
      is_active=True,
    )



  
