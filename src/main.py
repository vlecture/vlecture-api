import sentry_sdk

from fastapi import (
    FastAPI,
)
from fastapi import FastAPI, File, UploadFile, status, Response, HTTPException, Depends, Body
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from sqlalchemy import Enum
from src.utils.settings import (
    SENTRY_DSN,
)
from src.controllers import transcription, auth, upload
from src.utils.db import Base, engine

from src.schemas.auth import LogoutSchema
from src.models.users import User
from src.services.users import get_user_by_access_token

# Create middleware before init FastAPI server
mdw = [
    Middleware(
        CORSMiddleware,
        allow_origins=[
            "https://app.vlecture.tech",
            "https://staging.app.vlecture.tech",
            "https://api.vlecture.tech",
            "https://staging.api.vlecture.tech",
            "http://localhost",
            "http://localhost:3000",
            "http://localhost:8080",
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
]

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

app = FastAPI(middleware=mdw)
app.include_router(auth.auth_router)
app.include_router(transcription.transcription_router)
app.include_router(upload.upload_router)

# sentry trigger error test, comment when not needed
# @app.get("/sentry-debug")
# async def trigger_error():
#     division_by_zero = 1 / 0

# CORS
# origins = [
#     "https://app.vlecture.tech",
#     "https://staging.app.vlecture.tech",
#     "https://api.vlecture.tech",
#     "https://staging.api.vlecture.tech",
#     "http://localhost",
#     "http://localhost:3000",
#     "http://localhost:8080",
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "https://app.vlecture.tech",
#         "https://staging.app.vlecture.tech",
#         "https://api.vlecture.tech",
#         "https://staging.api.vlecture.tech",
#         "http://localhost",
#         "http://localhost:3000",
#         "http://localhost:8080",
#     ],
#     allow_credentials=True,
#     allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
#     allow_headers=["*"],
# )

Base.metadata.create_all(bind=engine)


class Tags(Enum):
    auth = "auth"


@app.get("/")
def root():
    return {"message": "Hello world!"}


@app.get("/hi")
def hi():
    return {"message": "Bonjour!"}
