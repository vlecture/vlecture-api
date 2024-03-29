import http
from fastapi import (
    APIRouter,
    Request,
    Response,
    Depends,
    Body,
)
from sqlalchemy import Enum
from sqlalchemy.orm import Session

from src.utils.db import get_db
from src.schemas.base import GenericResponseModel
from src.schemas.auth import (
  RegisterSchema, 
  LoginSchema, 
  EmailSchema,
  OTPCreateSchema,
  OTPCheckSchema,
  LogoutSchema
)

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
async def send_verif_email(payload: EmailSchema = Body(), session: Session = Depends(get_db)):
    """Checks if user already exists or not, create email and Token based on template, 
    and send it to user

    request body:
    - "email": list of emails to be sent to
    """

    is_user_exists = email_verification.is_user_exists(session=session, payload=payload)

    if (is_user_exists):
        return GenericResponseModel(
            status_code=http.HTTPStatus.CONFLICT,
            error=True,
            message="User already exists",
            data={}
        )
    
    recipient = payload.model_dump().get("email")

    token = email_verification.generate_token()

    otp_create_schema_obj = OTPCreateSchema(
        email=recipient,
        token=token
    )

    email_verification.insert_token_to_db(
        session=session,
        otp_data=otp_create_schema_obj
    )

    response = await email_verification.send_verif_email(
        recipient=recipient,
        token=token,
    )

    return response

@auth_router.post("/verify/check")
def validate_user_token(payload: OTPCheckSchema = Body(), session: Session = Depends(get_db)):
    """Validates a user's inputted token against the generated token

    request body:
    - "token": user-inputted token
    """

    user_email = payload.model_dump().get("email")

    # Check if OTP is valid
    is_answer_valid = email_verification.is_token_valid(
        session=session,
        otp_check_input=payload
    )

    if not is_answer_valid:
        return GenericResponseModel(
            status_code=http.HTTPStatus.UNAUTHORIZED,
            error=True,
            message="The token inputted is invalid",
            data={}
        )
    
    email_verification.purge_user_otp(
        session=session,
        email=user_email
    )

    return GenericResponseModel(
        status_code=http.HTTPStatus.OK,
        error=False,
        message="OTP input is valid",
        data={}
    )
    
    
@auth_router.post("/renew", tags=[AuthRouterTags.auth])
def renew(
    request: Request,
    response: Response,
    session: Session = Depends(get_db),
):
    return auth.renew_access_token(request, response, session)


@auth_router.post("/logout", tags=[AuthRouterTags.auth])
def logout(
    response: Response,
    payload: LogoutSchema = Body(),
    session: Session = Depends(get_db),
):
    """Processes user's logout request."""

    return auth.logout(response, session, payload)