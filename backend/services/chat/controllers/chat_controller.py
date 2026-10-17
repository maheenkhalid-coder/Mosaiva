from datetime import datetime, timezone

from bson import ObjectId
from fastapi import HTTPException
from pymongo import ReturnDocument


from backend.services.chat.config.db import db
from backend.services.chat.models.message import MessageCreate
from backend.services.chat.models.conversation import ConversationTitleUpdate


conversations = db["conversations"]
messages = db["messages"]

def create_conversation(user_id: str) -> dict:
    now = datetime.now(timezone.utc)

    conversation = {
        "title": "New Chat",
        "user_id": user_id,
        "created_at": now,
        "updated_at": now,
    }

    result = conversations.insert_one(conversation)
    conversation["_id"] = str(result.inserted_id)
    return conversation


def get_conversations(user_id: str) -> list[dict]:
    results = conversations.find({"user_id": user_id}).sort("updated_at", -1)

    return [
        {**conversation, "_id": str(conversation["_id"])}
        for conversation in results
    ]

def update_conversation_title(
    conversation_id: str,
    user_id: str,
    update: ConversationTitleUpdate,
) -> dict:
    if not ObjectId.is_valid(conversation_id):
        raise HTTPException(status_code=400, detail="Invalid conversation ID")

    updated = conversations.find_one_and_update(
        {
            "_id": ObjectId(conversation_id),
            "user_id": user_id,
        },
        {
            "$set": {
                "title": update.title,
                "updated_at": datetime.now(timezone.utc),
            }
        },
        return_document=ReturnDocument.AFTER,
    )

    if not updated:
        raise HTTPException(status_code=404, detail="Conversation not found")

    updated["_id"] = str(updated["_id"])
    return updated

def save_message(
    conversation_id: str,
    user_id: str,
    message: MessageCreate,
) -> dict:
    if not ObjectId.is_valid(conversation_id):
        raise HTTPException(status_code=400, detail="Invalid conversation ID")

    mongo_conversation_id = ObjectId(conversation_id)

    # Confirm this user owns the conversation.
    conversation = conversations.find_one(
        {"_id": mongo_conversation_id, "user_id": user_id}
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    saved_message = {
        "conversation_id": mongo_conversation_id,
        "role": message.role,
        "content": message.content,
        "created_at": datetime.now(timezone.utc),
    }

    result = messages.insert_one(saved_message)
    saved_message["_id"] = str(result.inserted_id)
    saved_message["conversation_id"] = str(mongo_conversation_id)

    conversations.update_one(
        {"_id": mongo_conversation_id},
        {"$set": {"updated_at": datetime.now(timezone.utc)}},
    )

    return saved_message


def get_messages(conversation_id: str, user_id: str) -> list[dict]:
    if not ObjectId.is_valid(conversation_id):
        raise HTTPException(status_code=400, detail="Invalid conversation ID")

    mongo_conversation_id = ObjectId(conversation_id)

    # Confirm this user owns the conversation.
    conversation = conversations.find_one(
        {"_id": mongo_conversation_id, "user_id": user_id}
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    stored_messages = messages.find(
        {"conversation_id": mongo_conversation_id}
    ).sort("created_at", 1)

    return [
        {
            **message,
            "_id": str(message["_id"]),
            "conversation_id": str(message["conversation_id"]),
        }
        for message in stored_messages
    ]