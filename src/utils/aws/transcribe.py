import time
import logging
import boto3
import uuid
from typing import Any
from src.utils.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

from botocore.exceptions import ClientError

CLIENT_NAME = "transcribe"
DEFAULT_REGION = "us-west-2"

class AWSTranscribeClient:
  def __init__(self):
    self._transcribe_client = boto3.client(
                                CLIENT_NAME, 
                                aws_access_key_id=AWS_ACCESS_KEY_ID, 
                                aws_secret_access_key=AWS_SECRET_ACCESS_KEY, 
                                region_name=DEFAULT_REGION
                              )
  
  def get_client(self) -> Any:
    return self._transcribe_client