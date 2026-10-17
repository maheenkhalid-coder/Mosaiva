from fastapi import APIRouter, Header

from backend.services.chat.controllers.chat_controller import (
    create_conversation,
    get_conversations,
    get_messages,
    save_message,
    update_conversation_title,
)
from backend.services.chat.models.message import MessageCreate
from backend.services.chat.models.conversation import ConversationTitleUpdate


router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("")
def create_conversation_route(
    user_id: str = Header(..., alias="x-user-id"),
):
    return create_conversation(user_id)


@router.get("")
def get_conversations_route(
    user_id: str = Header(..., alias="x-user-id"),
):
    return get_conversations(user_id)


@router.post("/{conversation_id}/messages")
def save_message_route(
    conversation_id: str,
    message: MessageCreate,
    user_id: str = Header(..., alias="x-user-id"),
):
    return save_message(conversation_id, user_id, message)


@router.get("/{conversation_id}/messages")
def get_messages_route(
    conversation_id: str,
    user_id: str = Header(..., alias="x-user-id"),
):
    return get_messages(conversation_id, user_id)

@router.patch("/{conversation_id}")
def update_conversation_title_route(
    conversation_id: str,
    update: ConversationTitleUpdate,
    user_id: str = Header(..., alias="x-user-id"),
):
    return update_conversation_title(conversation_id, user_id, update)