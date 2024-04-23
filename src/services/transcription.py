import uuid
from uuid import UUID

import time
import requests
import pytz
from datetime import datetime
from fastapi import (
  Depends
)

from sqlalchemy.orm import Session
from typing import List, Union
from botocore.exceptions import ClientError
from fastapi.encoders import jsonable_encoder

from src.models.users import (
  User
)

from src.services.users import get_current_user

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

from src.utils.time import get_datetime_now_jkt


class TranscriptionService:
  POLL_INTERVAL_SEC = 5  # 5sec  x 3%/sec

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
  
  def fetch_all_transcriptions_chunks_db(
    self,
    session: Session,
    user: User
  ):
    """
    Fetches all user's transcriptions from the database
    """

    if user is None:
        return None
    
    result = []

    # NOTE query optimization

    my_transcriptions = session.query(Transcription) \
                            .filter(Transcription.owner_id == user.id) \
                            .order_by(Transcription.created_at.desc()) \
                            .all()
    
    for tsc in my_transcriptions:
        # Create a new Result object to be put in result array
        related_tsc_chunks = session.query(TranscriptionChunk) \
            .filter(TranscriptionChunk.transcription_id == tsc.id) \
            .order_by(TranscriptionChunk.created_at.asc()) \
            .all()
        
        result_object = {
            "transcription": jsonable_encoder(tsc),
            "chunks": jsonable_encoder(related_tsc_chunks),
        }

        result.append(result_object)

    return result

  def fetch_one_transcriptions_chunks_db(
    self,
    tsc_id: UUID,
    session: Session,
    user: User
  ):
    """
    Fetches all user's transcriptions from the database
    """

    if user is None:
        return None
    
    # NOTE query optimization
    my_transcription = session.query(Transcription) \
                            .filter(Transcription.id == tsc_id) \
                            .order_by(Transcription.created_at.desc()) \
                            .first()
    
    # Create a new Result object to be put in result array
    related_tsc_chunks = session.query(TranscriptionChunk) \
        .filter(TranscriptionChunk.transcription_id == my_transcription.id) \
        .order_by(TranscriptionChunk.created_at.asc()) \
        .all()
        
    result_object = {
        "transcription": jsonable_encoder(my_transcription),
        "chunks": jsonable_encoder(related_tsc_chunks),
    }


    return result_object

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
    except ClientError as e:
      print(e)
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

        return db_tsc_chunk
    except Exception as e:
        session.rollback()
        raise RuntimeError(f"Error while inserting Transcription Chunk to DB: {e}")
    finally:
        session.close()

  async def _fetch_transcription_data(self, transcribe_client, job_name: str):
    response = await self.get_all_transcriptions(
        transcribe_client=transcribe_client, job_name=job_name
    )
    aws_link = requests.get(response)
    return aws_link.json()
  
  # TODO main method
  def convert_chunks_into_full_transcript(
    self, 
    tsc_id: UUID,
    session: Session,
    user: User,
  ):
    transcription_data = self.fetch_one_transcriptions_chunks_db(
      tsc_id=tsc_id,
      session=session,
      user=user,
    )

    # NOTE DELETE - unused
    chunks = transcription_data["chunks"]

    temp_transcripts = []

    for i in range(len(chunks)):
      transcript_text = chunks[i]["content"]
      temp_transcripts.append(transcript_text)
    else:
      print("No transcripts found in the response")

    full_transcript = " ".join(temp_transcripts)

    return full_transcript

  # TODO remove since we have by id 
  async def retrieve_formatted_transcription_from_job_name(
    self, 
    transcribe_client, 
    job_name: str
  ):
    transcription_data = await self._fetch_transcription_data(
        transcribe_client, job_name
    )

    job_name = transcription_data.get("jobName")

    # NOTE DELETE - unused
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
        "results": {"transcripts": full_transcript, "items": grouped_items},
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

          grouped_items.append(tsc_chunk_formatted)

          temp_group = []

    return grouped_items

  def generate_transcription_chunks(
      self,
      transcription_id: UUID,
      items: Union[List[ServiceRetrieveTranscriptionChunkItemSchema], None],
  ) -> GenerateTranscriptionChunksResponseSchema:
    """
    Generate TranscriptionChunk objects and total duration
    from a list of ServiceRetrieveTranscriptionChunkItemSchema items
    """

    total_duration = 0
    chunks: List[TranscriptionChunksSchema] = []

    for item in items:
      datetime_now_jkt = get_datetime_now_jkt()
      chunk_duration = float(item["duration"])

      chunk = TranscriptionChunksSchema(
          id=uuid.uuid4(),
          created_at=datetime_now_jkt,
          updated_at=datetime_now_jkt,
          is_deleted=False,
          transcription_id=transcription_id,
          content=item["content"],
          start_time=float(item["start_time"]),
          end_time=float(item["end_time"]),
          duration=chunk_duration,
          is_edited=False,
      )

      # Use `append` to correctly add the object to chunks list
      chunks.append(chunk)

      total_duration += chunk_duration

    response = GenerateTranscriptionChunksResponseSchema(
      duration=total_duration,
      chunks=chunks,
    )

    return response

  async def delete_transcription_job(self, transcribe_client, job_name: str):
    try:
      response = transcribe_client.delete_transcription_job(
          TranscriptionJobName=job_name
      )
      return response
    except ClientError as e:
      raise e
