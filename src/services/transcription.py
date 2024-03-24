import uuid
from uuid import UUID

import http
import time
import requests
import json

from sqlalchemy.orm import Session
from typing import List, Union
from botocore.exceptions import ClientError

from src.models.transcription import (
    Transcription,
    TranscriptionChunk,
)

from src.schemas.transcription import (
  TranscriptionChunkItemSchema,
  TranscriptionChunksSchema,
  TranscriptionSchema,
  ServiceRetrieveTranscriptionChunkItemSchema,
  GenerateTranscriptionChunksResponseSchema,
)


class TranscriptionService:
    POLL_INTERVAL_SEC = 5  # 5sec  x 3%/sec

    def get_datetime_now_jkt():
        TIMEZONE_JKT = pytz.timezone('Asia/Jakarta')
        return datetime.now(tz=TIMEZONE_JKT)

    def generate_file_uri(self, bucket_name: str, filename: str, extension: str):
        # NOTE - Can add subbuckets in the future
        return f"s3://{bucket_name}/{filename}.{extension}"

    async def get_all_transcriptions(self, transcribe_client, job_name: str):
        job_result = transcribe_client.get_transcription_job(
            TranscriptionJobName=job_name
        )
        transciption = job_result["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]
        return transciption

    async def poll_transcription_job(self, transcribe_client, job_name: str):
        max_tries = 60
        is_done = False

        while max_tries > 0:
            max_tries -= 1
            job_result = transcribe_client.get_transcription_job(
                TranscriptionJobName=job_name
            )
            job_status = job_result["TranscriptionJob"]["TranscriptionJobStatus"]

            if job_status in ["COMPLETED", "FAILED"]:
                print(f"Job {job_name} is {job_status}.")

                if job_status == "COMPLETED":
                    is_done = True
                    # print(
                    #   f"Download the transcript from\n"
                    #   f"\t{job_result['TranscriptionJob']['Transcript']['TranscriptFileUri']}."
                    # )
                break
            else:
                print(
                    f"Waiting for Transcription Job: {job_name}. Current status is {job_status}."
                )

            # Set interval to poll job status
            time.sleep(self.POLL_INTERVAL_SEC)

        if not is_done:
            return TimeoutError("Timeout when polling the transcription results")

        return job_result

    async def transcribe_file(
        self,
        transcribe_client: any,
        job_name: str,
        file_uri: str,
        file_format: str,
        language_code="id-ID",
    ):
        try:
            transcribe_client.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={"MediaFileUri": file_uri},
                MediaFormat=file_format,
                LanguageCode=language_code,
            )

            job_result = await self.poll_transcription_job(
                transcribe_client=transcribe_client, job_name=job_name
            )

            return job_result
        except TimeoutError:
            return TimeoutError("Timeout when polling the transcription results")
        except ClientError:
            raise RuntimeError("Transcription Job failed.")

    async def insert_transcription_result(
        self, 
        session: Session,
        transcription_data: TranscriptionSchema,
    ):
        """
        Stores a Transcription object to the db
        """
        db_tsc = Transcription(**transcription_data.model_dump())

        try:
            session.add(db_tsc)
            session.commit()
            session.refresh(db_tsc)
            print("Success adding Transcription to DB.")

            return db_tsc
        except Exception as e:
            session.rollback()
            raise RuntimeError(f"Error while inserting Transcription to DB: {e}")
        finally:
            session.close()

    async def insert_transcription_chunks(
        self,
        session: Session,
        transcription_chunk_data: TranscriptionChunksSchema
    ):
        """
        Stores a Transcription Chunk object to the db
        """

        db_tsc_chunk = TranscriptionChunk(**transcription_chunk_data.model_dump())

        try:
            session.add(db_tsc_chunk)
            session.commit()
            session.refresh(db_tsc_chunk)
            print("Success adding Transcription Chunk to DB.")

            return db_tsc_chunk
        except Exception as e:
            session.rollback()
            raise RuntimeError(f"Error while inserting Transcription Chunk to DB: {e}")
        finally:
            session.close()

    async def retrieve_formatted_transcription_from_job_name(
        self,
        transcribe_client,
        job_name: str
    ):
        response = await self.get_all_transcriptions(
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

        grouped_items = self.generate_grouped_items_and_format_chunks(items=items)

        response = {
            "jobName": job_name,
            "accountId": accountId,
            "status": status,
            "results": {
                "transcripts": full_transcript, 
                "items": grouped_items
            },
        }

        return response
        
    def generate_grouped_items_and_format_chunks(
        self,
        items: Union[List[TranscriptionChunkItemSchema], None],
    ):
        grouped_items = []
        temp_group = []

        for index, item in enumerate(items):
            if item.get("type") == "pronunciation":
                temp_group.append(item)

                if len(temp_group) == 5 or index == len(items) - 1:
                    contents = " ".join(
                        [i.get("alternatives")[0].get("content") for i in temp_group]
                    )

                    start_time = temp_group[0].get("start_time")
                    end_time = temp_group[-1].get("end_time")
                    duration = float(end_time) - float(start_time)

                    tsc_chunk_formatted: ServiceRetrieveTranscriptionChunkItemSchema = {
                            "content": str(contents),
                            "start_time": str(start_time),
                            "end_time": str(end_time),
                            "duration": "{:.2f}".format(duration),
                        }

                    grouped_items.append(
                        tsc_chunk_formatted
                    )

                    temp_group = []
        
        return grouped_items

    def generate_transcription_chunks(
        self, 
        transcription_id: UUID,
        items: Union[List[ServiceRetrieveTranscriptionChunkItemSchema], None]
    ) -> GenerateTranscriptionChunksResponseSchema:
        """
        Generate TranscriptionChunk objects and total duration
        from a list of ServiceRetrieveTranscriptionChunkItemSchema items
        """
        
        total_duration = 0
        chunks: List[TranscriptionChunksSchema] = []

        for item in items:
            datetime_now_jkt = self.get_datetime_now_jkt()
            chunk_duration = float(item.duration)

            chunk = TranscriptionChunksSchema(
                id=uuid.uuid4(),
                created_at=datetime_now_jkt,
                updated_at=datetime_now_jkt,
                is_deleted=False,
                
                transcription_id=transcription_id,
                content=item.content,
                start_time=float(item.start_time),
                end_time=float(item.end_time),
                duration=chunk_duration,
                is_edited=False,
            )

            chunks += chunk
            total_duration += chunk_duration
        
        response = GenerateTranscriptionChunksResponseSchema(
            duration=total_duration,
            chunks=chunks,
        )

        return response

    async def delete_transcription_job(self, transcribe_client, job_name: str):
        try:
            response = transcribe_client.delete_transcription_job(TranscriptionJobName=job_name)
            return response
        except ClientError as e:
            raise e