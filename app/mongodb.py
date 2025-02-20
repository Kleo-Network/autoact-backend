# app/mongodb.py
import motor.motor_asyncio  # type: ignore
import time
from app.settings import settings

class SimpleCache:
    def __init__(self, ttl=60000, limit=3000):
        self.cache = {}
        self.limit = limit
        self.ttl = ttl  # Time-to-live in seconds

    def purge(self):
        print("purging")
        for key, data in self.cache.items():
            if time.time() - data['time'] > self.ttl:
                self.cache.pop(key, None)


    def get(self, key):
        data = self.cache.get(key)
        if data and (time.time() - data['time'] < self.ttl):
            return data['value']
        else:
            self.cache.pop(key, None)
            return None

    def set(self, key, value):
        self.cache[key] = {'value': value, 'time': time.time()}
        if len(self.cache) > self.limit:
            self.purge()


class MongoDBClient:
    _client = None
    _cache = None

    @classmethod
    def get_client(cls):
        if cls._client is None:
            cls._client = motor.motor_asyncio.AsyncIOMotorClient(settings.DB_URL)
        return cls._client

    @classmethod
    def get_cache(cls):
        if cls._cache is None:
            cls._cache = SimpleCache(ttl=60000)
        return cls._cache

def get_db_cache():
    return MongoDBClient.get_cache()

def get_database():
    client = MongoDBClient.get_client()
    return client[settings.DB_NAME]

def get_forms():
    db = get_database()
    return db["forms"]


async def close_db_connection():
    """
    Close the MongoDB client connection.
    """
    if MongoDBClient._client is not None:
        MongoDBClient._client.close()
        MongoDBClient._client = None
    else:
        print("MongoDB client is not initialized.")
