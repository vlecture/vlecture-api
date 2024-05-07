from uuid import UUID
from datetime import datetime

from typing import (
  Annotated,
  Optional,
  List,
  Any
)
from pydantic import (
  BaseModel, 
  BeforeValidator,
  Field,
  ConfigDict,
)

from src.schemas.base import DBBaseModel

# OBJECT SCHEMA
class StreaksSchema(DBBaseModel, BaseModel):
  """
  Schema for Flashcard Streaks object
  """

  owner_id: UUID
  length_days: int
  is_active: bool

