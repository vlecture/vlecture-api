import http
import uuid
import secrets
import string
import time
from datetime import datetime, timedelta

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
   

def generate_token() -> str:
    """
    Generate a crypto-secure 6 digit alphanumeric token
    """
    token = ""

    for i in range(TOKEN_LENGTH):
       token += str(secrets.choice(string.ascii_uppercase + string.digits))

    return token

def purge_user_otp(session: Session, email: str):
    if is_user_exists(session, payload={ "email": email }) == False:
        return
   
    #  Else, delete all user's OTP from db
    delete_statement = delete(OTP).where(OTP.email.in_([email]))

    session.execute(delete_statement)
   
    return None

def insert_token_to_db(session: Session, otp_data: OTPCreateSchema):
    # otp_data_dict = otp_data.model_dump()
    
    db_otp = OTP(**otp_data.model_dump())
    {
       id: Null,
       email: "adavalue@",
       token: "ABC",
       created_at: Null,
       expires_at: Null
    }
    try:
        # with session.begin_nested():

            # insert_stmt = insert(OTP).values(
            #     id=uuid.uuid4(),
            #     email=otp_data_dict["email"],
            #     token=otp_data_dict["token"],
            #     created_at=datetime.now(),
            #     expires_at=datetime.now() + timedelta(seconds=int(OTP_LIFESPAN_SEC))
            # )

            # session.execute(insert_stmt)

        session.add(db_otp)
        session.commit()
        session.refresh(db_otp)
        print("Added token to db.")

        return db_otp.__str__()
    except Exception as e:
        print(f"Error: {e}")
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
       print("latest_otp == None")
       raise Exception("No OTP exists for user object")
    else: 
       print(f"latest_otp found: {latest_otp}")
    
    # Check if real OTP had expired
    if latest_otp.expires_at >= datetime.now():
       return False
    
    # Check if user OTP matches the real OTP
    if latest_otp == otp_check_input.token:
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
  
   