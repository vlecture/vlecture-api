import uuid
import http
import time
import requests
import json

from typing import List, Union
from botocore.exceptions import ClientError

from src.schemas.transcription import TranscriptionChunkItemSchema


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

    async def store_transcription_result(
        self, 
        transcription_job_response
    ):
        pass

    async def retrieve_transcription_from_job_name(
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

        grouped_items = self.generate_grouped_items(items=items)

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
        
    def generate_grouped_items(
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

                    grouped_items.append(
                        {
                            "content": contents,
                            "start_time": start_time,
                            "end_time": end_time,
                            "duration": "{:.2f}".format(duration),
                        }
                    )

                    temp_group = []
        
        return grouped_items

    async def delete_transcription_job(self, transcribe_client, job_name: str):
        try:
            response = transcribe_client.delete_transcription_job(TranscriptionJobName=job_name)
            return response
        except ClientError as e:
            raise e