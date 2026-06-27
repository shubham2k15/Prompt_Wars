from __future__ import annotations

from collections import Counter

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from ..models import MemoryItem, User


def extract_memory_candidates(text: str) -> list[str]:
    tokens = [token.strip(".,!?").lower() for token in text.split() if len(token) > 4]
    blocked = {"about", "their", "there", "could", "would", "should", "because", "after"}
    filtered = [token for token in tokens if token not in blocked]
    return [token for token, _ in Counter(filtered).most_common(3)]


def remember_text(db: Session, user: User, text: str, source_ref: str, memory_type: str = "conversation") -> None:
    for candidate in extract_memory_candidates(text):
        db.add(
            MemoryItem(
                user_id=user.id,
                memory_type=memory_type,
                content=f"User mentioned {candidate}",
                salience=0.55,
                confidence=0.60,
                source_ref=source_ref,
                tags=[candidate],
            )
        )


def retrieve_memories(db: Session, user: User, query: str, limit: int = 5) -> list[str]:
    query_tokens = set(extract_memory_candidates(query))
    items = db.execute(
        select(MemoryItem).where(MemoryItem.user_id == user.id).order_by(desc(MemoryItem.updated_at)).limit(20)
    ).scalars()
    scored: list[tuple[int, str]] = []
    for item in items:
        overlap = len(query_tokens.intersection(set(item.tags or [])))
        score = overlap + int(item.salience * 10)
        scored.append((score, item.content))
    return [content for _, content in sorted(scored, reverse=True)[:limit]]

