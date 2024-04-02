import os
from dotenv import load_dotenv

load_dotenv(".env", override=True)

ENV_TYPE = os.getenv("ENV")

print(f"ENV: {ENV_TYPE}")

# POSTGRES
try:
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")
    db_name = os.getenv("POSTGRES_DB")
    username = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")

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

except Exception:
    raise ValueError("Database config values are missing or incorrect.")

# TESTDB
TESTDB_URL = os.getenv("TESTDB_URL")

# MONGO DB
MONGODB_URL = os.getenv("MONGODB_URL")

MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME")
MONGODB_COLLECTION_NAME = os.getenv("MONGODB_COLLECTION_NAME")

MONGODB_URL_RW = os.getenv("MONGODB_URL_RW")
MONGODB_URL_MAJORITY = os.getenv("MONGODB_URL_MAJORITY")
MONGODB_URL_CLUSTER = os.getenv("MONGODB_URL_CLUSTER")

MONGODB_URL = f"{MONGODB_URL_RAW}/?retryWrites={MONGODB_URL_RW}&w={MONGODB_URL_MAJORITY}&appName={MONGODB_URL_CLUSTER}"

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

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ORG_ID = os.getenv("OPENAI_ORG_ID")
OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME")
