from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...db import get_db
from ...dependencies import get_current_user
from ...models import User
from ...schemas import (
    JournalCreateRequest,
    JournalResponse,
    MoodLogCreateRequest,
    MoodLogResponse,
)
from ...services.journal import create_journal, create_mood_log, list_journals, list_mood_logs


router = APIRouter()


@router.post("/journals", response_model=JournalResponse)
def post_journal(
    payload: JournalCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JournalResponse:
    return create_journal(db, current_user, payload)


@router.get("/journals", response_model=list[JournalResponse])
def get_journals(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[JournalResponse]:
    return list_journals(db, current_user)


@router.post("/mood-logs", response_model=MoodLogResponse)
def post_mood_log(
    payload: MoodLogCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MoodLogResponse:
    return create_mood_log(db, current_user, payload)


@router.get("/mood-logs", response_model=list[MoodLogResponse])
def get_mood_logs(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[MoodLogResponse]:
    return list_mood_logs(db, current_user)

