from enum import Enum
import uuid
import http
import requests

from src.utils.settings import AWS_BUCKET_NAME
from fastapi import APIRouter, Depends
from botocore.exceptions import ClientError

from src.schemas.base import GenericResponseModel
from src.services.transcription import TranscriptionService
from src.utils.aws.s3 import AWSS3Client
from src.utils.aws.transcribe import AWSTranscribeClient

class TranscriptionRouterTags(Enum):
  transcribe = "transcribe"

transcription_router = APIRouter(
  prefix="/v1/transcription",
  tags=[TranscriptionRouterTags.transcribe]
)

@transcription_router.post(
  "/{s3_filename}", 
  status_code=http.HTTPStatus.CREATED, 
  response_model=GenericResponseModel
)
async def transcribe_audio(s3_filename: str, language_code = "id-ID"):
  transcribe_client = AWSTranscribeClient().get_client()

  service = TranscriptionService()

  filename, file_format = s3_filename.split(".")
  generated_job_name = service.generate_job_name()

  file_uri = service.generate_file_uri(bucket_name=AWS_BUCKET_NAME, filename=filename, extension=file_format)

  try:
    response = await service.transcribe_file(
      transcribe_client=transcribe_client,
      job_name=generated_job_name,
      file_uri=file_uri,
      file_format=file_format,
      language_code=language_code
    ) 

    return GenericResponseModel(
      status_code=http.HTTPStatus.CREATED,
      message="Successfully created audio transcription",
      error="",
      data=response,
    )
  except TimeoutError:
    return GenericResponseModel(
      status_code=http.HTTPStatus.REQUEST_TIMEOUT,
      message="Error",
      error="Timeout while processing transcription job.",
      data={},
    )
  except ClientError:
    return GenericResponseModel(
      status_code=http.HTTPStatus.BAD_REQUEST,
      message="Error",
      error="Audio Transcription job failed.",
      data={},
    )

@transcription_router.get(
  "/{transcription_job_name}",
  status_code=http.HTTPStatus.OK,
  response_model=GenericResponseModel
)
async def poll_transcription_job(transcription_job_name: str):
  transcribe_client = AWSTranscribeClient().get_client()

  service = TranscriptionService()

  try:
    response = await service.poll_transcription_job(
      transcribe_client=transcribe_client, 
      job_name=transcription_job_name
    )

    return GenericResponseModel(
      status_code=http.HTTPStatus.OK,
      message="Successfully retrieved transcription status",
      error="",
      data=response,
    )
  except TimeoutError:
    return GenericResponseModel(
      status_code=http.HTTPStatus.REQUEST_TIMEOUT,
      message="Error",
      error="Timeout while processing transcription job.",
      data={},
    )
  except ClientError:
    return GenericResponseModel(
      status_code=http.HTTPStatus.BAD_REQUEST,
      message="Error",
      error="Audio Transcription job failed.",
      data={},
    )

  