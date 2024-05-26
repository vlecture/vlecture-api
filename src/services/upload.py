import mimetypes
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
        self.allowed_types = ["audio/mp4",
                              "audio/mp4a-latm", "audio/x-m4a", "audio/mpeg"]
        self.max_file_size_mb = 100

    def validate_file(self, file):
        # Check file type
        file_type, _ = mimetypes.guess_type(file.filename)
        if file_type not in self.allowed_types:
            raise ValueError("Only MP3 or M4A files are allowed")

        # Validate file size
        file.file.seek(0, 2)  # Move the cursor to the end of the file
        file_size_MB = file.file.tell() / (1024 * 1024)  # Size in MB
        file.file.seek(0)  # Reset the cursor to the start of the file
        if file_size_MB > self.max_file_size_mb:
            raise ValueError(f"File size exceeds the {
                             self.max_file_size_mb} MB limit")

    def upload_file(self, file, filename):
        try:
            self.validate_file(file)
            self.s3_client.upload_fileobj(
                file.file, self.bucket_name, filename)
        finally:
            file.file.close()

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
