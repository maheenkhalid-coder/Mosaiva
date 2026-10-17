from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class MessageCreate(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class MessageDocument(MessageCreate):
    conversation_id: str
    created_at: datetime = Field(default_factory=utc_now)