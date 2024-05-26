import http
import secrets
import string
import pytz
from datetime import datetime, timezone

from fastapi import HTTPException

from sqlalchemy.orm import Session
from fastapi_mail import MessageSchema, MessageType

from src.models.otp import OTP
from src.schemas.auth import EmailSchema, CheckUserExistsSchema, OTPCreateSchema, OTPCheckSchema
from src.utils.mail import get_mail_client
from src.services.users import get_user

TOKEN_LENGTH = 6

class EmailVerificationService:
   def is_user_exists(self, session: Session, payload: CheckUserExistsSchema) -> bool:
    """
    Check whether user exists in database
    """
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

   def localize_to_utc(self, date: datetime):
      """
      Generates UTC timezone-aware `datetime` object
      """
      utc_tz = pytz.timezone("UTC")

      return utc_tz.localize(date)

   def generate_token(self) -> str:
      """
      Generate a crypto-secure 6 digit alphanumeric token
      """
      token = ""

      for _ in range(TOKEN_LENGTH):
         token += str(secrets.choice(string.ascii_uppercase + string.digits))

      return token

   def purge_user_otp(self, session: Session, email: str):
      # Delete all user's OTP from otps table
      deleted_rows = session.query(OTP).filter(OTP.email == email)
      deleted_rows.delete()
      session.commit()
      
      return deleted_rows or None

   def insert_token_to_db(self, session: Session, otp_data: OTPCreateSchema):
      """
      Inserts a token to the OTP table
      """
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
      # finally:
      #    session.close()

   def get_latest_valid_otp(self, session: Session, email: str):
      """
      Get the latest valid OTP for a user's email
      """
      latest_otp = session.query(OTP) \
         .filter(OTP.email == email) \
         .order_by(OTP.created_at.desc()) \
         .first()

      return latest_otp

   def is_token_valid(self, session: Session, otp_check_input: OTPCheckSchema) -> bool:
      """
      Check whether an OTP is consumable or not
      """
      latest_otp = self.get_latest_valid_otp(session, otp_check_input.email)
      
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
       

   async def send_verif_email(self, recipient: EmailSchema, token: str):
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


      message = MessageSchema(
         subject=MESSAGE_SUBJECT,
         recipients=[recipient],
         body=MESSAGE_BODY,
         subtype=MessageType.html,
      )

      client = get_mail_client()

      await client.send_message(message)

      return message

  
   