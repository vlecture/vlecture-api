from fastapi import FastAPI, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from src.routes.routes import router
from src.utils.db import Base, engine, get_db
from src.schemas.users import CreateUserSchema
from src.models.users import User
from src.services.users import create_user


app = FastAPI()
app.include_router(router)

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


@app.get("/")
def root():
    return {"message": "Hello world!"}


@app.get("/hi")
def hi():
    return {"message": "Bonjour!"}


@app.post("/signup", tags=["auth"])
def signup(payload: CreateUserSchema = Body(), session: Session = Depends(get_db)):
    """Processes request to register user account."""
    payload.hashed_password = User.hash_password(payload.hashed_password)
    return create_user(session, user=payload)
