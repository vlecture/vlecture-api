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

PyObjectId = Annotated[str, BeforeValidator(str)]

# OBJECT SCHEMAS
class NoteBlockSchema(BaseModel):
  """
  Object Schema for a vlecture Note Block  
  """

  id: str
  type: str
  props: Optional[dict]
  content: Optional[List[dict]]
  children: Optional[List[Any]]


class NoteSchema(BaseModel):
  """
  Mongodb Collection Schema for a vlecture Note
  """

  # The primary key for the NoteSchema, stored as a `str` on the instance.
  # This will be aliased to `_id` when sent to MongoDB,
  # but provided as `id` in the API requests and responses.
  id: Optional[PyObjectId] = Field(alias="_id", default=None)
  owner_id: UUID
  
  title: Optional[str] = Field(max_length=255, min_length=3)
  subtitle: Optional[str] = Field(max_length=255, min_length=1)

  created_at: datetime
  updated_at: datetime

  is_deleted: bool = Field(default=False)
  is_edited: bool = Field(default=False)
  is_published: bool = Field(default=False)

  main: Optional[List[NoteBlockSchema]]
  cues: Optional[List[NoteBlockSchema]]
  summary: Optional[List[NoteBlockSchema]]

  # To ensure Python and Mongodb `_id` compatibility
  model_config = ConfigDict(
    populate_by_name=True,
    arbitrary_types_allowed=True,
  )

class LLMCornellNoteFromTranscript(BaseModel):
  main: Optional[List[str]]
  cues: Optional[List[str]]
  summary: Optional[List[str]]

# REQUEST SCHEMAS
class GenerateVlectureNoteRequestSchema(BaseModel):
  transcript: str
  title: str

class GenerateNoteServiceRequestSchema(BaseModel):
  transcript: str
  title: str
  owner_id: UUID

class GenerateBlockNoteFromCornellJsonRequestSchema(BaseModel):
  cornell_json_section: List[str]

class BlockNoteCornellSchema(BaseModel):
  main: Optional[List[NoteBlockSchema]]
  cues: Optional[List[NoteBlockSchema]]
  summary: Optional[List[NoteBlockSchema]]

# RESPONSE SCHEMAS
class GenerateNoteResponseSchema(BaseModel):
  note: NoteSchema

