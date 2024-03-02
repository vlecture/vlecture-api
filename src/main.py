from fastapi import FastAPI, status, HTTPException, Depends, Body
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


@app.post("/register", tags=[Tags.auth])
def register(payload: RegisterSchema = Body(), session: Session = Depends(get_db)):
    """Processes request to register user account."""
    try:
        return auth.register(session, payload=payload)
    except HTTPException as err:
        return err


@app.post("/login", tags=[Tags.auth])
def login(payload: LoginSchema = Body(), session: Session = Depends(get_db)):
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
