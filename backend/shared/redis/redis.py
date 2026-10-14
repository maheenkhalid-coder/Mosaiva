import os
from pathlib import Path

from dotenv import load_dotenv
from redis import asyncio as redis_async

project_root = Path(__file__).resolve().parents[3]
load_dotenv(project_root / ".env")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = redis_async.from_url(REDIS_URL, decode_responses=True)