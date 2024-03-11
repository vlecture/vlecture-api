import http
from typing import List
from fastapi import HTTPException, Response

from sqlalchemy.orm import Session
from fastapi_mail import MessageSchema, MessageType

from src.schemas.base import GenericResponseModel
from src.schemas.auth import EmailSchema, CheckUserExistsSchema
from src.utils.mail import get_mail_client
from src.services.users import create_user, get_user, update_tokens

def verify_user_exists(session: Session, payload: CheckUserExistsSchema):
    user = None

    if (len(payload.email) == 0):
       raise HTTPException(
          status_code=http.HTTPStatus.UNPROCESSABLE_ENTITY,
          detail="Email field must be filled!"
       )

    try:
       user = get_user(session=session, email=payload.email.lower())
    except Exception:
       return False
    
    if user:
       return True
    else:
      return False
   

def generate_token():
    token = "EXAMPLE"

    return token
    

async def send_verif_email(recipients: List[EmailSchema], token: str):
    MESSAGE_SUBJECT = "Your vlecture.tech verification token"

    MESSAGE_BODY = f"""
    <h2>
      Hi! We noticed you're trying to register to vlecture
    </h2>

    <p>
      Your verification token is 
      <b>
        {token}.
      </b>
    </p>

    <p>
      Please insert it on the verification screen on the app.
    </p>

    <br>
      Thanks,
    <br>
      vlecture team
    """


    try:
      message = MessageSchema(
          subject=MESSAGE_SUBJECT,
          recipients=recipients,
          body=MESSAGE_BODY,
          subtype=MessageType.html,
      )

      client = get_mail_client()

      response = await client.send_message(message)

      print(f"send email repsonse: {response}\n")

      return GenericResponseModel(
          status_code=http.HTTPStatus.OK,
          message="Email has been sent",
          error=False,
          data=None,
      )
    except ValueError:
       return GenericResponseModel(
          status_code=http.HTTPStatus.BAD_REQUEST,
          error=True,
          message="Invalid value when sending email.",
          data={},
       )
    except Exception:
       return GenericResponseModel(
          status_code=http.HTTPStatus.BAD_REQUEST,
          error=True,
          message="Unknown error while sending email",
          data={},
       )
  
# def validate_token(user_token: str):
   