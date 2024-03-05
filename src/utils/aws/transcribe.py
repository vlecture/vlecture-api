import time
import logging
import boto3
import uuid
from typing import Any
import os
from dotenv import load_dotenv

load_dotenv()

from botocore.exceptions import ClientError

CLIENT_NAME = "transcribe"
DEFAULT_REGION = "us-west-2"

class AWSTranscribeClient:
  def __init__(self):
    self._transcribe_client = boto3.client(
                                CLIENT_NAME, 
                                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"), 
                                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"), 
                                region_name=DEFAULT_REGION
                              )
  
  def get_client(self) -> Any:
    return self._transcribe_client