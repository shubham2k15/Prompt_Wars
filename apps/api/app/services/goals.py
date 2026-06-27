from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from ..models import Goal, Habit, HabitLog, User
from ..schemas import (
    GoalCreateRequest,
    GoalResponse,
    GoalUpdateRequest,
    HabitCreateRequest,
    HabitLogCreateRequest,
    HabitResponse,
)


def create_goal(db: Session, user: User, payload: GoalCreateRequest) -> GoalResponse:
    goal = Goal(
        user_id=user.id,
        title=payload.title,
        category=payload.category,
        target_date=payload.target_date,
        progress=payload.progress,
        status=normalize_goal_status(payload.status, payload.progress),
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return build_goal_response(goal)


def list_goals(db: Session, user: User) -> list[GoalResponse]:
    goals = db.execute(select(Goal).where(Goal.user_id == user.id).order_by(desc(Goal.updated_at))).scalars()
    return [build_goal_response(goal) for goal in goals]


def update_goal(db: Session, user: User, goal_id: str, payload: GoalUpdateRequest) -> GoalResponse:
    goal = db.get(Goal, goal_id)
    if not goal or goal.user_id != user.id:
        raise ValueError("Goal not found")
    next_progress = payload.progress if payload.progress is not None else goal.progress
    goal.progress = next_progress
    goal.status = normalize_goal_status(payload.status, next_progress, current_status=goal.status)
    db.commit()
    db.refresh(goal)
    return build_goal_response(goal)


def normalize_goal_status(status: str | None, progress: int, current_status: str | None = None) -> str:
    if progress >= 100:
        return "completed"
    if status in {"completed", "paused", "not_started", "in_progress"}:
        return status
    if progress > 0:
        return "in_progress"
    if current_status in {"paused", "not_started"}:
        return current_status
    return "not_started"


def create_habit(db: Session, user: User, payload: HabitCreateRequest) -> HabitResponse:
    habit = Habit(
        user_id=user.id,
        name=payload.name,
        frequency=payload.frequency,
        target_count=payload.target_count,
    )
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return build_habit_response(habit)


def list_habits(db: Session, user: User) -> list[HabitResponse]:
    habits = db.execute(select(Habit).where(Habit.user_id == user.id).order_by(desc(Habit.updated_at))).scalars()
    return [build_habit_response(habit) for habit in habits]


def log_habit(db: Session, user: User, habit_id: str, payload: HabitLogCreateRequest) -> HabitResponse:
    habit = db.get(Habit, habit_id)
    if not habit or habit.user_id != user.id:
        raise ValueError("Habit not found")
    db.add(HabitLog(habit_id=habit.id, status=payload.status))
    db.commit()
    db.refresh(habit)
    return build_habit_response(habit)


def build_goal_response(goal: Goal) -> GoalResponse:
    return GoalResponse(
        id=goal.id,
        title=goal.title,
        category=goal.category,
        target_date=goal.target_date,
        progress=goal.progress,
        status=goal.status,
        created_at=goal.created_at,
        updated_at=goal.updated_at,
    )


def build_habit_response(habit: Habit) -> HabitResponse:
    completion_count = len(habit.logs or [])
    latest_status = habit.logs[-1].status if habit.logs else "pending"
    return HabitResponse(
        id=habit.id,
        name=habit.name,
        frequency=habit.frequency,
        target_count=habit.target_count,
        active=habit.active,
        completion_count=completion_count,
        latest_status=latest_status,
        created_at=habit.created_at,
        updated_at=habit.updated_at,
    )
