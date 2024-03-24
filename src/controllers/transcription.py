from enum import Enum
import http
import uuid
from datetime import datetime
import pytz

from fastapi import (
    APIRouter,
    Request,
    Response,
    Depends,
    Body,
)

from botocore.exceptions import ClientError
import requests

from sqlalchemy.orm import Session

from src.utils.db import get_db

from src.models.transcription import Transcription

from src.utils.settings import AWS_BUCKET_NAME
from src.schemas.base import GenericResponseModel
from src.schemas.transcription import (
    TranscribeAudioRequestSchema,
    PollTranscriptionRequestSchema,
    ViewTranscriptionRequestSchema,

    TranscriptionSchema,
    TranscriptionChunksSchema,
)
from src.services.transcription import TranscriptionService
from src.utils.aws.s3 import AWSS3Client
from src.utils.aws.transcribe import AWSTranscribeClient

class TranscriptionRouterTags(Enum):
    transcribe = "transcribe"


transcription_router = APIRouter(
    prefix="/v1/transcription", tags=[TranscriptionRouterTags.transcribe]
)


@transcription_router.post(
    "/create", status_code=http.HTTPStatus.CREATED, response_model=GenericResponseModel
)
async def transcribe_audio(req: TranscribeAudioRequestSchema, session: Session = Depends(get_db)):
    transcribe_client = AWSTranscribeClient().get_client()

    service = TranscriptionService()

    filename, file_format = req.s3_filename.split(".")
    job_name = req.job_name
    language_code = req.language_code

    file_uri = service.generate_file_uri(
        bucket_name=AWS_BUCKET_NAME, 
        filename=filename, 
        extension=file_format,
    )

    try:
        # Transcribe audio
        created_tsc_response = await service.transcribe_file(
            transcribe_client=transcribe_client,
            job_name=job_name,
            file_uri=file_uri,
            file_format=file_format,
            language_code=language_code,
        )

        # Store created transcription to db
        print("STORING TRANSCRIPTION TO DB....")

        formatted_tsc_response = await service.retrieve_formatted_transcription_from_job_name(
            transcribe_client=transcribe_client,
            job_name=job_name
        )
        
        # Transcription Fields
        tsc_datetime_now = service.get_datetime_now_jkt()
        chunk_items = formatted_tsc_response["results"]["items"]

        tsc_id = uuid.uuid4()
        tsc_title = req.title if req.title != None else "My Transcription"

        # Generate the TranscriptionChunk objects, and calculate total_duration first
        generate_chunks_response = service.generate_transcription_chunks(
            transcription_id=tsc_id,
            items=chunk_items
        )

        total_duration = generate_chunks_response.duration
        chunks = generate_chunks_response.chunks

        # Store Transcription object to database
        ## No need to insert chunk column bcs there aren't any
        tsc_create_schema = TranscriptionSchema(
            id=tsc_id,
            created_at=tsc_datetime_now,
            updated_at=tsc_datetime_now,
            is_deleted=False,

            title=tsc_title,
            tags=req.tags,
            duration=total_duration,
        )


        store_tsc_response = await service.insert_transcription_result(
            session=session,
            transcription_data=tsc_create_schema
        )

        if (store_tsc_response):
            print(f"Stored transcription object to db: {store_tsc_response.__str__()}")


        # Then, store TranscriptionChunk object to database, bcs it needs to maintain a ForeignKey
        for chunk in chunks:
            store_tsc_chunk_response = await service.insert_transcription_chunks(
                session=session,
                transcription_chunk_data=chunk
            )

            if (store_tsc_response):
                print(f"Stored chunk {store_tsc_chunk_response.id} to db")

        return GenericResponseModel(
            status_code=http.HTTPStatus.CREATED,
            message="Successfully created audio transcription",
            error="",
            data=created_tsc_response,
        )
    except TimeoutError:
        return GenericResponseModel(
            status_code=http.HTTPStatus.REQUEST_TIMEOUT,
            message="Error",
            error="Timeout while processing transcription job.",
            data={},
        )
    except RuntimeError:
        return GenericResponseModel(
            status_code=http.HTTPStatus.BAD_REQUEST,
            message="Error",
            error="Audio Transcription job failed.",
            data={},
        )


@transcription_router.get(
    "/poll", status_code=http.HTTPStatus.OK, response_model=GenericResponseModel
)
async def poll_transcription_job(req: PollTranscriptionRequestSchema):
    transcribe_client = AWSTranscribeClient().get_client()

    service = TranscriptionService()

    try:
        response = await service.poll_transcription_job(
            transcribe_client=transcribe_client, job_name=req.job_name
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


@transcription_router.get(
    "/view", status_code=http.HTTPStatus.OK, response_model=GenericResponseModel
)
async def view_transcription(req: ViewTranscriptionRequestSchema):
    transcribe_client = AWSTranscribeClient().get_client()
    job_name = req.job_name
    
    service = TranscriptionService()

    try:
        response = await service.retrieve_formatted_transcription_from_job_name(
            transcribe_client=transcribe_client,
            job_name=job_name
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

@transcription_router.delete(
    "/delete", status_code=http.HTTPStatus.OK, response_model=GenericResponseModel
)
async def delete_transcription(job_name: str):
    transcribe_client = AWSTranscribeClient().get_client()

    service = TranscriptionService()

    try:
        response = await service.delete_transcription_job(
            transcribe_client=transcribe_client, job_name=job_name
        )

        return GenericResponseModel(
            status_code=http.HTTPStatus.OK,
            message="Successfully deleted transcription job",
            error="",
            data=response,
        )
    except TimeoutError:
        return GenericResponseModel(
            status_code=http.HTTPStatus.REQUEST_TIMEOUT,
            message="Error",
            error="Timeout while trying to delete transcription job.",
            data={},
        )
    except ClientError as e:
        return GenericResponseModel(
            status_code=http.HTTPStatus.BAD_REQUEST,
            message="Error",
            error=f"Failed to delete transcription job: {e}",
            data={},
        )
