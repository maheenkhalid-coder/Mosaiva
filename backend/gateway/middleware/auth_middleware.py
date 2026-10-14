import json

from fastapi import HTTPException, Request
from redis.exceptions import RedisError

from backend.shared.redis.redis import redis_client


async def get_current_user(request: Request) -> dict:
    session_id = request.cookies.get("session")

    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        session_data = await redis_client.get(f"session:{session_id}")
    except RedisError as error:
        raise HTTPException(
            status_code=503,
            detail="Session service unavailable",
        ) from error

    if not session_data:
        raise HTTPException(status_code=401, detail="Session expired")

    try:
        return json.loads(session_data)
    except json.JSONDecodeError as error:
        raise HTTPException(
            status_code=401,
            detail="Invalid session",
        ) from error