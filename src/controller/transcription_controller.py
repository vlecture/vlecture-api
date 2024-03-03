from enum import Enum
import http

from fastapi import APIRouter, Depends

from schemas.base import GenericResponseModel
from services.transcription import TranscriptionService

class TranscriptionRouterTags(Enum):
  transcribe = "transcribe"

transcription_router = APIRouter(
  prefix="/v1/transcription",
  tags=[TranscriptionRouterTags.transcribe]
)

@transcription_router.post(
  "/{s3_obj_uuid}", 
  status_code=http.HTTPStatus.CREATED, 
  response_model=GenericResponseModel
)
async def transcribe_audio():
  pass

