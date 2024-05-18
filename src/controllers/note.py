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
    HTTPException,
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
  BlockNoteCornellSchema,
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
  language = payload["language"] if "language" in payload else "id-ID"

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
    "is_deleted": False
  }))

  return my_notes

@note_router.patch(
    "/save/{note_id}",
    response_description="Update specified fields of a block note section",
    status_code=http.HTTPStatus.OK,
    response_model=NoteSchema,
)
def save_note(
  note_id: str,
  note_blocks: BlockNoteCornellSchema,
  request: Request,
  user: User = Depends(get_current_user),
):
  if not user:
    return JSONResponse(
      content="Error: Not logged in.",
      status_code=http.HTTPStatus.UNAUTHORIZED,
    )
  
  service = NoteService()

  try:
    result = service.save_note(
      request=request,
      note_id=note_id,
      note_blocks=note_blocks,
    )

    return result
  except HTTPException as e:
    if e.status_code == 404:
      return JSONResponse(
        content="Error: Note not found.",
        status_code=http.HTTPStatus.NOT_FOUND,
      )
    else:
      return JSONResponse(
        content="Error: Failed to save note.",
        status_code=http.HTTPStatus.BAD_REQUEST,
      )

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
  try:
    service = NoteService()

    my_note = service.fetch_note_from_mongodb(
      note_id=note_id,
      request=request,
      user=user,
    )

    if not my_note:
      return JSONResponse(
        status_code=http.HTTPStatus.NOT_FOUND, 
        content={"message": "Note not found or already deleted."}
      )

    return my_note
  except HTTPException as e:
    if e.status_code == 400:
      return JSONResponse(
        content="Invalid request body parameters.",
        status_code=http.HTTPStatus.BAD_REQUEST,
      )
    
    if e.status_code == 401:
      return JSONResponse(
        content="Not logged in.",
        status_code=http.HTTPStatus.UNAUTHORIZED,
      )

@note_router.delete(
  "/delete/{note_id}",
  response_description="delete a specific note",
  status_code=http.HTTPStatus.OK,
)
def delete_a_note(
  note_id: str,
  request: Request,
  user: User = Depends(get_current_user),
):
  if not user:
    return JSONResponse(
      content="Error: Not logged in.",
      status_code=http.HTTPStatus.UNAUTHORIZED,
    )
  
  service = NoteService()
  
  response = service.delete_note(
    note_id=note_id,
    request=request,
    user=user,
  )

  if isinstance(response, str) and "NotFound" in response:    
    return JSONResponse(status_code=http.HTTPStatus.NOT_FOUND, content={"message": response})
  
  if isinstance(response, str) and "OperationalFailure" in response:
    return JSONResponse(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, content={"message": response})

  return JSONResponse(status_code=http.HTTPStatus.OK, content={"message": "Success: Note deleted successfully."})

