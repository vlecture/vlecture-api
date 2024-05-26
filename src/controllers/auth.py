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

from src.models.users import User
from src.services.users import get_current_user
from src.utils.db import get_db
from src.schemas.auth import (
    RegisterSchema,
    LoginSchema,
    EmailSchema,
    OTPCreateSchema,
    OTPCheckSchema,
    LogoutSchema,
)
from starlette.status import HTTP_200_OK
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from src.services import auth
from src.services.email_verification import EmailVerificationService


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
async def send_verif_email(
    payload: EmailSchema = Body(), session: Session = Depends(get_db)
):
    """Checks if user already exists or not, create email and Token based on template,
    and send it to user

    request body:
    - "email": list of emails to be sent to
    """

    service = EmailVerificationService()

    is_user_exists = service.is_user_exists(session=session, payload=payload)

    if is_user_exists:
        return JSONResponse(
            status_code=http.HTTPStatus.CONFLICT, content="Error: User already exists!"
        )

    recipient = payload.model_dump().get("email")

    token = service.generate_token()

    otp_create_schema_obj = OTPCreateSchema(email=recipient, token=token)

    try:
        service.purge_user_otp(session=session, email=recipient)
        service.insert_token_to_db(session=session, otp_data=otp_create_schema_obj)

        response = await service.send_verif_email(
            recipient=recipient,
            token=token,
        )

        return JSONResponse(
            status_code=http.HTTPStatus.OK, content=jsonable_encoder(response)
        )
    except ValueError:
        return JSONResponse(
            status_code=http.HTTPStatus.UNPROCESSABLE_ENTITY,
            content="Error: Invalid value when sending email.",
        )
    except Exception:
        return JSONResponse(
            status_code=http.HTTPStatus.BAD_REQUEST,
            content="Error: Unknown problem while sending email.",
        )


@auth_router.post("/verify/check")
def validate_user_token(
    payload: OTPCheckSchema = Body(), session: Session = Depends(get_db)
):
    """Validates a user's inputted token against the generated token

    request body:
    - "token": user-inputted token
    """

    service = EmailVerificationService()

    user_email = payload.model_dump().get("email")

    # Check if OTP is valid
    is_answer_valid = service.is_token_valid(session=session, otp_check_input=payload)

    if not is_answer_valid:
        return JSONResponse(
            status_code=http.HTTPStatus.UNAUTHORIZED,
            content="Error: The inputted token is invalid.",
        )

    service.purge_user_otp(session=session, email=user_email)

    return JSONResponse(status_code=http.HTTPStatus.OK, content="OTP input is valid.")


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

@auth_router.get("/name", tags=[AuthRouterTags.auth])
def get_username( 
    user: User = Depends(get_current_user),
):
    if not user:
        return JSONResponse(
            status_code=http.HTTPStatus.UNAUTHORIZED,
            content="Unauthorized. Please log in."
        )
    
    return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "email":user.email,
        }
    )

@auth_router.get("/verify_token", tags=[AuthRouterTags.auth])
def verify(
    request: Request,
    session: Session = Depends(get_db),
):
    return auth.verify_access_token(request, session)

@auth_router.post("/email-exist", tags=[AuthRouterTags])
async def email_check(
    payload: EmailSchema = Body(),
    session: Session = Depends(get_db),
):
    service = EmailVerificationService()

    is_user_exists = service.is_user_exists(session=session, payload=payload)

    if is_user_exists:
        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "status" : True,
            }
        )
    
    return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "status" : False,
            }
    )
