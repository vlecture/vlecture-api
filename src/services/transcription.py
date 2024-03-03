import uuid
import http
import time
import requests
import json
from os import environ as env

from botocore.exceptions import ClientError

from src.utils.s3 import AWSS3Client
from src.utils.transcribe import AWSTranscribeClient


class TranscriptionService:
   POLL_INTERVAL_SEC = 10

   def generate_job_name(self) -> str:
     return str(uuid.uuid4())

   def generate_file_uri(self, bucket_name: str, filename: str, extension: str):
    #  return f"https://s3-{aws_region}.amazonaws.com/"
    
    # TODO - can add subbuckets in the future
    return f"s3://{bucket_name}/{filename}.{extension}"

   def transcribe_file(self, transcribe_client: any, job_name: str, filename: str, file_format = "mp3", language_code = "id-ID"):
    BUCKET_NAME = env.get("AWS_BUCKET_NAME")
    file_uri = self.generate_file_uri(bucket_name=BUCKET_NAME, filename=filename, extension=file_format)
    
    try:
      transcribe_client.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={
          "MediaFileUri": file_uri
        },
        MediaFormat=file_format,
        LanguageCode=language_code,
      )

      max_tries = 60
      while max_tries > 0:
        max_tries -= 1
        job = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
        job_status = job["TranscriptionJob"]["TranscriptionJobStatus"]
        
        if job_status in ["COMPLETED", "FAILED"]:
          print(f"Job {job_name} is {job_status}.")
          
          if job_status == "COMPLETED":
            print(
              f"Download the transcript from\n"
              f"\t{job['TranscriptionJob']['Transcript']['TranscriptFileUri']}."
            )
          break
        else:
          print(f"Waiting for {job_name}. Current status is {job_status}.")
        
        # Set interval to poll job status
        time.sleep(self.POLL_INTERVAL_SEC)
      
      status = job
      content = requests.get(status['TranscriptionJob']['Transcript']['TranscriptFileUri'])
      res = json.loads(content.content.decode('utf8'))['results']['transcripts'][0]['transcript']
      
      # TODO delete
      print(res)

      return res
    except ClientError:
      return ClientError("Transcription Job failed.")