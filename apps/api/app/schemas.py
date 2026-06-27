from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    user_id: str = Field(min_length=4, max_length=64)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    identifier: str
    password: str
    device_label: str = "web"


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


class VerifyEmailRequest(BaseModel):
    token: str


class ActionResponse(BaseModel):
    message: str
    token: str | None = None


class ProfileUpdateRequest(BaseModel):
    full_name: str = ""
    exam_type: str = ""
    target_rank: str = ""
    preferred_language: str = "English"
    motivation_style: str = "gentle"
    communication_style: str = "empathetic"
    study_schedule: dict[str, Any] = Field(default_factory=dict)
    wellness_preferences: dict[str, Any] = Field(default_factory=dict)


class ProfileResponse(ProfileUpdateRequest):
    user_id: str
    email: EmailStr


class JournalCreateRequest(BaseModel):
    title: str = Field(min_length=3, max_length=160)
    content: str = Field(min_length=1, max_length=5000)
    mood_self_score: int = Field(ge=1, le=5)
    energy_score: int = Field(ge=1, le=5)
    sleep_hours: float = Field(ge=0, le=24)


class JournalResponse(BaseModel):
    id: str
    title: str
    content: str
    mood_self_score: int
    energy_score: int
    sleep_hours: float
    ai_summary: str
    detected_triggers: list[str]
    created_at: datetime


class MoodLogCreateRequest(BaseModel):
    mood_score: int = Field(ge=1, le=5)
    stress_score: int = Field(ge=1, le=5)
    anxiety_score: int = Field(ge=1, le=5)
    confidence_score: int = Field(ge=1, le=5)
    note: str = Field(default="", max_length=2000)


class MoodLogResponse(BaseModel):
    id: str
    mood_score: int
    stress_score: int
    anxiety_score: int
    confidence_score: int
    note: str
    created_at: datetime


class ChatSessionCreateRequest(BaseModel):
    title: str = "New conversation"


class ChatMessageCreateRequest(BaseModel):
    content: str = Field(min_length=1, max_length=4000)


class ChatMessageResponse(BaseModel):
    id: str
    role: str
    content: str
    sentiment: str
    emotions: list[str]
    created_at: datetime


class ChatSessionResponse(BaseModel):
    id: str
    title: str
    summary: str
    risk_level: str
    messages: list[ChatMessageResponse]
    created_at: datetime
    updated_at: datetime


class DashboardResponse(BaseModel):
    wellness_score: int
    burnout_risk: str
    study_life_balance_score: int
    mood_forecast: str
    recent_triggers: list[str]
    top_memories: list[str]
    check_in_streak: int
    today_focus: str
    emotional_timeline: list[dict[str, Any]]
    emotional_heatmap: list[dict[str, Any]]
    weekly_reflection: str
    achievements: list[str]
    active_goals: list[str]
    habit_signals: list[str]


class ExportResponse(BaseModel):
    profile: ProfileResponse
    journals: list[JournalResponse]
    mood_logs: list[MoodLogResponse]
    memories: list[str]
    conversations: list[ChatSessionResponse]
    goals: list["GoalResponse"]
    habits: list["HabitResponse"]
    reports: list["ReportResponse"]


class GoalCreateRequest(BaseModel):
    title: str = Field(min_length=3, max_length=180)
    category: str = "study"
    target_date: str = ""
    progress: int = Field(default=0, ge=0, le=100)
    status: str = "not_started"


class GoalUpdateRequest(BaseModel):
    progress: int | None = Field(default=None, ge=0, le=100)
    status: str | None = "active"


class GoalResponse(BaseModel):
    id: str
    title: str
    category: str
    target_date: str
    progress: int
    status: str
    created_at: datetime
    updated_at: datetime


class HabitCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    frequency: str = "daily"
    target_count: int = Field(default=1, ge=1, le=10)


class HabitLogCreateRequest(BaseModel):
    status: str = "done"


class HabitResponse(BaseModel):
    id: str
    name: str
    frequency: str
    target_count: int
    active: bool
    completion_count: int
    latest_status: str
    created_at: datetime
    updated_at: datetime


class ReportResponse(BaseModel):
    id: str
    report_type: str
    period_label: str
    content_json: dict[str, Any]
    created_at: datetime


ExportResponse.model_rebuild()
