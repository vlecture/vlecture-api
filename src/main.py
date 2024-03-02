from fastapi import FastAPI, Response, status, HTTPException, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import Enum
from sqlalchemy.orm import Session


from src.utils.db import Base, engine, get_db
from src.schemas.auth import RegisterSchema, LoginSchema
from src.services.users import get_user
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
