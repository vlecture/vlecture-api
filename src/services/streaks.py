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

class StreakDecisionEnum(str, Enum):
  CONTINUE = "CONTINUE"
  TERMINATE = "TERMINATE"
  ERROR = "ERROR"

class StreaksService:
  SECONDS_IN_HOUR = 3600
  SECONDS_TO_HOUR_PRECISION = 6
  HOURS_IN_DAY = 24
  BASE_LENGTH_DAYS = 1

  def fetch_all_my_streak(
    self,
    session: Session,
    user_id: UUID,
  ) -> (List[Streaks] | None):
    """
    Get all streaks from a user
    """

    all_streaks = session.query(Streaks) \
      .filter(Streaks.owner_id == user_id, Streaks.is_active == True) \
      .order_by(Streaks.updated_at.desc()) \
      .all()
    
    return all_streaks

  def fetch_latest_streak(
    self, 
    session: Session,
    user_id: UUID
  ) -> (Streaks | None):
    """
    Get the latest Streak from a user
    """
    latest_streak = session.query(Streaks) \
      .filter(Streaks.owner_id == user_id, Streaks.is_active == True) \
      .order_by(Streaks.updated_at.desc()) \
      .first()
    
    return latest_streak

  def determine_streak_decision(
    self, 
    current_time: datetime, 
    streak_last_updated: datetime
  ) -> StreakDecisionEnum:
    if (current_time < streak_last_updated):
      return StreakDecisionEnum.ERROR
    
    SECONDS_IN_DAY = self.SECONDS_IN_HOUR * self.HOURS_IN_DAY
    seconds_diff = (current_time - streak_last_updated).total_seconds()

    if seconds_diff > SECONDS_IN_DAY:
      return StreakDecisionEnum.TERMINATE

    return StreakDecisionEnum.CONTINUE

  def create_streak_and_store_db(
    self,
    session: Session,
    user_id: UUID,
    time_created: datetime,
  ) -> Streaks:
    streak_schema = self._create_new_streak(
      user_id=user_id,
      time_created=time_created,
    )

    streak_obj_db = Streaks(**streak_schema.model_dump())

    try:
      session.add(streak_obj_db)
      session.commit()
      session.refresh(streak_obj_db)
    except Exception as e:
      session.rollback()
      raise RuntimeError(f"Error while creating new Streak: ${e}")
    finally:
      session.close()

    return streak_obj_db
  
  def _create_new_streak(
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
    time_updated: datetime,
    session: Session,
  ) -> bool:
    # Update updated_at and length_days (if needed)
    self._sync_streak_updated_at(
      streak=streak, 
      time_updated=time_updated, 
      session=session
    )

    is_increment_length = self.decide_if_increment_length(
      streak=streak, 
      time_updated=time_updated
    )

    if not is_increment_length:
      print("Streak length is NOT incremented...")
      return False
    
    # Else, also update streak length
    self.increment_streak_length(
      streak=streak,
      time_updated=time_updated,
      session=session,
    )

    print("Streak length is incremented!")

    return True

  def _sync_streak_updated_at(
    self, 
    streak: Streaks, 
    time_updated: datetime, 
    session: Session
  ):
    streak.updated_at = time_updated
    session.commit()

  def make_streak_inactive(
    self,
    streak: Streaks,
    session: Session,
  ):
    streak.is_active = False
    session.commit()

  def decide_if_increment_length(
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

    if new_streak_length_days == -1:
      return False

    if new_streak_length_days <= streak.length_days:
      return False
    
    return True
  
  def increment_streak_length(
    self,
    streak: Streaks,
    time_updated: datetime,
    session: Session,
  ) -> None:
    streak_created_at = streak.created_at
    new_streak_length_days = self.calc_new_streak_length_days(
      time_updated=time_updated, 
      streak_created_at=streak_created_at
    )

    streak.length_days = new_streak_length_days
    session.commit()

  def calc_new_streak_length_days(
    self,
    time_updated: datetime,
    streak_created_at: datetime,
  ) -> int:
    seconds_diff_from_creation = (time_updated - streak_created_at).total_seconds()
    
    hours_diff_from_creation = round(seconds_diff_from_creation / self.SECONDS_IN_HOUR, self.SECONDS_TO_HOUR_PRECISION)
    print("hours_diff_from_creation", seconds_diff_from_creation / self.SECONDS_IN_HOUR)

    ### Formula: length_days = (diff_hours // HOURS_IN_DAY) + BASE
    # HOURS_IN_DAY = 24
    # BASE = 1 (initial length_days value)
    new_streak_length_days = int((hours_diff_from_creation // self.HOURS_IN_DAY) + self.BASE_LENGTH_DAYS)

    return new_streak_length_days

  def terminate_streak(self):
    pass

  
