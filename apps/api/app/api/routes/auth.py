from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from ...db import get_db
from ...rate_limit import enforce_rate_limit
from ...schemas import (
    ActionResponse,
    ForgotPasswordRequest,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenPair,
    VerifyEmailRequest,
)
from ...services.auth import (
    authenticate_user,
    create_email_verification,
    create_password_reset,
    register_user,
    reset_password,
    revoke_refresh_token,
    rotate_refresh_token,
    verify_email,
)


router = APIRouter()


@router.post("/register", response_model=TokenPair)
def register(payload: RegisterRequest, request: Request, db: Session = Depends(get_db)) -> TokenPair:
    enforce_rate_limit(request, "register", limit=10, window_seconds=300)
    return register_user(db, payload)


@router.post("/login", response_model=TokenPair)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)) -> TokenPair:
    enforce_rate_limit(request, "login", limit=20, window_seconds=300)
    return authenticate_user(db, payload)


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> TokenPair:
    return rotate_refresh_token(db, payload.refresh_token)


@router.post("/logout")
def logout(payload: RefreshRequest, db: Session = Depends(get_db)) -> dict[str, str]:
    revoke_refresh_token(db, payload.refresh_token)
    return {"message": "Logged out"}


@router.post("/forgot-password", response_model=ActionResponse)
def forgot_password(
    payload: ForgotPasswordRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> ActionResponse:
    enforce_rate_limit(request, "forgot-password", limit=10, window_seconds=300)
    return create_password_reset(db, payload.email)


@router.post("/reset-password", response_model=ActionResponse)
def post_reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)) -> ActionResponse:
    return reset_password(db, payload.token, payload.new_password)


@router.post("/request-verification", response_model=ActionResponse)
def request_verification(
    payload: ForgotPasswordRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> ActionResponse:
    enforce_rate_limit(request, "request-verification", limit=10, window_seconds=300)
    return create_email_verification(db, payload.email)


@router.post("/verify-email", response_model=ActionResponse)
def post_verify_email(payload: VerifyEmailRequest, db: Session = Depends(get_db)) -> ActionResponse:
    return verify_email(db, payload.token)
