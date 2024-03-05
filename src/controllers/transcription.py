from enum import Enum
import uuid
import http
import requests

from os import environ as env
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
  service = TranscriptionService()
  transcribe_client = AWSTranscribeClient().get_client()

  filename, file_format = s3_object_name.split(".")
  generated_job_name = service.generate_job_name()

  BUCKET_NAME = env.get("AWS_BUCKET_NAME")
  file_uri = service.generate_file_uri(bucket_name=BUCKET_NAME, filename=filename, extension=file_format)

  try:
    response = service.transcribe_file(
      transcribe_client=transcribe_client,
      job_name=generated_job_name,
      file_uri=file_uri,
      file_format=file_format,
      language_code=language_code
    ) 

    return GenericResponseModel(
      status_code=http.HTTPStatus.OK,
      message="Successfully created audio transcription",
      data=response
    )
  except ClientError:
    return GenericResponseModel(
      status_code=http.HTTPStatus.REQUEST_TIMEOUT,
      error="Timeout while processing transcription job.",
    )