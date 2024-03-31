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

from bson.objectid import ObjectId

from src.models.users import User
from src.services.users import get_current_user

from src.services.note import (
  NoteService
)

from src.schemas.note import (
  NoteSchema,
  GenerateVlectureNoteRequestSchema,
  GenerateNoteServiceRequestSchema,
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
  status_code=http.HTTPStatus.OK,
  response_model=NoteSchema
)
def generate_vlecture_note(
  request: Request, 
  payload: GenerateVlectureNoteRequestSchema = Body(),
  user: User = Depends(get_current_user),
):
  service = NoteService()
  payload = jsonable_encoder(payload)
  
  transcript = payload["transcript"]
  title = payload["title"]
  language = payload["language"] if "language" in payload else "id"

  # Convert Transcript into vlecture Note object
  req_generate_note = GenerateNoteServiceRequestSchema(
    transcript=transcript,
    title=title,
    owner_id=user.id,
    language=language,
    subtitle="",
  )

  created_note_schema = service.generate_note_from_transcription(
    payload=req_generate_note
  )

  # Convert new note Pydantic object into JSON
  # created_note_schema = jsonable_encoder(created_note_schema)

  # Store Note to database
  new_note_document = request.app.note_collection.insert_one(
    created_note_schema.model_dump(
      # NOTE important - exlucdes ID when creating documents to avoid "_id": null errors
      by_alias=True,
      exclude=["id"]
    )
  )
  
  # Retrieve newly created item
  created_note_document = request.app.note_collection.find_one({
    "_id": new_note_document.inserted_id
  })

  return created_note_document

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
  note_id: str,
  request: Request,
  user: User = Depends(get_current_user),
):
  note_id = ObjectId(note_id)
  my_note = request.app.note_collection.find_one({
    "_id": note_id
  })

  return my_note


@note_router.delete(
  "delete/{note_id}",
  response_description="Delete a specific note",
  status_code=http.HTTPStatus.OK,
)
def delete_a_note(
  note_id: str,
  request: Request,
  user: User = Depends(get_current_user),
):
  note_id = ObjectId(note_id)
  
  existing_note = request.app.note_collection.find_one({
    "_id": note_id,
    "owner_id": user.id,
    "is_deleted": False 
  })

  if not existing_note:
    return JSONResponse(status_code=http.HTTPStatus.NOT_FOUND, content={"message": "Note not found or already deleted."})

  
  result = request.app.note_collection.update_one(
    {"_id": note_id},
    {"$set": {"is_deleted": True}}
  )

  if result.modified_count == 0:
    return JSONResponse(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, content={"message": "Failed to delete note."})
  else:
    return JSONResponse(status_code=http.HTTPStatus.OK, content={"message": "Note deleted successfully."})