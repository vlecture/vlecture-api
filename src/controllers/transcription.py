from enum import Enum
import http

from fastapi import APIRouter
from botocore.exceptions import ClientError
import requests

from src.utils.settings import AWS_BUCKET_NAME
from src.schemas.base import GenericResponseModel
from src.schemas.transcription import (
    TranscribeAudioRequestSchema,
    PollTranscriptionRequestSchema,
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
async def transcribe_audio(req: TranscribeAudioRequestSchema):
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
        response = await service.transcribe_file(
            transcribe_client=transcribe_client,
            job_name=job_name,
            file_uri=file_uri,
            file_format=file_format,
            language_code=language_code,
        )

        # Store created transcription to db
        print("STORING TRANSCRIPTION TO DB....")

        tsc_response = await service.get_all_transcriptions(
            transcribe_client=transcribe_client, job_name=job_name
        )

        store_response = await service.store_transcription_result(transcription_job_response=tsc_response)

        if (store_response):
            print(f"store_response: {store_response}")

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
async def view_transcription(job_name: str):
    transcribe_client = AWSTranscribeClient().get_client()

    service = TranscriptionService()

    try:
        response = await service.get_all_transcriptions(
            transcribe_client=transcribe_client, job_name=job_name
        )

        aws_link = requests.get(response)

        transcription_data = aws_link.json()

        job_name = transcription_data.get("jobName")
        accountId = transcription_data.get("accountId")
        status = transcription_data.get("status")
        transcripts = transcription_data.get("results", {}).get("transcripts", [])

        temp_transcripts = []

        if transcripts:
            for i in range(len(transcripts)):
                transcript_text = transcripts[i].get("transcript")
                temp_transcripts.append(transcript_text)
        else:
            print("No transcripts found in the response")

        full_transcript = " ".join(temp_transcripts)

        items = transcription_data.get("results", {}).get("items", [])

        grouped_items = service.generate_grouped_items(items=items)

        return GenericResponseModel(
            status_code=http.HTTPStatus.OK,
            message="Successfully retrieved transcription status",
            error="",
            data={
                "jobName": job_name,
                "accountId": accountId,
                "status": status,
                "results": {"transcripts": full_transcript, "items": grouped_items},
            },
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
