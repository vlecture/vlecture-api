import secrets
import string
from botocore.exceptions import ClientError
import boto3

def sha():
    sha = ""
    for _ in range(6):
        x = secrets.randbelow(2)
        if x == 0:
            sha += str(secrets.randbelow(10))
        else:
            sha += secrets.choice(string.ascii_lowercase)

    return sha

class UploadService:
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name
        self.s3_client = boto3.client('s3')

    def check_user_ownership(self, filename, user_id):
        uuid_from_filename = filename.split('_')[0]
        return uuid_from_filename == user_id

    def delete_file(self, filename):
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=filename)
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=filename)
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey' or e.response['Error']['Code'] == '404':
                raise ValueError("File not found")
            else:
                raise
        except Exception as e:
            raise RuntimeError(f"Unexpected server error: {str(e)}")
