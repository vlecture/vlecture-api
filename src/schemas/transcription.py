from datetime import date, datetime, time, timedelta
import uuid
from typing import Union, List, Optional
from uuid import UUID

from pydantic import (
  BaseModel, 
  computed_field,
  field_validator,
)

from src.schemas.base import DBBaseModel

# DATABASE SCHEMA
class TranscriptionChunksSchema(DBBaseModel, BaseModel):
  """
  Schema for Transcription Chunks object
  """
  
  duration: float = 0 # how many seconds in a chunk
  is_edited: bool = False
  transcription_id: UUID
  
  start_time: float
  end_time: float

  content: Optional[str] = ""
  

  @field_validator("duration")
  @classmethod
  def validate_duration(cls, dur: float) -> float:
    if dur < 0:
      raise ValueError("Duration must be a non-negative real number")
    
    return dur
  
class TranscriptionSchema(DBBaseModel, BaseModel):
  """
  Input type & schema for Transcription
  
  Usage example:

  async def create_trc(trc: TranscriptionSchema) -> Any:
      ... 
      return transcriptionResObj
    
  """
  owner_id: UUID
  title: str
  tags: Optional[Union[List[str], str]] = []
  duration: float

### REQUEST SCHEMAS
class TranscribeAudioRequestSchema(BaseModel):
   s3_filename: str
   job_name: str
   language_code: str

   # NOTE Mar 24, newly added, backward-compatible field definitions
   title: Optional[str]
   tags: Optional[Union[List[str], str]] = []
   

class PollTranscriptionRequestSchema(BaseModel):
   job_name: str

class ViewTranscriptionRequestSchema(BaseModel):
   job_name: str

### RESPONSE SCHEMAS
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

class GenerateTranscriptionChunksResponseSchema(BaseModel):
   duration: float
   chunks: List[TranscriptionChunksSchema]

# OBJECT SCHEMAS
class TranscriptionChunkItemAlternativesSchema(BaseModel):
   confidence: str
   content: str

class TranscriptionChunkItemSchema(BaseModel):
   item_type: str
   alternatives: List[TranscriptionChunkItemAlternativesSchema]
   start_time: str
   end_time: str

# STORE TRANSCRIPTION SERVICE
class ServiceRetrieveTranscriptionChunkItemSchema(BaseModel):
   """
   The returned response from `service.retrieve_transcription_from_job_name`
   """

   content: str
   start_time: str
   end_time: str
   duration: str
   
class ServiceStoreTranscriptionRequestSchema(BaseModel):
   transcript_text: str
   transcript_items: List[ServiceRetrieveTranscriptionChunkItemSchema]