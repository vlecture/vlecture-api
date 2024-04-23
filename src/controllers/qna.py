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

from src.schemas.qna import (
  # OBJECTS
  QNAAnswerSchema,
  QNAQuestionSchema,
  QNAQuestionSetSchema,

  # REQUESTS
  GenerateQNASetRequestSchema
)

 
from src.services.users import get_current_user

from src.services.note import (
  NoteService
)

from src.services.qna import (
  QNAService
)

class QNARouterTags(Enum):
  qna = "qna"

qna_router = APIRouter(
  prefix="/v1/qna",
  tags=[QNARouterTags],
)

@qna_router.post(
  "/generate",
  response_description="Create a new Note QnA set",
  status_code=http.HTTPStatus.OK,
)
def generate_qna_set(
  request: Request,
  payload: GenerateQNASetRequestSchema = Body(),
  user: User = Depends(get_current_user),
):
  note_service = NoteService()
  qna_service = QNAService()

  note_id = payload.note_id
  question_count = payload.question_count
  
  my_note = note_service.fetch_note_from_mongodb(
    note_id=note_id,
    request=request,
    user=user,
  )

  generated_qna_set = qna_service.generate_qna_set(
    note=my_note,
    question_count=question_count,
    user=user,
  )

  created_qna_set_schema = qna_service.create_qna_set_obj(
    question_count=question_count,
    qna_set=generated_qna_set,
    user=user,
  )

  # Store to MongoDB
  new_qna_set_document = request.app.qna_collection.insert_one(
    created_qna_set_schema.model_dump(
      by_alias=True,
      # exclude=["id"],
    )
  )

  created_qna_set_document = request.app.qna_collection.find_one({
    "_id": new_qna_set_document.inserted_id,
  }, {
    # Exclude "_id" field from the returned object -- bcs already came with "id" field
    "_id": 0,
  })

  return created_qna_set_document



