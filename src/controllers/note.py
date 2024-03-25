from enum import Enum
import http
from datetime import datetime
import pytz

from fastapi import (
    APIRouter,
    Request,
    Response,
    Depends,
    Body,
)

from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from typing import (
  List
)

from src.models.users import User
from src.services.users import get_current_user


from src.schemas.note import (
  NoteSchema,
  GenerateNoteRequestSchema,
)

class NoteRouterTags(Enum):
  notes = "notes"

note_router = APIRouter(
  prefix="/v1/notes",
  tags=[NoteRouterTags.notes]
)

@note_router.post(
  "/generate",
  response_description="Create a new vlecture Note",
  status_code=http.HTTPStatus.CREATED,
  response_model=NoteSchema
)
def generate_vlecture_note(
  request: Request, 
  transcript: GenerateNoteRequestSchema = Body(),
  user: User = Depends(get_current_user),
):
  transcript = jsonable_encoder(transcript)

  # Process Note Generation here...
  # ...

  # Generate object to be inserted to mdb
  mdb_note_schema = {}

  # Store to MongoDB
  new_note = request.app.note_collection.insert_one(mdb_note_schema)

  created_note = request.app.note_collection.find_one({
    "_id": new_note.inserted_id
  })

  return created_note

@note_router.get(
  "/all",
  response_description="Fetch all of user's notes",
  status_code=http.HTTPStatus.OK,
  response_model=List[NoteSchema]
)
def get_all_notes(
  request: Request,
  user: User = Depends(get_current_user)
):
  my_notes = list(request.app.note_collection.find({
    "owner_id": user.id,
  }))

  return my_notes


@note_router.get(
  "/{note_id}",
  response_description="Fetch a specific note",
  status_code=http.HTTPStatus.OK,
  response_model=NoteSchema,
)
def get_a_note(
  request: Request,
  user: User = Depends(get_current_user)
):
  my_note = request.app.note_collection.find({
    "owner_id": user.id
  })

  return my_note

