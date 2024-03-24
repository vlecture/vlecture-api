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

            # Grab the transcription text
            # content = requests.get(job_result['TranscriptionJob']['Transcript']['TranscriptFileUri'])
            # res = json.loads(content.content.decode('utf8'))['results']['transcripts'][0]['transcript']

            # return res
        except TimeoutError:
            return TimeoutError("Timeout when polling the transcription results")
        except ClientError:
            raise RuntimeError("Transcription Job failed.")

    # TODO debug - Helper function
    # def extract_query_params_from_transcribe_url(self, query_param_part: str) -> dict:
    #     KV_PAIR_DELIM = "&"
    #     KEY_VALUE_DELIM = "="

    #     query_params = {}

    #     query_param_splitted = query_param_part.split(KV_PAIR_DELIM)

    #     for kv_pair in query_param_splitted:
    #         # Split pair based on "="
    #         [key, value] = kv_pair.split(KEY_VALUE_DELIM)

    #         # Construct query_params key-value pair
    #         query_params[key] = value

    #     # Extra steps: Format, %2F -> "/" to avoid "Malformed Error"
    #     query_params["X-Amz-Credential"] = query_params["X-Amz-Credential"].replace(r"%2F", "/")

    #     return query_params

    # async def store_transcription_result(
    #     self, 
    #     transcription_job_response
    # ):
    #     try:
    #         URI_DELIMITER = "?"
            
    #         # Fetch Transcription JSON file using custom URL path and Headers
    #         transcript_file_uri = transcription_job_response["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]
            
    #         # Split by "="
    #         res_path, res_query_params = transcript_file_uri.split(URI_DELIMITER)

    #         query_params = self.extract_query_params_from_transcribe_url(res_query_params)

    #         print(f"\nquery_params: {query_params}\n\n")

    #         # Send GET request to AWS Endpoint (valid for 15 mins since completion time)
    #         response = requests.get(
    #             # url=res_path, 
    #             url=transcript_file_uri,
    #             # params=query_params,
    #         )

    #         data = {}

    #         print(f"store_transcription_result: {response.__str__()}")
    #         print(f"url: {response.url}")
            
    #         if (response.json()):
    #             data = response.json()
    #             print(f"json: {data}")

    #         # TODO store to db async-ly

    #         # TODO remove
    #         return data
    #     except Exception as e:
    #         print(e)
    #         raise RuntimeError("Failed to save transcription")

    

    async def store_transcription_result(
        self, 
        transcription_job_response
    ):
        pass

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