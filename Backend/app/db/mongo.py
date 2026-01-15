import os

from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "moodsync")

client = AsyncIOMotorClient(MONGO_URL)


def get_mongo_db():
    return client[MONGO_DB]
