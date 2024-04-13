from src.utils.settings import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

try:
    # Database url configuration
    DATABASE_URL = (
        "postgresql+psycopg2://{username}:{password}@{host}:{port}/{db_name}".format(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            db_name=POSTGRES_DB,
            username=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
        )
    )

except Exception:
    raise ValueError("Database config values are missing or incorrect.")

if DATABASE_URL is None:
    raise ValueError("DB_URL environment variable is not set!")

print(POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
