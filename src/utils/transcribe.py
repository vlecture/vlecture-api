import time
import logging
import boto3
import uuid
from typing import Any
from botocore.exceptions import ClientError

CLIENT_NAME = "transcribe"
DEFAULT_REGION = "us-west-2"

class AWSTranscribeClient:
  def __init__(self):
    self._transcribe_client = boto3.client(CLIENT_NAME)
  
  def get_client(self) -> Any:
    return self._transcribe_client