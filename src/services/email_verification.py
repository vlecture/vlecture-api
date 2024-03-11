import http
from typing import List
from fastapi_mail import MessageSchema, MessageType

from src.schemas.base import GenericResponseModel
from src.schemas.auth import EmailSchema
from src.utils.mail import get_mail_client

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
   