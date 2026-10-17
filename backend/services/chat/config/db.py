# services/chat/config/db.py sets up the MongoDB connection used by that service.

import os

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
if not MONGODB_URI:
    raise RuntimeError("MONGODB_URI is not set. Add it to the project-root .env file.")

try:
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    db = client["mosaiva"]
    print("MongoDB connected successfully")
except PyMongoError as error:
    print(f"MongoDB connection failed: {error}")
    raise