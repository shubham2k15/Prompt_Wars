from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...db import get_db
from ...dependencies import get_current_user
from ...models import User
from ...schemas import ChatMessageCreateRequest, ChatSessionCreateRequest, ChatSessionResponse
from ...services.chat import add_message, create_session, get_session, list_sessions


router = APIRouter()


@router.post("/sessions", response_model=ChatSessionResponse)
def post_session(
    payload: ChatSessionCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChatSessionResponse:
    return create_session(db, current_user, payload.title)


@router.get("/sessions", response_model=list[ChatSessionResponse])
def get_sessions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[ChatSessionResponse]:
    return list_sessions(db, current_user)


@router.get("/sessions/{conversation_id}", response_model=ChatSessionResponse)
def get_chat_session(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChatSessionResponse:
    try:
        return get_session(db, current_user, conversation_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/sessions/{conversation_id}/messages", response_model=ChatSessionResponse)
async def post_message(
    conversation_id: str,
    payload: ChatMessageCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChatSessionResponse:
    try:
        return await add_message(db, current_user, conversation_id, payload.content)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

