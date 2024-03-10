import os
from dotenv import load_dotenv

ENV_TYPE = os.getenv("ENV")

if ENV_TYPE == "DEV":
    load_dotenv(".env.dev")
else:
    # Prod
    load_dotenv(".env")

host = os.getenv("POSTGRES_HOST")
port = os.getenv("POSTGRES_PORT")
db_name = os.getenv("POSTGRES_DB")
username = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")

if None in [host, port, db_name, username, password]:
    raise ValueError(
        "One or more environment variables for the database configuration are not set"
    )

# Database url configuration
DATABASE_URL = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{db_name}"

REFRESH_TOKEN_SECRET = os.getenv("REFRESH_TOKEN_SECRET")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

SENTRY_DSN = os.getenv("SENTRY_DSN")
