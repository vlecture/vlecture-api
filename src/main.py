import sentry_sdk
import certifi

from fastapi import (
    FastAPI,
)

from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson.binary import UuidRepresentation

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy import Enum
from src.utils.settings import (
    SENTRY_DSN,
    MONGODB_URL,
    MONGODB_DB_NAME,
    MONGODB_COLLECTION_NAME,
)
from src.controllers import (
    transcription, 
    auth, 
    upload, 
    waitlist,
    note,
    flashcards
)
from src.utils.db import Base, engine


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

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://vlecture.tech",
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
    allow_headers=[
        "Accept",
        "Authorization",
        "Cache-Control",
        "Content-Type",
        "DNT",
        "If-Modified-Since",
        "Keep-Alive",
        "Origin",
        "User-Agent",
        "X-Requested-With",
    ],
)

# Include routers after CORS middleware
app.include_router(auth.auth_router)
app.include_router(transcription.transcription_router)
app.include_router(upload.upload_router)
app.include_router(waitlist.waitlist_router)
app.include_router(note.note_router)
app.include_router(flashcards.flashcards_router)


# Connect to MongoDB on startup
@app.on_event("startup")
def startup_mongodb_client():
    client = MongoClient(
        MONGODB_URL,
        server_api=ServerApi('1'),

        # MongoClient Configs
        uuidRepresentation="standard",
        tlsCAFile=certifi.where(),
    )

    try:
        client.admin.command('ping')
        print("Pinged your deployment. Successfully connected to MongoDB!")

        # Assign MongoDB client to FastAPI app
        app.mongodb_client = client
        app.database = app.mongodb_client.get_database(MONGODB_DB_NAME)
        app.note_collection = app.database.get_collection(MONGODB_COLLECTION_NAME)
        
        print("Connected to MongoDB Database.")
    except Exception as e:
        print(e)
 
@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()
    print("Closed MongoDB Connection")


# sentry trigger error test, comment when not needed
# @app.get("/sentry-debug")
# async def trigger_error():
#     division_by_zero = 1 / 0

Base.metadata.create_all(bind=engine)


class Tags(Enum):
    auth = "auth"


@app.get("/")
def root():
    return {"message": "Hello world!"}


@app.get("/hi")
def hi():
    return {"message": "Bonjour!"}