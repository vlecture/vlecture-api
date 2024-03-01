from datetime import date, datetime, time, timedelta
import uuid
from typing import Union, List, Optional
from uuid import UUID

from pydantic import (
  BaseModel, 
  Field, 
  computed_field,
  field_validator,
)

from src.schemas.base import DBBaseModel

TRANSCRIPTION_DEFAULT_TITLE = "My Transcription"

class TranscriptionResponseSchema(BaseModel):
  """
  Return type for Transcription object

  Usage example:

  @app.post("/transcribe/", response_model=TranscriptionResponseSchema):
      ... 
      return transcriptionResObj
  """
  id: UUID
  title: str
  created_at: datetime
  duration: float

class TranscriptionChunksResponseSchema(BaseModel):
  "Transcription Chunks response model"
  id: UUID
  transcription_id: UUID
  content: Optional[str]
  created_at: datetime
  duration: float

class TranscriptionChunksSchema(DBBaseModel, BaseModel):
  """
  Schema for Transcription Chunks object
  """
  
  transcription_id: UUID
  duration: float = 0 # how many seconds in a chunk
  content: Optional[str] = ""
  is_edited: bool = False

  @field_validator("duration")
  @classmethod
  def validate_duration(cls, dur: float) -> float:
    if dur < 0:
      raise ValueError("Duration must be a non-negative real number")
    
    return dur
  
  class Config:
        orm_mode = True
  
  def build_response_model(self) -> TranscriptionChunksResponseSchema:
    return TranscriptionChunksResponseSchema( 
          id=self.id,
          transcription_id=self.transcription_id,
          content=self.content,
          created_at=self.created_at,
          duration=self.duration,
        )

class TranscriptionSchema(DBBaseModel, BaseModel):
  """
  Input type & schema for Transcription
  
  Usage example:

  async def create_trc(trc: TranscriptionSchema) -> Any:
      ... 
      return transcriptionResObj
    
  """
  title: str = TRANSCRIPTION_DEFAULT_TITLE
  tags: Optional[Union[List[str], str]] = []
  chunks: Optional[List[TranscriptionChunksSchema]] = []
  is_edited: bool = False

  @computed_field
  @property
  def duration(self) -> float:
    """Duration property is computed automatically"""
    if len(self.chunks) == 0:
      return 0
    
    total = 0

    for chunk in self.chunks:
      total += chunk.duration
    
    return total
  
  class Config:
        orm_mode = True

  def build_response_model(self) -> TranscriptionResponseSchema:
    return TranscriptionResponseSchema( 
          id=self.id,
          title=self.title,
          created_at=self.created_at,
          duration=self.duration,
        )


# OLD MODELS
# class TranscriptionChunksSchema(BaseModel):
#   id: UUID = Field(default_factory=lambda: uuid.uuid4())
#   transcription_id: UUID
#   duration: float = 0 # how many seconds in a chunk
#   content: Optional[str] = ""
#   created_at: datetime = Field(default_factory=lambda: datetime.now())
#   updated_at: datetime = Field(default_factory=lambda: datetime.now())
#   is_edited: bool = False
#   is_deleted: bool = False

#   @field_validator("duration")
#   @classmethod
#   def validate_duration(cls, dur: float) -> float:
#     if dur < 0:
#       raise ValueError("Duration must be a non-negative real number")
    
#     return dur

# class TranscriptionSchema(BaseModel):
#   """
#   Input type & schema for Transcription
  
#   Usage example:

#   async def create_trc(trc: TranscriptionSchema) -> Any:
#       ... 
#       return transcriptionResObj
    
#   """
#   id: UUID = Field(default_factory= lambda: uuid.uuid4())
#   title: str = TRANSCRIPTION_DEFAULT_TITLE
#   tags: Optional[Union[List[str], str]] = []
#   chunks: Optional[List[TranscriptionChunksSchema]] = []
#   # duration: float # uses a computed field below
#   created_at: datetime = Field(default_factory=lambda: datetime.now())
#   updated_at: datetime = Field(default_factory=lambda: datetime.now())
#   is_edited: bool = False
#   is_deleted: bool = False

#   @computed_field
#   @property
#   def duration(self) -> float:
#     if len(self.chunks) == 0:
#       return 0
    
#     total = 0

#     for chunk in self.chunks:
#       total += chunk.duration
    
#     return total