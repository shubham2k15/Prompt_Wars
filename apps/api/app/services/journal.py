from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from ..models import Journal, MoodLog, User
from ..schemas import (
    JournalCreateRequest,
    JournalResponse,
    MoodLogCreateRequest,
    MoodLogResponse,
)
from ..security import decrypt_text, encrypt_text
from .memory import remember_text


def summarize_journal(text: str, mood: int, energy: int, sleep_hours: float) -> tuple[str, list[str]]:
    triggers = []
    lowered = text.lower()
    trigger_map = {
        "sleep": "sleep disruption",
        "fear": "fear of falling behind",
        "mock test": "mock test pressure",
        "parents": "family expectations",
        "comparison": "comparison fatigue",
        "procrastination": "procrastination loop",
        "lonely": "isolation",
        "tired": "mental fatigue",
        "burnout": "burnout risk",
        "guilt": "self-criticism",
        "anxious": "anxiety spike",
    }
    for keyword, label in trigger_map.items():
        if keyword in lowered:
            triggers.append(label)
    if not triggers:
        triggers = ["academic pressure"]

    strengths = []
    for keyword, label in {
        "tried": "you still showed up even while stretched",
        "finished": "you followed through on something important",
        "helped": "you noticed what gave some relief",
        "calm": "you still had moments of steadiness",
        "better": "you caught signs that recovery is possible",
    }.items():
        if keyword in lowered:
            strengths.append(label)

    emotional_read = "heavy and overloaded" if mood <= 2 or energy <= 2 else "strained but workable" if mood <= 3 else "more steady than overwhelmed"
    sleep_read = (
        "Sleep looks like a meaningful recovery gap right now."
        if sleep_hours < 6
        else "Sleep is giving you at least some recovery support."
    )
    strengths_line = strengths[0] if strengths else "you took time to name what is happening instead of bottling it up"
    next_step = build_journal_next_step(triggers, mood, energy, sleep_hours)

    summary = "\n".join(
        [
            "Here is a gentle read of today:",
            f"- What I am noticing: the day feels {emotional_read}, with pressure clustering around {', '.join(triggers[:3])}.",
            f"- What may be helping already: {strengths_line}.",
            f"- Body check: mood {mood}/5, energy {energy}/5, sleep {sleep_hours:g} hours. {sleep_read}",
            f"- Next caring step: {next_step}",
            "- Gentle reminder: your worth did not drop because today felt difficult. A smaller, kinder reset still counts as progress.",
        ]
    )
    return summary, triggers[:5]


def build_journal_next_step(triggers: list[str], mood: int, energy: int, sleep_hours: float) -> str:
    if sleep_hours < 6:
        return "Protect tonight's wind-down, shrink the next study block to one clear target, and avoid extending work deep into exhaustion."
    if "comparison fatigue" in triggers:
        return "Step away from rank or peer comparison for one block and return to a private checklist you can actually complete."
    if mood <= 2 or energy <= 2:
        return "Choose one very small task, finish it gently, then take a real recovery break before asking for more from yourself."
    return "Pick one measurable study win for the next hour, then follow it with a short reset so momentum stays sustainable."


def create_journal(db: Session, user: User, payload: JournalCreateRequest) -> JournalResponse:
    summary, triggers = summarize_journal(
        payload.content,
        payload.mood_self_score,
        payload.energy_score,
        payload.sleep_hours,
    )
    journal = Journal(
        user_id=user.id,
        title=payload.title,
        content_encrypted=encrypt_text(payload.content),
        mood_self_score=payload.mood_self_score,
        energy_score=payload.energy_score,
        sleep_hours=payload.sleep_hours,
        ai_summary=summary,
        detected_triggers=triggers,
    )
    db.add(journal)
    db.flush()
    remember_text(db, user, payload.content, source_ref=journal.id, memory_type="journal")
    db.commit()
    db.refresh(journal)
    return JournalResponse(
        id=journal.id,
        title=journal.title,
        content=payload.content,
        mood_self_score=journal.mood_self_score,
        energy_score=journal.energy_score,
        sleep_hours=journal.sleep_hours,
        ai_summary=journal.ai_summary,
        detected_triggers=journal.detected_triggers or [],
        created_at=journal.created_at,
    )


def list_journals(db: Session, user: User) -> list[JournalResponse]:
    journals = db.execute(
        select(Journal).where(Journal.user_id == user.id).order_by(desc(Journal.created_at))
    ).scalars()
    return [
        JournalResponse(
            id=journal.id,
            title=journal.title,
            content=decrypt_text(journal.content_encrypted),
            mood_self_score=journal.mood_self_score,
            energy_score=journal.energy_score,
            sleep_hours=journal.sleep_hours,
            ai_summary=journal.ai_summary,
            detected_triggers=journal.detected_triggers or [],
            created_at=journal.created_at,
        )
        for journal in journals
    ]


def create_mood_log(db: Session, user: User, payload: MoodLogCreateRequest) -> MoodLogResponse:
    mood_log = MoodLog(
        user_id=user.id,
        mood_score=payload.mood_score,
        stress_score=payload.stress_score,
        anxiety_score=payload.anxiety_score,
        confidence_score=payload.confidence_score,
        note_encrypted=encrypt_text(payload.note) if payload.note else "",
    )
    db.add(mood_log)
    db.commit()
    db.refresh(mood_log)
    return MoodLogResponse(
        id=mood_log.id,
        mood_score=mood_log.mood_score,
        stress_score=mood_log.stress_score,
        anxiety_score=mood_log.anxiety_score,
        confidence_score=mood_log.confidence_score,
        note=payload.note,
        created_at=mood_log.created_at,
    )


def list_mood_logs(db: Session, user: User) -> list[MoodLogResponse]:
    logs = db.execute(select(MoodLog).where(MoodLog.user_id == user.id).order_by(desc(MoodLog.created_at))).scalars()
    return [
        MoodLogResponse(
            id=log.id,
            mood_score=log.mood_score,
            stress_score=log.stress_score,
            anxiety_score=log.anxiety_score,
            confidence_score=log.confidence_score,
            note=decrypt_text(log.note_encrypted) if log.note_encrypted else "",
            created_at=log.created_at,
        )
        for log in logs
    ]
