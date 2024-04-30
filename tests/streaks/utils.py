import uuid
import pytz
from datetime import (
  datetime,
  timedelta
)
from src.schemas.streaks import StreaksSchema

original_streak_uuid = uuid.UUID('a2024ff2-b77b-43ec-aad6-d3fc5730655b')
new_streak_uuid = uuid.UUID('3d45cbf3-38a1-48a4-a737-c2a429fdc4b1')

owner_id = uuid.UUID('af81b095-20ca-453a-8caf-d6448359443a');

time_after_30h = datetime(2024, 4, 30, 12, 4, 49, 22859, tzinfo=pytz.timezone(zone="Asia/Jakarta"))
time_after_12h = time_after_30h - timedelta(hours=18)
time_creation = time_after_30h - timedelta(hours=30)

streak_obj = StreaksSchema(
  id=original_streak_uuid,

  # Create a streak 30 hours ago
  created_at=time_creation,
  updated_at=time_creation,
  is_deleted=False,
  owner_id=owner_id,
  length_days=1,
  is_active=True,
)

streak_obj_first_update_after_12h = StreaksSchema(
  id=original_streak_uuid,

  # Updated streak_obj after 12 hours
  created_at=time_creation,
  updated_at=time_after_12h,
  is_deleted=False,
  owner_id=owner_id,

  # Still 1 because 24 hours haven't elapsed yet
  length_days=1,
  is_active=True,
)

streak_obj_second_update_after_30h = StreaksSchema(
  id=original_streak_uuid,

  # Updated streak_obj after 30 hours
  created_at=time_creation,
  updated_at=time_after_30h,
  is_deleted=False,
  owner_id=owner_id,

  # Because total hours elapsed since streak is alive is >= 24 and < 48, length_days becomes 2  
  length_days=2,
  is_active=True,
)

streak_obj_terminate_streak_after_30h = StreaksSchema(
  id=original_streak_uuid,

  created_at=time_creation,

  # updated_at DOES NOT change
  updated_at=time_creation,
  is_deleted=False,
  owner_id=owner_id,

  length_days=1,

  # is_active is set to FALSE
  is_active=False,
)

new_streak_obj_after_30h = StreaksSchema(
  id=new_streak_uuid,
  created_at=time_after_30h,
  updated_at=time_after_30h,
  is_deleted=False,
  owner_id=owner_id,
  length_days=1,
  is_active=True,
)