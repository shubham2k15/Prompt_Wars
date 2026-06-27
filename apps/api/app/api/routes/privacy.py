from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete
from sqlalchemy.orm import Session

from ...db import get_db
from ...dependencies import get_current_user
from ...models import (
    Conversation,
    EmailVerificationToken,
    Goal,
    Habit,
    HabitLog,
    Journal,
    MemoryItem,
    Message,
    MoodLog,
    PasswordResetToken,
    RefreshToken,
    Report,
    User,
)
from ...schemas import ActionResponse, ExportResponse
from ...services.chat import list_sessions
from ...services.dashboard import list_reports
from ...services.goals import list_goals, list_habits
from ...services.journal import list_journals, list_mood_logs
from ...services.profile import build_profile_response, get_or_create_profile


router = APIRouter()


@router.get("/export", response_model=ExportResponse)
def export_data(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> ExportResponse:
    profile = get_or_create_profile(db, current_user)
    memories = db.query(MemoryItem).filter(MemoryItem.user_id == current_user.id).all()
    return ExportResponse(
        profile=build_profile_response(current_user, profile),
        journals=list_journals(db, current_user),
        mood_logs=list_mood_logs(db, current_user),
        memories=[memory.content for memory in memories],
        conversations=list_sessions(db, current_user),
        goals=list_goals(db, current_user),
        habits=list_habits(db, current_user),
        reports=list_reports(db, current_user),
    )


@router.delete("/memory")
def reset_memory(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, str]:
    db.execute(delete(MemoryItem).where(MemoryItem.user_id == current_user.id))
    db.commit()
    return {"message": "Memory reset"}


@router.delete("/memory/{memory_id}", response_model=ActionResponse)
def delete_memory_item(
    memory_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ActionResponse:
    deleted = db.execute(
        delete(MemoryItem).where(MemoryItem.id == memory_id, MemoryItem.user_id == current_user.id)
    )
    db.commit()
    if not deleted.rowcount:
        raise HTTPException(status_code=404, detail="Memory not found")
    return ActionResponse(message="Memory deleted.")


@router.delete("/journals/{journal_id}", response_model=ActionResponse)
def delete_journal(
    journal_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ActionResponse:
    deleted = db.execute(delete(Journal).where(Journal.id == journal_id, Journal.user_id == current_user.id))
    db.commit()
    if not deleted.rowcount:
        raise HTTPException(status_code=404, detail="Journal not found")
    return ActionResponse(message="Journal deleted.")


@router.delete("/conversations/{conversation_id}", response_model=ActionResponse)
def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ActionResponse:
    conversation = db.get(Conversation, conversation_id)
    if not conversation or conversation.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Conversation not found")
    db.execute(delete(Message).where(Message.conversation_id == conversation_id))
    db.execute(delete(Conversation).where(Conversation.id == conversation_id))
    db.commit()
    return ActionResponse(message="Conversation deleted.")


@router.delete("/account", response_model=ActionResponse)
def delete_account(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> ActionResponse:
    conversation_ids = [conversation.id for conversation in current_user.conversations]
    habit_ids = [habit.id for habit in current_user.habits]
    if conversation_ids:
        db.execute(delete(Message).where(Message.conversation_id.in_(conversation_ids)))
    if habit_ids:
        db.execute(delete(HabitLog).where(HabitLog.habit_id.in_(habit_ids)))
    db.execute(delete(Conversation).where(Conversation.user_id == current_user.id))
    db.execute(delete(Journal).where(Journal.user_id == current_user.id))
    db.execute(delete(MoodLog).where(MoodLog.user_id == current_user.id))
    db.execute(delete(MemoryItem).where(MemoryItem.user_id == current_user.id))
    db.execute(delete(Goal).where(Goal.user_id == current_user.id))
    db.execute(delete(Habit).where(Habit.user_id == current_user.id))
    db.execute(delete(Report).where(Report.user_id == current_user.id))
    db.execute(delete(RefreshToken).where(RefreshToken.user_id == current_user.id))
    db.execute(delete(PasswordResetToken).where(PasswordResetToken.user_id == current_user.id))
    db.execute(delete(EmailVerificationToken).where(EmailVerificationToken.user_id == current_user.id))
    profile = get_or_create_profile(db, current_user)
    db.delete(profile)
    db.delete(current_user)
    db.commit()
    return ActionResponse(message="Account deleted.")
