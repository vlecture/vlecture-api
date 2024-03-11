import os
from dotenv import load_dotenv

load_dotenv(".env")

ENV_TYPE = os.getenv("ENV")
print(f"ENV: {ENV_TYPE}")

host=os.getenv("POSTGRES_HOST")
port=os.getenv("POSTGRES_PORT")
db_name=os.getenv("POSTGRES_DB")
username=os.getenv("POSTGRES_USER")
password=os.getenv("POSTGRES_PASSWORD")

# Check if any DB env vars are None
env_vars = ['host', 'port', 'db_name', 'username', 'password']
values = [os.environ.get(var) for var in env_vars]
none_values = [var for var, val in zip(env_vars, values) if val is None]
if none_values:
    raise ValueError("One or more environment variables for the database configuration are not set: {}".format(', '.join(none_values)))

# Database url configuration
DATABASE_URL = (
    "postgresql+psycopg2://{username}:{password}@{host}:{port}/{db_name}".format(
        host=host,
        port=port,
        db_name=db_name,
        username=username,
        password=password,
    )
)

REFRESH_TOKEN_SECRET = os.getenv("REFRESH_TOKEN_SECRET")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

SENTRY_DSN = os.getenv("SENTRY_DSN")

MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM")
MAIL_PORT = os.getenv("MAIL_PORT")
MAIL_SERVER = os.getenv("MAIL_SERVER")
MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME")
MAIL_STARTTLS = os.getenv("MAIL_STARTTLS")
MAIL_SSL_TLS = os.getenv("MAIL_SSL_TLS")
USE_CREDENTIALS = os.getenv("USE_CREDENTIALS")
VALIDATE_CERTS = os.getenv("VALIDATE_CERTS")

OTP_SECRET = os.getenv("OTP_SECRET")
OTP_LIFESPAN_SEC = os.getenv("OTP_LIFESPAN_SEC")