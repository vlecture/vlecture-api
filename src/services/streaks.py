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

  def update_streak_length(
    self,
    streak: Streaks,
    user_id: UUID,
    session: Session,
    time_updated: datetime,
  ) -> bool:
    # Update updated_at and length_days (if needed)
    self.sync_streak_updated_at(streak=streak, time_updated=time_updated, session=session)

    is_increment_length = self.check_if_increment_length(streak=streak, time_updated=time_updated)

    if not is_increment_length:
      return False
    
    # Else, also update streak length
    streak_length_incremented = self.increment_streak_length(
      streak=streak,
      time_updated=time_updated,
      session=session
    )

    if streak_length_incremented:
      print("Streak length is incremented!")
    else:
      print("Streak length stays the same.")

    return True

  def sync_streak_updated_at(
    self, 
    streak: Streaks, 
    time_updated: datetime, 
    session: Session
  ):
    streak.updated_at = time_updated
    session.commit()

  def check_if_increment_length(
    self,
    streak: Streaks,
    time_updated: datetime,
  ) -> bool:
    # We're assuming that all streaks that gets passed in are active streaks
    streak_created_at = streak.created_at
    
    if not streak.is_active:
      return False

    if not streak_created_at:
      return False
    
    if streak_created_at > time_updated:
      return False
    
    new_streak_length_days = self.calc_new_streak_length_days(
      time_updated=time_updated, 
      streak_created_at=streak_created_at
    )

    if new_streak_length_days > streak.length_days:
      return True
    
    return False
  
  def increment_streak_length(
    self,
    streak: Streaks,
    time_updated: datetime,
    session: Session,
  ) -> bool:
    streak_created_at = streak.created_at
    new_streak_length_days = self.calc_new_streak_length_days(
      time_updated=time_updated, 
      streak_created_at=streak_created_at
    )

    if new_streak_length_days > streak.length_days:
      streak.length_days = new_streak_length_days
      session.commit()
      return True
    
    return False

  def calc_new_streak_length_days(
    self,
    time_updated: datetime,
    streak_created_at: datetime,
  ) -> int:
    HOURS_IN_DAY = 24
    BASE_LENGTH_DAYS = 1

    seconds_diff_from_creation = (time_updated - streak_created_at).total_seconds()
    hours_diff_from_creation = float(seconds_diff_from_creation / self.SECONDS_IN_HOUR, 1)

    ### Formula: length_days = (diff_hours // HOURS_IN_DAY) + BASE
    # HOURS_IN_DAY = 24
    # BASE = 1 (initial length_days value)
    new_streak_length_days = int((hours_diff_from_creation // HOURS_IN_DAY) + BASE_LENGTH_DAYS)

    return new_streak_length_days

  def terminate_streak(self):
    pass

  
