from datetime import date, datetime, time, timedelta
import uuid
from typing import Union, List, Optional
from pydantic import (
  UUID4, 
  BaseModel, 
  Field, 
  computed_field,
  field_validator,
)

TRANSCRIPTION_DEFAULT_TITLE = "My Transcription"

class TranscriptionChunksSchema(BaseModel):
  id: UUID4 = Field(default_factory=lambda: uuid.uuid4())
  transcription_id: UUID4
  duration: float = 0 # how many seconds in a chunk
  content: Optional[str] = ""
  created_at: datetime = Field(default_factory=lambda: datetime.now())
  updated_at: datetime = Field(default_factory=lambda: datetime.now())
  is_edited: bool = False
  is_deleted: bool = False

  @field_validator("duration")
  @classmethod
  def validate_duration(cls, dur: float) -> float:
    if dur < 0:
      raise ValueError("Duration must be a non-negative real number")
    
    return dur

class TranscriptionSchema(BaseModel):
  """
  Input type & schema for Transcription
  
  Usage example:

  async def create_trc(trc: TranscriptionSchema) -> Any:
      ... 
      return transcriptionResObj
    
  """
  id: UUID4 = Field(default_factory= lambda: uuid.uuid4())
  title: str = TRANSCRIPTION_DEFAULT_TITLE
  tags: Optional[Union[List[str], str]] = []
  chunks: Optional[List[TranscriptionChunksSchema]] = []
  # duration: float # uses a computed field below
  created_at: datetime = Field(default_factory=lambda: datetime.now())
  updated_at: datetime = Field(default_factory=lambda: datetime.now())
  is_edited: bool = False
  is_deleted: bool = False

  @computed_field
  @property
  def duration(self) -> float:
    if len(self.chunks) == 0:
      return 0
    
    total = 0

    for chunk in self.chunks:
      total += chunk.duration
    
    return total

class TranscriptionResponseSchema(BaseModel):
  """
  Return type for Transcription object

  Usage example:

  @app.post("/transcribe/", response_model=TranscriptionResponseSchema):
      ... 
      return transcriptionResObj
  """
  id: UUID4 = Field(default_factory= lambda: uuid.uuid4())
  title: str = Field(min_length=1, max_length=255, default=TRANSCRIPTION_DEFAULT_TITLE)
  tags: Optional[Union[List[str], str]] = []
  created_at: datetime = Field(default_factory=lambda: datetime.now())
  is_edited: bool = False

  @computed_field
  @property
  def duration(self) -> float:
    if len(self.chunks) == 0:
      return 0
    
    total = 0

    for chunk in self.chunks:
      total += chunk.duration
    
    return total
