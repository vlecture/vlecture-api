import os
from dotenv import load_dotenv

def get_env_variable(name):
  value = os.getenv(name)
  if value is None and os.environ.get('GITHUB_ACTIONS', False):
    value = os.environ.get(f'secrets.{name}')
  return value

if not os.environ.get('GITHUB_ACTIONS', False):
  load_dotenv(".env", override=True)

ENV_TYPE = os.getenv("ENV")

print(f"ENV: {ENV_TYPE}")

# POSTGRES
POSTGRES_HOST = get_env_variable("POSTGRES_HOST")
POSTGRES_PORT = get_env_variable("POSTGRES_PORT")
POSTGRES_DB = get_env_variable("POSTGRES_DB")
POSTGRES_USER = get_env_variable("POSTGRES_USER")
POSTGRES_PASSWORD = get_env_variable("POSTGRES_PASSWORD")

# TESTDB
TESTDB_URL = get_env_variable("TESTDB_URL")

# MONGO DB
MONGODB_URL = get_env_variable("MONGODB_URL")

MONGODB_DB_NAME = get_env_variable("MONGODB_DB_NAME")
MONGODB_COLLECTION_NAME = get_env_variable("MONGODB_COLLECTION_NAME")

MONGODB_URL_RW = get_env_variable("MONGODB_URL_RW")
MONGODB_URL_MAJORITY = get_env_variable("MONGODB_URL_MAJORITY")
MONGODB_URL_CLUSTER = get_env_variable("MONGODB_URL_CLUSTER")

REFRESH_TOKEN_SECRET = get_env_variable("REFRESH_TOKEN_SECRET")
ACCESS_TOKEN_SECRET = get_env_variable("ACCESS_TOKEN_SECRET")

AWS_BUCKET_NAME = get_env_variable("AWS_BUCKET_NAME")
AWS_ACCESS_KEY_ID = get_env_variable("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = get_env_variable("AWS_SECRET_ACCESS_KEY")

SENTRY_DSN = get_env_variable("SENTRY_DSN")

MAIL_USERNAME = get_env_variable("MAIL_USERNAME")
MAIL_PASSWORD = get_env_variable("MAIL_PASSWORD")
MAIL_FROM = get_env_variable("MAIL_FROM")
MAIL_PORT = get_env_variable("MAIL_PORT")
MAIL_SERVER = get_env_variable("MAIL_SERVER")
MAIL_FROM_NAME = get_env_variable("MAIL_FROM_NAME")
MAIL_STARTTLS = get_env_variable("MAIL_STARTTLS")
MAIL_SSL_TLS = get_env_variable("MAIL_SSL_TLS")
USE_CREDENTIALS = get_env_variable("USE_CREDENTIALS")
VALIDATE_CERTS = get_env_variable("VALIDATE_CERTS")

OTP_SECRET = get_env_variable("OTP_SECRET")
OTP_LIFESPAN_SEC = get_env_variable("OTP_LIFESPAN_SEC")

OPENAI_API_KEY = get_env_variable("OPENAI_API_KEY")
OPENAI_ORG_ID = get_env_variable("OPENAI_ORG_ID")
OPENAI_MODEL_NAME = get_env_variable("OPENAI_MODEL_NAME")

VERY_EASY_DIFF_THRESHOLD = get_env_variable("VERY_EASY_DIFF_THRESHOLD")
EASY_DIFF_THRESHOLD = get_env_variable("EASY_DIFF_THRESHOLD")
MEDIUM_DIFF_THRESHOLD = get_env_variable("MEDIUM_DIFF_THRESHOLD")
HARD_DIFF_THRESHOLD = get_env_variable("HARD_DIFF_THRESHOLD")