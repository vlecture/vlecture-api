from datetime import date, datetime, time, timedelta
from pydantic import UUID4, BaseModel, Field, List, Optional

class TranscriptionChunks(BaseModel):
  id: UUID4
  transcription_id: UUID4
  duration: float # how many seconds in chunk
  content: Optional[str]
  created_at: datetime
  updated_at: datetime
  is_edited: bool

class TranscriptionSchema(BaseModel):
  id: UUID4
  title: str
  tags: Optional[List[str]]
  chunks: Optional[List[TranscriptionChunks]]
  duration: float # total seconds of transcription
  created_at: datetime
  updated_at: datetime
