import sentry_sdk

from fastapi import (
    FastAPI,
)
from fastapi import FastAPI, File, UploadFile, status, Response, HTTPException, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import Enum
from src.utils.settings import (
    SENTRY_DSN,
)
from src.controllers import transcription, auth, upload
from src.utils.db import Base, engine

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
app.include_router(auth.auth_router)
app.include_router(transcription.transcription_router)
app.include_router(upload.upload_router)

# sentry trigger error test, comment when not needed
# @app.get("/sentry-debug")
# async def trigger_error():
#     division_by_zero = 1 / 0

# CORS
origins = [
    "http://localhost:3000",
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

@app.post("/logout", tags=[Tags.auth])
def logout(response: Response, payload: LogoutSchema = Body(), session: Session = Depends(get_db)):
    user = None
    try:
        user = get_user_by_access_token(session=session, access_token=payload.access_token)
        is_active: bool = user.get_is_active()
        if not is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User is not logged in!"
            )
        
        user.clear_token(session)
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return {"message": "Logout successful."}

    except Exception:  
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User is not logged in!"
            )