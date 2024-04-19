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

from src.schemas.qna import (
  QNAAnswerSchema,
  QNAQuestionSchema,
  QNAQuestionSetSchema,
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
  response_model=QNASchema
)
def generate_qna_set(
  request: Request,
  payload: dict, # TODO
  respnose_model: dict, # TODO
):
  pass