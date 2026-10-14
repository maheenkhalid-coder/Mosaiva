import json
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, Response
from firebase_admin import auth as firebase_auth
from firebase_admin.exceptions import FirebaseError
from pymongo.errors import PyMongoError
from redis.exceptions import RedisError

# Importing this module initializes the Firebase Admin app.
from backend.services.auth.config import firebase as _firebase_config
from backend.services.auth.config.db import db
from backend.shared.redis.redis import redis_client


users = db["users"]
SESSION_TTL_SECONDS = 7 * 24 * 60 * 60


async def login(token: str, response: Response):
    # Verify the ID token sent by the React app.
    try:
        decoded = firebase_auth.verify_id_token(token)
    except (FirebaseError, ValueError) as error:
        raise HTTPException(
            status_code=401,
            detail="Google sign-in could not be verified.",
        ) from error

    firebase_uid = decoded["uid"]
    now = datetime.now(timezone.utc)

    # Find or create the MongoDB user.
    try:
        users.update_one(
            {"firebase_uid": firebase_uid},
            {
                "$set": {
                    "name": decoded.get("name"),
                    "email": decoded.get("email"),
                    "avatar": decoded.get("picture"),
                    "updated_at": now,
                },
                "$setOnInsert": {
                    "firebase_uid": firebase_uid,
                    "created_at": now,
                },
            },
            upsert=True,
        )

        user = users.find_one({"firebase_uid": firebase_uid})
    except PyMongoError as error:
        raise HTTPException(
            status_code=503,
            detail="User database is unavailable.",
        ) from error

    if user is None:
        raise HTTPException(status_code=500, detail="Could not load user.")

    # Create a random session ID and store its data in Redis with a 7-day expiry.
    session_id = secrets.token_urlsafe(32)
    session_data = {
        "firebase_uid": firebase_uid,
        "user_id": str(user["_id"]),
        "name": user.get("name"),
        "email": user.get("email"),
        "avatar": user.get("avatar"),
    }

    try:
        await redis_client.set(
            f"session:{session_id}",
            json.dumps(session_data),
            ex=SESSION_TTL_SECONDS,
        )
    except RedisError as error:
        raise HTTPException(
            status_code=503,
            detail="Session storage is unavailable.",
        ) from error

    # The browser stores the session ID; JavaScript cannot read this HttpOnly cookie.
    response.set_cookie(
        key="session",
        value=session_id,
        max_age=SESSION_TTL_SECONDS,
        httponly=True,
        secure=False,  # Local HTTP development; set True in HTTPS production.
        samesite="lax",
    )

    # Don't return MongoDB's internal _id.
    user.pop("_id", None)
    return user


async def logout(session_id: str | None, response: Response):
    if session_id:
        try:
            await redis_client.delete(f"session:{session_id}")
        except RedisError as error:
            raise HTTPException(
                status_code=503,
                detail="Could not end the session because Redis is unavailable.",
            ) from error

    response.delete_cookie(
        key="session",
        httponly=True,
        secure=False,  # Match the setting used when creating it.
        samesite="lax",
    )

    return {"message": "Logout successful"}