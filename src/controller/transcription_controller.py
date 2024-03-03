from enum import Enum
import uuid
import http
import requests

from fastapi import APIRouter, Depends
from botocore.exceptions import ClientError

from schemas.base import GenericResponseModel
from services.transcription import TranscriptionService
from utils.s3 import AWSS3Client
from utils.transcribe import AWSTranscribeClient

class TranscriptionRouterTags(Enum):
  transcribe = "transcribe"

transcription_router = APIRouter(
  prefix="/v1/transcription",
  tags=[TranscriptionRouterTags.transcribe]
)

@transcription_router.post(
  "/{s3_object_name}", 
  status_code=http.HTTPStatus.CREATED, 
  response_model=GenericResponseModel
)
async def transcribe_audio(s3_object_name: str, language_code = "id-ID"):
  # s3_client = AWSS3Client().get_client()
  service = TranscriptionService()
  transcribe_client = AWSTranscribeClient().get_client()

  filename, file_format = s3_object_name.split(".")
  generated_job_name = service.generate_job_name()

  try:
    response = service.transcribe_file(
      transcribe_client=transcribe_client,
      job_name=generated_job_name,
      filename=filename,
      file_format=file_format,
      language_code=language_code
    ) 

    return GenericResponseModel(
      status_code=http.HTTPStatus.OK,
      message="Successfully created audio transcription",
      data=response
    )
  except ClientError as err:
    return GenericResponseModel(
      status_code=http.HTTPStatus.REQUEST_TIMEOUT,
      error="Timeout while processing transcription job.",
    )