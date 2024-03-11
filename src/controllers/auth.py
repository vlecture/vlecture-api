import http
from fastapi import (
    APIRouter,
    Response,
    Depends,
    Body,
)
from sqlalchemy import Enum
from sqlalchemy.orm import Session

from src.utils.db import get_db
from src.schemas.base import GenericResponseModel
from src.schemas.auth import RegisterSchema, LoginSchema, EmailSchema

from src.services import auth, email_verification


class AuthRouterTags(Enum):
    auth = "auth"

auth_router = APIRouter(prefix="/v1/auth", tags=[AuthRouterTags.auth])


@auth_router.post("/register", tags=[AuthRouterTags.auth])
def register(payload: RegisterSchema = Body(), session: Session = Depends(get_db)):
    """Processes request to register user account."""
    return auth.register(session, payload=payload)


@auth_router.post("/login", tags=[AuthRouterTags.auth])
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

@auth_router.post("/verify")
async def send_verif_email(payload: EmailSchema = Body()):
    recipients = payload.model_dump().get("email")
    token = email_verification.generate_token()

    response = await email_verification.send_verif_email(
        recipients=recipients,
        token=token,
    )

    print(response)

    return response