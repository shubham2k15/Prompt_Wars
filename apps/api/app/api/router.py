from fastapi import APIRouter

from .routes import auth, chat, dashboard, goals, journals, privacy, profile


api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])
api_router.include_router(journals.router, tags=["wellness"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(dashboard.router, prefix="/insights", tags=["insights"])
api_router.include_router(goals.router, tags=["planning"])
api_router.include_router(privacy.router, prefix="/privacy", tags=["privacy"])
