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

class NoteBlockSchema(BaseModel):
  """
  Object Schema for a vlecture Note Block  
  """

  id: str
  type: str
  props: Optional[Any]
  content: Optional[List[Any]]
  children: Optional[List[Any]]


class NoteSchema(BaseModel):
  """
  Mongodb Collection Schema for a vlecture Note
  """

  id: Optional[PyObjectId] = Field(alias="_id", default=None)
  owner_id: UUID
  
  title: Optional[str] = Field(max_length=255, min_length=3)
  subtitle: Optional[str] = Field(max_length=255, min_length=1)

  created_at: datetime
  updated_at: datetime

  is_deleted: bool = Field(default=False)
  is_edited: bool = Field(default=False)
  is_published: bool = Field(default=False)

  content: Optional[List[NoteBlockSchema]]
  cues: Optional[List[NoteBlockSchema]]
  summary: Optional[List[NoteBlockSchema]]

  # To ensure Python and Mongodb `_id` compatibility
  model_config = ConfigDict(
    populate_by_name=True,
    arbitrary_types_allowed=True,
    json_schema_extra={

    }
  )

# REQUEST SCHEMAS
class GenerateNoteRequestSchema(BaseModel):
  transcript: str

# RESPONSE SCHEMAS
