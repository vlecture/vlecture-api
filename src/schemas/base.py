import http
from datetime import datetime
from typing import Optional, Any, Union

import uuid
from uuid import UUID

from pydantic.main import BaseModel

from pydantic import (
  BaseModel, 
)

class GenericResponseModel(BaseModel):
  """
  A generic response model for all API responses
  """

  status_code: Optional[Union[http.HTTPStatus, int]] = None
  error: Optional[str]
  message: Optional[str]
  data: Any

class DBBaseModel(BaseModel):
  """
  Base model for all the models to be stored in the database
  """

  id: UUID
  created_at: datetime 
  updated_at: Optional[datetime]
  is_deleted: datetime

  class Config:
    orm_mode = True