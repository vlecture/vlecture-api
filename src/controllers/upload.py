from enum import Enum
import mimetypes
import boto3
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from src.models.users import User
from src.services.users import get_current_user
from src.services.upload import UploadService, sha

from src.utils.settings import AWS_ACCESS_KEY_ID, AWS_BUCKET_NAME, AWS_SECRET_ACCESS_KEY
from starlette.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)


class UploadRouterTags(Enum):
    upload = "upload"


upload_router = APIRouter(prefix="/v1/upload", tags=[UploadRouterTags.upload])


@upload_router.post("")
async def upload_file(
    user: User = Depends(get_current_user), file: UploadFile = File(...)
):
    user_id = user.id
    try:
        allowed_types = ["audio/mp4", "audio/mp4a-latm", "audio/x-m4a", "audio/mpeg"]
        file_type, _ = mimetypes.guess_type(file.filename)

        # NOTE delete
        print(file_type)
        if file_type not in allowed_types:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Only MP3 or M4A files are allowed",
            )

        file_name = str(user_id) + "_" + str(sha()) + "_" + file.filename
        s3_client.upload_fileobj(file.file, AWS_BUCKET_NAME, file_name)
    except HTTPException as e:
        return e
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Error on uploading the file")

    finally:
        file.file.close()

    return {"status_code": HTTP_200_OK, "filename": file_name}


@upload_router.delete("/delete/{filename}")
async def delete_audio(filename: str, user: User = Depends(get_current_user)):
    service =  UploadService(AWS_BUCKET_NAME)
    if not service.check_user_ownership(filename, str(user.id)):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Unauthorized to delete this file"
        )

    try:
        service.delete_file(filename)
    except ValueError as e:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

    return {"status_code": 200, "message": "Successfully deleted the audio file"}
