from __future__ import annotations

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from ..ai.providers.gemini import GeminiProvider
from ..ai.providers.mock import MockCompanionProvider
from ..config import get_settings
from ..models import Conversation, Message, User
from ..schemas import ChatMessageResponse, ChatSessionResponse
from ..security import decrypt_text, encrypt_text
from .memory import remember_text, retrieve_memories
from .profile import get_or_create_profile
from .safety import assess_text


settings = get_settings()


def get_provider():
    return GeminiProvider() if settings.gemini_api_key else MockCompanionProvider()


def create_session(db: Session, user: User, title: str) -> ChatSessionResponse:
    conversation = Conversation(user_id=user.id, title=title)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return ChatSessionResponse(
        id=conversation.id,
        title=conversation.title,
        summary=conversation.summary,
        risk_level=conversation.risk_level,
        messages=[],
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
    )


async def add_message(db: Session, user: User, conversation_id: str, content: str) -> ChatSessionResponse:
    conversation = db.get(Conversation, conversation_id)
    if not conversation or conversation.user_id != user.id:
        raise ValueError("Conversation not found")

    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content_encrypted=encrypt_text(content),
        sentiment="reflective",
        emotions=[],
    )
    db.add(user_message)
    db.flush()

    risk = assess_text(content)
    profile = get_or_create_profile(db, user)
    memories = retrieve_memories(db, user, content)

    if risk.escalated and risk.guidance:
        assistant_text = risk.guidance
        emotions = ["concerned"]
        sentiment = "supportive"
    else:
        context = {
            "profile": {
                "exam_type": profile.exam_type,
                "motivation_style": profile.motivation_style,
                "communication_style": profile.communication_style,
            },
            "memories": memories,
            "recent_triggers": [],
        }
        provider = get_provider()
        try:
            result = await provider.respond(prompt=content, context=context)
        except Exception:
            fallback = MockCompanionProvider()
            result = await fallback.respond(prompt=content, context=context)
        assistant_text = result["content"]
        emotions = result.get("emotions", ["reflective"])
        sentiment = result.get("sentiment", "supportive")

    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content_encrypted=encrypt_text(assistant_text),
        sentiment=sentiment,
        emotions=emotions,
    )
    db.add(assistant_message)

    conversation.risk_level = risk.risk_level
    conversation.summary = assistant_text[:220]

    remember_text(db, user, content, source_ref=conversation.id)
    db.commit()
    db.refresh(conversation)
    return get_session(db, user, conversation.id)


def get_session(db: Session, user: User, conversation_id: str) -> ChatSessionResponse:
    conversation = db.get(Conversation, conversation_id)
    if not conversation or conversation.user_id != user.id:
        raise ValueError("Conversation not found")

    messages = db.execute(
        select(Message).where(Message.conversation_id == conversation.id).order_by(Message.created_at)
    ).scalars()
    return ChatSessionResponse(
        id=conversation.id,
        title=conversation.title,
        summary=conversation.summary,
        risk_level=conversation.risk_level,
        messages=[
            ChatMessageResponse(
                id=message.id,
                role=message.role,
                content=decrypt_text(message.content_encrypted),
                sentiment=message.sentiment,
                emotions=message.emotions or [],
                created_at=message.created_at,
            )
            for message in messages
        ],
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
    )


def list_sessions(db: Session, user: User) -> list[ChatSessionResponse]:
    sessions = db.execute(
        select(Conversation).where(Conversation.user_id == user.id).order_by(desc(Conversation.updated_at))
    ).scalars()
    return [get_session(db, user, session.id) for session in sessions]
