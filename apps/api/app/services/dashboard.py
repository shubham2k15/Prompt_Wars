from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from ..models import Goal, Habit, HabitLog, Journal, MemoryItem, MoodLog, Report, User
from ..schemas import DashboardResponse, ReportResponse


def get_dashboard_snapshot(db: Session, user: User) -> DashboardResponse:
    mood_logs = (
        db.query(MoodLog).filter(MoodLog.user_id == user.id).order_by(MoodLog.created_at.desc()).limit(14).all()
    )
    journals = db.query(Journal).filter(Journal.user_id == user.id).order_by(Journal.created_at.desc()).limit(10).all()
    memories = (
        db.query(MemoryItem)
        .filter(MemoryItem.user_id == user.id)
        .order_by(MemoryItem.updated_at.desc())
        .limit(5)
        .all()
    )
    goals = (
        db.execute(
            select(Goal).where(Goal.user_id == user.id, Goal.status.in_(["not_started", "in_progress", "paused"]))
        )
        .scalars()
        .all()
    )
    habits = db.execute(select(Habit).where(Habit.user_id == user.id, Habit.active.is_(True))).scalars().all()

    avg_mood = sum(log.mood_score for log in mood_logs) / len(mood_logs) if mood_logs else 3.5
    avg_stress = sum(log.stress_score for log in mood_logs) / len(mood_logs) if mood_logs else 3.0
    avg_confidence = sum(log.confidence_score for log in mood_logs) / len(mood_logs) if mood_logs else 3.3
    avg_sleep = sum(journal.sleep_hours for journal in journals) / len(journals) if journals else 7.0

    wellness_score = max(40, min(96, int((avg_mood * 22) + ((6 - avg_stress) * 11) + (avg_confidence * 6))))
    study_life_balance_score = max(35, min(95, int((avg_sleep * 8) + ((6 - avg_stress) * 9) + (avg_mood * 6))))

    if avg_stress >= 4.2:
        burnout_risk = "high"
    elif avg_stress >= 3.0:
        burnout_risk = "medium"
    else:
        burnout_risk = "low"

    triggers = _dedupe([trigger for journal in journals for trigger in (journal.detected_triggers or [])])[:6]
    top_memories = [memory.content for memory in memories][:5]
    check_in_streak = min(len(mood_logs) + len(journals), 21)
    today_focus = _build_today_focus(burnout_risk)
    emotional_timeline = _build_timeline(mood_logs, journals)
    emotional_heatmap = _build_heatmap(mood_logs, journals)
    mood_forecast = _build_forecast(avg_mood, avg_stress, triggers)
    weekly_reflection = _build_weekly_reflection(avg_stress, triggers, check_in_streak)
    achievements = _build_achievements(check_in_streak, journals, habits)
    habit_signals = _build_habit_signals(habits)

    return DashboardResponse(
        wellness_score=wellness_score,
        burnout_risk=burnout_risk,
        study_life_balance_score=study_life_balance_score,
        mood_forecast=mood_forecast,
        recent_triggers=triggers or ["academic pressure"],
        top_memories=top_memories or ["No saved memory insights yet"],
        check_in_streak=check_in_streak,
        today_focus=today_focus,
        emotional_timeline=emotional_timeline,
        emotional_heatmap=emotional_heatmap,
        weekly_reflection=weekly_reflection,
        achievements=achievements,
        active_goals=[goal.title for goal in goals][:4] or ["Set a short-term study goal to begin tracking momentum."],
        habit_signals=habit_signals,
    )


def generate_weekly_report(db: Session, user: User) -> ReportResponse:
    snapshot = get_dashboard_snapshot(db, user)
    highlights = [
        f"Burnout risk is currently {snapshot.burnout_risk}.",
        f"Top triggers this week: {', '.join(snapshot.recent_triggers[:3])}.",
        f"Most useful focus right now: {snapshot.today_focus}",
    ]
    report = Report(
        user_id=user.id,
        report_type="weekly",
        period_label=f"week-of-{datetime.utcnow().date().isoformat()}",
        content_json={
            "wellness_score": snapshot.wellness_score,
            "study_life_balance_score": snapshot.study_life_balance_score,
            "mood_forecast": snapshot.mood_forecast,
            "highlights": highlights,
            "weekly_reflection": snapshot.weekly_reflection,
            "achievements": snapshot.achievements,
        },
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return ReportResponse(
        id=report.id,
        report_type=report.report_type,
        period_label=report.period_label,
        content_json=report.content_json,
        created_at=report.created_at,
    )


def list_reports(db: Session, user: User) -> list[ReportResponse]:
    reports = db.execute(
        select(Report).where(Report.user_id == user.id).order_by(desc(Report.created_at)).limit(10)
    ).scalars()
    return [
        ReportResponse(
            id=report.id,
            report_type=report.report_type,
            period_label=report.period_label,
            content_json=report.content_json,
            created_at=report.created_at,
        )
        for report in reports
    ]


def _build_today_focus(burnout_risk: str) -> str:
    if burnout_risk == "high":
        return "Shrink the next study block, protect sleep tonight, and avoid stacking guilt on top of fatigue."
    if burnout_risk == "medium":
        return "Choose one measurable study target, then schedule a real break before motivation fades."
    return "Build confidence with an intentional sprint, then lock in the routine that made it possible."


def _build_timeline(mood_logs: list[MoodLog], journals: list[Journal]) -> list[dict]:
    grouped: dict[str, dict[str, float]] = defaultdict(lambda: {"mood": 0.0, "stress": 0.0, "count": 0.0})
    for log in mood_logs:
        key = log.created_at.strftime("%a")
        grouped[key]["mood"] += log.mood_score
        grouped[key]["stress"] += log.stress_score
        grouped[key]["count"] += 1
    for journal in journals:
        key = journal.created_at.strftime("%a")
        grouped[key]["mood"] += journal.mood_self_score
        grouped[key]["stress"] += 6 - journal.energy_score
        grouped[key]["count"] += 1
    result = []
    order = [(datetime.utcnow() - timedelta(days=index)).strftime("%a") for index in range(6, -1, -1)]
    for key in order:
        count = grouped[key]["count"] or 1
        result.append(
            {
                "label": key,
                "mood": round(grouped[key]["mood"] / count, 1),
                "stress": round(grouped[key]["stress"] / count, 1),
            }
        )
    return result


def _build_heatmap(mood_logs: list[MoodLog], journals: list[Journal]) -> list[dict]:
    mood_by_day: dict[str, list[int]] = defaultdict(list)
    for log in mood_logs:
        mood_by_day[log.created_at.strftime("%a")].append(log.mood_score)
    for journal in journals:
        mood_by_day[journal.created_at.strftime("%a")].append(journal.mood_self_score)

    heatmap = []
    for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
        entries = mood_by_day.get(day, [])
        intensity = round((sum(entries) / len(entries)) / 5, 2) if entries else 0.35
        heatmap.append({"day": day, "intensity": intensity})
    return heatmap


def _build_forecast(avg_mood: float, avg_stress: float, triggers: list[str]) -> str:
    if avg_stress >= 4:
        return f"Forecast suggests an emotional dip if {', '.join(triggers[:2]) or 'pressure'} piles up without recovery."
    if avg_mood >= 4:
        return "Forecast looks stable if the current sleep and break rhythm stays intact."
    return "Forecast is mixed. A smaller workload and cleaner breaks should improve the next two days."


def _build_weekly_reflection(avg_stress: float, triggers: list[str], streak: int) -> str:
    base = "This week shows that your emotional state is closely tied to study pressure and recovery quality."
    if avg_stress >= 4:
        base += " Stress has been elevated enough to justify reducing intensity before burnout compounds."
    elif avg_stress >= 3:
        base += " You are holding a moderate amount of strain, so structure matters more than motivation."
    else:
        base += " You are in a steadier zone, which is the right time to reinforce routines that are working."
    if triggers:
        base += f" The clearest triggers were {', '.join(triggers[:3])}."
    base += f" Your current check-in streak is {streak}, which is a meaningful signal of self-awareness."
    return base


def _build_achievements(streak: int, journals: list[Journal], habits: list[Habit]) -> list[str]:
    achievements = []
    if streak >= 3:
        achievements.append("Check-in streak unlocked")
    if len(journals) >= 3:
        achievements.append("Reflection rhythm unlocked")
    if any(len(habit.logs) >= habit.target_count for habit in habits):
        achievements.append("Habit consistency unlocked")
    return achievements or ["First awareness step unlocked"]


def _build_habit_signals(habits: list[Habit]) -> list[str]:
    signals = []
    for habit in habits[:4]:
        completions = len(habit.logs)
        if completions >= habit.target_count:
            signals.append(f"{habit.name}: on track")
        else:
            signals.append(f"{habit.name}: needs one more check-in")
    return signals or ["No active habits yet. Add one calming or study-support habit."]


def _dedupe(items: list[str]) -> list[str]:
    return list(dict.fromkeys(items))
