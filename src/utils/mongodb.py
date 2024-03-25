import motor.motor_asyncio

from src.utils.settings import (
  MONGODB_URL,
  MONGODB_DB_NAME,
  MONGODB_COLLECTION_NAME
)

client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
db = client.get_database(MONGODB_DB_NAME)
note_collection = db.get_collection(MONGODB_COLLECTION_NAME)
