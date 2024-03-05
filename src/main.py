import mimetypes
import boto3
from fastapi import (
    FastAPI,
    File,
    UploadFile,
    status,
    Response,
    HTTPException,
    Depends,
    Body,
)
from fastapi import FastAPI, File, UploadFile, status, Response, HTTPException, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import Enum
from sqlalchemy.orm import Session

import sentry_sdk

from src.utils.settings import (
    AWS_ACCESS_KEY_ID,
    AWS_BUCKET_NAME,
    AWS_SECRET_ACCESS_KEY,
    SENTRY_DSN,
)
from src.utils.db import Base, engine, get_db
from src.schemas.auth import RegisterSchema, LoginSchema
from src.services import auth
from src.schemas.auth import LogoutSchema
from src.models.users import User
from src.services.users import get_user_by_access_token

sentry_sdk.init(
    dsn=SENTRY_DSN,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # Sentry recommends adjusting this value in production.
    profiles_sample_rate=1.0,
)

app = FastAPI()

# sentry trigger error test, comment when not needed
# @app.get("/sentry-debug")
# async def trigger_error():
#     division_by_zero = 1 / 0

# CORS
origins = [
    "http://localhost",
    "http://localhost:8080",
    "api.vlecture.com",
    "vlecture-api-production.up.railway.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)


class Tags(Enum):
    auth = "auth"


@app.get("/")
def root():
    return {"message": "Hello world!"}


@app.get("/hi")
def hi():
    return {"message": "Bonjour!"}


# Authentication Endpoints


@app.post("/register", tags=[Tags.auth])
def register(payload: RegisterSchema = Body(), session: Session = Depends(get_db)):
    """Processes request to register user account."""
    return auth.register(session, payload=payload)


@app.post("/login", tags=[Tags.auth])
def login(
    response: Response,
    payload: LoginSchema = Body(),
    session: Session = Depends(get_db),
):
    """Processes user's authentication and returns a token
    on successful authentication.

    request body:
    - email,
    - password
    """
    return auth.login(response, session, payload)


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        allowed_types = ["audio/mp3", "audio/mpeg"]
        file_type, _ = mimetypes.guess_type(file.filename)
        if file_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only MP3 or M4A files are allowed",
            )

        s3_client.upload_fileobj(file.file, AWS_BUCKET_NAME, file.filename)

    except HTTPException as e:
        return e

    except Exception as e:
        print("Error:", str(e))
        raise HTTPException(status_code=500, detail="Error on uploading the file")

    finally:
        file.file.close()

    return {"filename": file.filename}

@app.post("/logout", tags=[Tags.auth])
def logout(response: Response, payload: LogoutSchema = Body(), session: Session = Depends(get_db)):
    user = None
    try:
        user = get_user_by_access_token(session=session, email=payload.access_token)
        # is_active: bool = user.is_active()
        # if not is_active:
        #     raise HTTPException(
        #         status_code=status.HTTP_401_UNAUTHORIZED,
        #         detail="User is already inactive.",
        #     )
        
        user.clear_token()
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return {"message": "Logout successful."}

    except Exception:  
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User is not logged in!"
            )
        
@app.post("/check", tags=[Tags.auth])      
def check_logged_in_user_by_token(payload: LogoutSchema, session: Session = Depends(get_db)):
    user = None
    try:
        user = get_user_by_access_token(session=session, email=payload.access_token)
        return {"message": "User is still logged in"}
    
    except Exception:
        if user is None:
            return {"message": "User has logged out"}