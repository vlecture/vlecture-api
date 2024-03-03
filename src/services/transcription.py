import http
import time

from botocore.exceptions import ClientError

from src.utils.s3 import AWS_S3_Client
from src.utils.transcribe import AWS_Transcribe_Client


class TranscriptionService:
   POLL_INTERVAL_SEC = 10

   def transcribe_file(self, transcribe_client, job_name, file_uri, file_format = "mp3", language_code = "id-ID"):
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
    
    if "TranscriptionJob" in job:
      return job
    
    return ClientError("TranscriptionJob did not return any results.")