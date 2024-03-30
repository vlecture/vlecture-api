from datetime import datetime
from typing import List, Optional

from pydantic import UUID4
from pydantic import (
  BaseModel,
)

from src.schemas.base import DBBaseModel

class FlashcardSetsRequestSchema(BaseModel):
  user_id: UUID4

class FlashcardsRequestSchema(BaseModel):
  set_id: UUID4
