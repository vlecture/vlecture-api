import http
import uuid
import secrets
import string
import pytz
import time
from datetime import datetime, timedelta, timezone

from typing import List
from fastapi import HTTPException, Response

from sqlalchemy import delete, insert
from sqlalchemy.orm import Session
from fastapi_mail import MessageSchema, MessageType

from src.models.otp import OTP
from src.schemas.base import GenericResponseModel
from src.schemas.auth import EmailSchema, CheckUserExistsSchema, OTPCreateSchema, OTPCheckSchema
from src.utils.mail import get_mail_client
from src.services.users import create_user, get_user, update_tokens
from src.utils.settings import OTP_LIFESPAN_SEC, OTP_SECRET

TOKEN_LENGTH = 6

def is_user_exists(session: Session, payload: CheckUserExistsSchema) -> bool:
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

def localize_to_utc(date: datetime):
   """
   Generates WIB (Waktu Indonesia Barat) timezone-aware `datetime` object
   """
   utc_tz = pytz.timezone("UTC")

   return utc_tz.localize(datetime)
      

def generate_token() -> str:
    """
    Generate a crypto-secure 6 digit alphanumeric token
    """
    token = ""

    for i in range(TOKEN_LENGTH):
       token += str(secrets.choice(string.ascii_uppercase + string.digits))

    return token

def purge_user_otp(session: Session, email: str):
    # Delete all user's OTP from otps table
    deleted_rows = session.query(OTP).filter(OTP.email == email)
    deleted_rows.delete()
    session.commit()
   
    return deleted_rows or None

def insert_token_to_db(session: Session, otp_data: OTPCreateSchema):
    db_otp = OTP(**otp_data.model_dump())

    try:
        session.add(db_otp)
        session.commit()
        session.refresh(db_otp)
        print("Success adding token to db.")

        return db_otp.__str__()
    except Exception as e:
        print(f"Error while inserting token to DB: {e}")
        session.rollback()
        raise e
    finally:
        session.close()

def get_latest_valid_otp(session: Session, email: str):
    latest_otp = session.query(OTP) \
      .filter(OTP.email == email) \
      .order_by(OTP.created_at.desc()) \
      .first()

    return latest_otp

def is_token_valid(session: Session, otp_check_input: OTPCheckSchema) -> bool:
    latest_otp = get_latest_valid_otp(session, otp_check_input.email)
    
    if latest_otp is None:
       raise Exception("No OTP exists for user object")
    
    # Check if real OTP had expired
    now_in_utc = datetime.now(tz=timezone.utc)

    # If now is past expiry time, then mark token as invalid
    if now_in_utc >= latest_otp.expires_at:
       return False
    
    # Check if token in OTP object matches the real OTP
    if latest_otp.token == otp_check_input.token:
       return True
    
    return False
       

async def send_verif_email(recipient: EmailSchema, token: str):
    """
    Generate token and send verification email to recipient. By default supports one recipient only
    """

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
          recipients=[recipient],
          body=MESSAGE_BODY,
          subtype=MessageType.html,
      )

      client = get_mail_client()

      await client.send_message(message)

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
  
   