import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.utils.settings import DATABASE_URL
from src.utils.db import Base


@pytest.fixture(scope="function")
def test_db_session():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_session = TestingSessionLocal()
    yield db_session
    db_session.rollback()
    db_session.close()
    Base.metadata.drop_all(bind=engine)
