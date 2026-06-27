from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.router import api_router
from .config import get_settings
from .db import Base, engine
from . import models  # noqa: F401


settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict:
    import os
    return {
        "status": "ok",
        "app": settings.app_name,
        "env": settings.app_env,
        "cors": settings.cors_origins,
        "cors_list": settings.cors_origin_list,
        "os_env_app_env": os.environ.get("APP_ENV"),
        "os_env_cors_origins": os.environ.get("CORS_ORIGINS")
    }


app.include_router(api_router)
