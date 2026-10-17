from datetime import datetime, timezone

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ConversationCreate(BaseModel):
    title: str = "New Chat"
    user_id: str


class ConversationDocument(ConversationCreate):
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

class ConversationTitleUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=200)