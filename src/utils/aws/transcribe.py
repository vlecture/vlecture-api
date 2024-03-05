import time
import logging
import boto3
import uuid
from typing import Any
from os import environ as env

from botocore.exceptions import ClientError

CLIENT_NAME = "transcribe"
DEFAULT_REGION = "us-west-2"

class AWSTranscribeClient:
  def __init__(self):
    self._transcribe_client = boto3.client(
                                CLIENT_NAME, 
                                aws_access_key_id=env.get("AWS_SERVER_PUBLIC_KEY"), 
                                aws_secret_access_key=env.get("AWS_SERVER_SECRET_KEY"), 
                                region_name=DEFAULT_REGION
                              )
  
  def get_client(self) -> Any:
    return self._transcribe_client