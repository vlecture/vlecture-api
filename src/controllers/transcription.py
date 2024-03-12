from enum import Enum
import http

from fastapi import APIRouter
from botocore.exceptions import ClientError

from src.utils.settings import AWS_BUCKET_NAME
from src.schemas.base import GenericResponseModel
from src.schemas.transcription import (
  TranscribeAudioRequestSchema,
  PollTranscriptionRequestSchema
)
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
  "/create", 
  status_code=http.HTTPStatus.CREATED, 
  response_model=GenericResponseModel
)
async def transcribe_audio(req: TranscribeAudioRequestSchema):
  transcribe_client = AWSTranscribeClient().get_client()

  service = TranscriptionService()
  
  filename, file_format = req.s3_filename.split(".")
  job_name = req.job_name
  language_code = req.language_code

  file_uri = service.generate_file_uri(bucket_name=AWS_BUCKET_NAME, filename=filename, extension=file_format)

  try:
    response = await service.transcribe_file(
      transcribe_client=transcribe_client,
      job_name=job_name,
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
  "/poll",
  status_code=http.HTTPStatus.OK,
  response_model=GenericResponseModel
)
async def poll_transcription_job(req: PollTranscriptionRequestSchema):
  transcribe_client = AWSTranscribeClient().get_client()

  service = TranscriptionService()

  try:
    response = await service.poll_transcription_job(
      transcribe_client=transcribe_client, 
      job_name=req.job_name
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

  