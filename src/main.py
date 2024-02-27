import mimetypes
from fastapi import FastAPI, File, UploadFile, status, HTTPException, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import Enum
from sqlalchemy.orm import Session

from starlette.status import HTTP_400_BAD_REQUEST
from src.services.audio_file import create_audio_file

from src.utils.db import Base, engine, get_db
from src.schemas.users import CreateUserSchema, UserLoginSchema
from src.schemas.audio_file import AudioFileSchema
from src.models.users import User
from src.services.users import create_user, get_user


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


class Tags(Enum):
    auth = "auth"


@app.get("/")
def root():
    return {"message": "Hello world!"}


@app.get("/hi")
def hi():
    return {"message": "Bonjour!"}


@app.post("/signup", tags=[Tags.auth])
def signup(payload: CreateUserSchema = Body(), session: Session = Depends(get_db)):
    """Processes request to register user account."""
    user = None
    if (
        len(payload.email) == 0
        or len(payload.first_name) == 0
        or (payload.last_name) == 0
        or (payload.hashed_password) == 0
    ):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="All required fields must be filled!",
        )
    try:
        user = get_user(session=session, email=payload.email)
    except Exception:
        payload.hashed_password = User.hash_password(payload.hashed_password)
        return create_user(session, user=payload)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already exists!"
        )
    else:
        payload.hashed_password = User.hash_password(payload.hashed_password)
        return create_user(session, user=payload)


@app.post("/login", tags=[Tags.auth])
def login(payload: UserLoginSchema = Body(), session: Session = Depends(get_db)):
    """Processes user's authentication and returns a token
    on successful authentication.

    request body:

    - email,

    - password
    """
    user = None
    try:
        user = get_user(session=session, email=payload.email)
    except Exception:
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found!"
            )
    else:
        is_validated: bool = user.validate_password(payload.password)
        if not is_validated:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user credentials",
            )

        return user.generate_token()

@app.post('/upload/download')
async def upload_download(payload: AudioFileSchema, file: UploadFile = File(...), db: Session = Depends(get_db)):
    allowed_audio_types = ['audio/mp3', 'audio/mpeg']
    content_type, _ = mimetypes.guess_type(file.filename)
    
    if content_type not in allowed_audio_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Only MP3 or M4A files are allowed"
        )

    data = await file.read()
    new_filename = file.filename

    audio_file_data = payload(filename=new_filename, content_type=content_type, file_content=data)
    return create_audio_file(db, audio_file_data)
