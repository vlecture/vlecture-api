import mimetypes
import boto3
from fastapi import FastAPI, File, UploadFile, status, Response, HTTPException, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import Enum
from sqlalchemy.orm import Session

from src.utils.settings import AWS_ACCESS_KEY_ID, AWS_BUCKET_NAME, AWS_SECRET_ACCESS_KEY
from src.utils.db import Base, engine, get_db

from src.utils.db import Base, engine, get_db
from src.schemas.auth import RegisterSchema, LoginSchema
from src.services import auth


app = FastAPI()

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
    "s3", aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)


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
    try:
        return auth.register(session, payload=payload)
    except HTTPException as err:
        return err


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
    try:
        return auth.login(response, session, payload)
    except HTTPException as err:
        return err

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        allowed_types = ['audio/mp3', 'audio/mpeg']
        file_type, _ = mimetypes.guess_type(file.filename)
        if file_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Only MP3 or M4A files are allowed"
            )

        s3_client.upload_fileobj(file.file, AWS_BUCKET_NAME,  file.filename)

    except HTTPException as e:
        return e

    except Exception as e:
        print("Error:", str(e))
        raise HTTPException(
            status_code=500, detail='Error on uploading the file')

    finally:
        file.file.close()

    return {"filename": file.filename}