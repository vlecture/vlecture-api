import pytest
import certifi

import pymongo
from pymongo.server_api import ServerApi

from src.utils.settings import (
    MONGODB_URL,
)

@pytest.fixture(scope="session")
def mongo_test_db():
    db = pymongo.MongoClient(
        MONGODB_URL,
        server_api=ServerApi('1'),

        # MongoClient Configs
        uuidRepresentation='standard',
        tlsCAFile=certifi.where()
    )
    
    return db

