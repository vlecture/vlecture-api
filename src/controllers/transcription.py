from enum import Enum
import http
import uuid
from uuid import UUID

from datetime import datetime
import json

from fastapi import (
    APIRouter,
    Request,
    Response,
    Depends,
    Body,
)

from src.utils.time import get_datetime_now_jkt

from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from botocore.exceptions import ClientError
import requests

from sqlalchemy.orm import Session

from src.utils.db import get_db

from src.models.transcription import Transcription

from src.models.users import User
from src.services.users import get_current_user

from src.utils.settings import AWS_BUCKET_NAME
from src.schemas.base import GenericResponseModel
from src.schemas.transcription import (
    TranscribeAudioRequestSchema,
    PollTranscriptionRequestSchema,
    ViewTranscriptionViaJobNameRequestSchema,
    TranscriptionSchema,
    TranscriptionChunksSchema,
    ViewTranscriptionRequestSchema,
)
from src.services.transcription import TranscriptionService

from src.utils.time import (
    get_datetime_now_jkt
)
from src.utils.aws.s3 import AWSS3Client
from src.utils.aws.transcribe import (
    AWSTranscribeClient,
)


class TranscriptionRouterTags(Enum):
    transcribe = "transcribe"


transcription_router = APIRouter(
    prefix="/v1/transcription", tags=[TranscriptionRouterTags.transcribe]
)


@transcription_router.post("/create", status_code=http.HTTPStatus.OK)
async def transcribe_audio(
    req: TranscribeAudioRequestSchema,
    session: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
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

    # print(filename)

    try:
        # Transcribe audio
        await service.transcribe_file(
            transcribe_client=transcribe_client,
            job_name=job_name,
            file_uri=file_uri,
            file_format=file_format,
            language_code=language_code,
        )

        # Store created transcription to db
        print("STORING TRANSCRIPTION TO DB....")

        formatted_tsc_response = (
            await service.retrieve_formatted_transcription_from_job_name(
                transcribe_client=transcribe_client, job_name=job_name
            )
        )

        # Transcription Fields
        tsc_datetime_now = get_datetime_now_jkt()
        chunk_items = formatted_tsc_response["results"]["items"]

        tsc_id = uuid.uuid4()
        tsc_title = req.title if req.title != None else "My Transcription"

        # Generate the TranscriptionChunk objects, and calculate total_duration first
        generate_chunks_response = service.generate_transcription_chunks(
            transcription_id=tsc_id, items=chunk_items
        )

        transcription_chunks = generate_chunks_response.chunks
        total_duration = generate_chunks_response.duration

        # Fetch user id
        owner_id = user.id

        # Store Transcription object to database
        tsc_create_schema = TranscriptionSchema(
            id=tsc_id,
            created_at=tsc_datetime_now,
            updated_at=tsc_datetime_now,
            is_deleted=False,
            owner_id=owner_id,
            title=tsc_title,
            tags=req.tags,
            duration=total_duration,
            language=language_code,
        )

        store_tsc_response = await service.insert_transcription_result(
            session=session, transcription_data=tsc_create_schema
        )

        if store_tsc_response:
            print(f"Stored transcription object to db: {store_tsc_response.__str__()}")

        # Then, store TranscriptionChunk object to database, bcs it needs to maintain a ForeignKey
        print(f"Storing Transcription Chunks to db...")
        for chunk in transcription_chunks:
            await service.insert_transcription_chunks(
                session=session, transcription_chunk_data=chunk
            )

        response = {
            "transcription": tsc_create_schema,
            "transcription_chunks": transcription_chunks,
        }

        return JSONResponse(
            status_code=http.HTTPStatus.CREATED, content=jsonable_encoder(response)
        )

    except TimeoutError:
        return JSONResponse(
            status_code=http.HTTPStatus.REQUEST_TIMEOUT,
            content="Error: Timeout during audio transcription.",
        )
    except RuntimeError:
        return JSONResponse(
            status_code=http.HTTPStatus.BAD_REQUEST,
            content="Audio Transcription job failed.",
        )


@transcription_router.get("/poll", status_code=http.HTTPStatus.OK)
async def poll_transcription_job(req: PollTranscriptionRequestSchema):
    transcribe_client = AWSTranscribeClient().get_client()

    service = TranscriptionService()

    try:
        response = await service.poll_transcription_job(
            transcribe_client=transcribe_client, job_name=req.job_name
        )

        return JSONResponse(
            status_code=http.HTTPStatus.OK, content=jsonable_encoder(response)
        )
    except TimeoutError:
        return JSONResponse(
            status_code=http.HTTPStatus.REQUEST_TIMEOUT,
            content="Error: Timeout while processing transcription job.",
        )
    except ClientError:
        return JSONResponse(
            status_code=http.HTTPStatus.BAD_REQUEST,
            content="Error: Audio Transcription job failed.",
        )

@transcription_router.get("/all", status_code=http.HTTPStatus.OK)
def view_all_transcriptions(
    session: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    service = TranscriptionService()

    response = service.fetch_all_transcriptions_chunks_db(
        session=session,
        user=user,
    )
    
    return JSONResponse(
        status_code=http.HTTPStatus.OK,
        content=response,
    )

@transcription_router.get("/{tsc_id}", status_code=http.HTTPStatus.OK)
def view_a_transcription(
    tsc_id: UUID,
    session: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    service = TranscriptionService()

    response = service.fetch_one_transcriptions_chunks_db(
        tsc_id=tsc_id,
        session=session,
        user=user,
    )

    full_transcript = service.convert_chunks_into_full_transcript(
        tsc_id=tsc_id,
        session=session,
        user=user,
    )

    response["full_transcript"] = full_transcript
    
    return JSONResponse(
        status_code=http.HTTPStatus.OK,
        content=response,
    )

@transcription_router.post("/view", status_code=http.HTTPStatus.OK)
async def view_transcription_from_jobname(req: ViewTranscriptionViaJobNameRequestSchema):
    transcribe_client = AWSTranscribeClient().get_client()
    job_name = req.job_name

    service = TranscriptionService()

    try:
        response = await service.retrieve_formatted_transcription_from_job_name(
            transcribe_client=transcribe_client, job_name=job_name
        )

        return JSONResponse(
            status_code=http.HTTPStatus.OK, content=jsonable_encoder(response)
        )
    except TimeoutError:
        return JSONResponse(
            status_code=http.HTTPStatus.REQUEST_TIMEOUT,
            content="Error: Timeout while processing transcription job.",
        )
    except ClientError:
        return JSONResponse(
            status_code=http.HTTPStatus.BAD_REQUEST,
            content="Error: Audio Transcription job failed..",
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

        return JSONResponse(
            status_code=http.HTTPStatus.OK, content=jsonable_encoder(response)
        )
    except TimeoutError:
        return JSONResponse(
            status_code=http.HTTPStatus.REQUEST_TIMEOUT,
            content="Error: Timeout while trying to delete transcription job.",
        )
    except ClientError as e:
        return JSONResponse(
            status_code=http.HTTPStatus.BAD_REQUEST,
            content=f"Error: Failed to delete transcription job: {e}",
        )
