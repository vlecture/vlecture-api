import logging
import boto3
from typing import Any
import os

from src.utils.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

from botocore.exceptions import ClientError

CLIENT_NAME = "s3"
DEFAULT_REGION = "us-west-2"

class AWSS3Client:
  def __init__(self):
    self._s3_client = boto3.client(
                        CLIENT_NAME, 
                        aws_access_key_id=AWS_ACCESS_KEY_ID, 
                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY, 
                        region_name=DEFAULT_REGION
                      )
  
  def get_client(self) -> Any:
    return self._s3_client
  
  """https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-uploading-files.html"""
  def upload_file(self, file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = self.get_client()
    try:
        s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True