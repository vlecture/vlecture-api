
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from src.utils.settings import (
  MAIL_USERNAME,
  MAIL_PASSWORD,
  MAIL_FROM,
  MAIL_SERVER,
  MAIL_PORT,
  MAIL_FROM_NAME,
  MAIL_STARTTLS,
  MAIL_SSL_TLS,
  USE_CREDENTIALS,
  VALIDATE_CERTS
)
from src.schemas.auth import EmailSchema

conf = ConnectionConfig(
  MAIL_USERNAME=MAIL_USERNAME,
  MAIL_PASSWORD=MAIL_PASSWORD,
  MAIL_FROM=MAIL_FROM,
  MAIL_PORT=MAIL_PORT,
  MAIL_SERVER=MAIL_SERVER,
  MAIL_FROM_NAME=MAIL_FROM_NAME,
  MAIL_STARTTLS=MAIL_STARTTLS,
  MAIL_SSL_TLS=MAIL_SSL_TLS,
  USE_CREDENTIALS=USE_CREDENTIALS,
  VALIDATE_CERTS=VALIDATE_CERTS,
)

def get_mail_client():
  mail_client = FastMail(conf)
  
  return mail_client

