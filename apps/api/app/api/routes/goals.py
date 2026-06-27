from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...db import get_db
from ...dependencies import get_current_user
from ...models import User
from ...schemas import (
    GoalCreateRequest,
    GoalResponse,
    GoalUpdateRequest,
    HabitCreateRequest,
    HabitLogCreateRequest,
    HabitResponse,
)
from ...services.goals import create_goal, create_habit, list_goals, list_habits, log_habit, update_goal


router = APIRouter()


@router.get("/goals", response_model=list[GoalResponse])
def get_goals(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[GoalResponse]:
    return list_goals(db, current_user)


@router.post("/goals", response_model=GoalResponse)
def post_goal(
    payload: GoalCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GoalResponse:
    return create_goal(db, current_user, payload)


@router.patch("/goals/{goal_id}", response_model=GoalResponse)
def patch_goal(
    goal_id: str,
    payload: GoalUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GoalResponse:
    try:
        return update_goal(db, current_user, goal_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/habits", response_model=list[HabitResponse])
def get_habits(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[HabitResponse]:
    return list_habits(db, current_user)


@router.post("/habits", response_model=HabitResponse)
def post_habit(
    payload: HabitCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> HabitResponse:
    return create_habit(db, current_user, payload)


@router.post("/habits/{habit_id}/logs", response_model=HabitResponse)
def post_habit_log(
    habit_id: str,
    payload: HabitLogCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> HabitResponse:
    try:
        return log_habit(db, current_user, habit_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
