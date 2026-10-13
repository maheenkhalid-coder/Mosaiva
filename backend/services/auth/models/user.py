from datetime import datetime, timezone

from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    name: str
    email: EmailStr
    avatar: str | None = None
    firebase_uid: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))