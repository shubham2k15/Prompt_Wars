from __future__ import annotations

from datetime import datetime, timedelta
import secrets

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from ..config import get_settings
from ..models import EmailVerificationToken, PasswordResetToken, RefreshToken, User, UserProfile
from ..schemas import ActionResponse, LoginRequest, RegisterRequest, TokenPair
from ..security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    hash_token,
    verify_password,
)


settings = get_settings()


def validate_password_strength(password: str) -> None:
    if not any(char.isupper() for char in password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password needs an uppercase letter")
    if not any(char.islower() for char in password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password needs a lowercase letter")
    if not any(char.isdigit() for char in password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password needs a number")


def register_user(db: Session, payload: RegisterRequest) -> TokenPair:
    validate_password_strength(payload.password)
    existing = db.execute(
        select(User).where(or_(User.user_id == payload.user_id, User.email == payload.email.lower()))
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User ID or email already exists")

    user = User(
        user_id=payload.user_id,
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.flush()

    db.add(UserProfile(user_id=user.id))
    db.commit()
    db.refresh(user)
    return issue_tokens(db, user, device_label="web")


def authenticate_user(db: Session, payload: LoginRequest) -> TokenPair:
    stmt = select(User).where(or_(User.user_id == payload.identifier, User.email == payload.identifier.lower()))
    user = db.execute(stmt).scalar_one_or_none()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return issue_tokens(db, user, device_label=payload.device_label)


def issue_tokens(db: Session, user: User, device_label: str) -> TokenPair:
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=hash_token(refresh_token),
            expires_at=datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days),
            device_label=device_label,
        )
    )
    db.commit()
    return TokenPair(access_token=access_token, refresh_token=refresh_token)


def rotate_refresh_token(db: Session, refresh_token: str) -> TokenPair:
    try:
        payload = decode_refresh_token(refresh_token)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token") from exc

    token_hash = hash_token(refresh_token)
    token_record = db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash, RefreshToken.revoked_at.is_(None))
    ).scalar_one_or_none()
    if not token_record or token_record.expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired or revoked")

    user = db.get(User, payload["sub"])
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    token_record.revoked_at = datetime.utcnow()
    db.flush()
    return issue_tokens(db, user, device_label=token_record.device_label)


def revoke_refresh_token(db: Session, refresh_token: str) -> None:
    token_hash = hash_token(refresh_token)
    token_record = db.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash)).scalar_one_or_none()
    if token_record and not token_record.revoked_at:
        token_record.revoked_at = datetime.utcnow()
        db.commit()


def create_password_reset(db: Session, email: str) -> ActionResponse:
    user = db.execute(select(User).where(User.email == email.lower())).scalar_one_or_none()
    if not user:
        return ActionResponse(message="If that email exists, a reset flow has been prepared.")

    raw_token = secrets.token_urlsafe(24)
    db.add(
        PasswordResetToken(
            user_id=user.id,
            token_hash=hash_token(raw_token),
            expires_at=datetime.utcnow() + timedelta(minutes=30),
        )
    )
    db.commit()
    return ActionResponse(
        message="Password reset token generated for demo use.",
        token=raw_token if settings.app_env != "production" else None,
    )


def reset_password(db: Session, raw_token: str, new_password: str) -> ActionResponse:
    validate_password_strength(new_password)
    token_record = db.execute(
        select(PasswordResetToken).where(
            PasswordResetToken.token_hash == hash_token(raw_token),
            PasswordResetToken.used_at.is_(None),
        )
    ).scalar_one_or_none()
    if not token_record or token_record.expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reset token is invalid or expired")

    user = db.get(User, token_record.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.password_hash = hash_password(new_password)
    token_record.used_at = datetime.utcnow()
    db.commit()
    return ActionResponse(message="Password reset complete.")


def create_email_verification(db: Session, email: str) -> ActionResponse:
    user = db.execute(select(User).where(User.email == email.lower())).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    raw_token = secrets.token_urlsafe(24)
    db.add(
        EmailVerificationToken(
            user_id=user.id,
            token_hash=hash_token(raw_token),
            expires_at=datetime.utcnow() + timedelta(hours=24),
        )
    )
    db.commit()
    return ActionResponse(
        message="Email verification token generated for demo use.",
        token=raw_token if settings.app_env != "production" else None,
    )


def verify_email(db: Session, raw_token: str) -> ActionResponse:
    token_record = db.execute(
        select(EmailVerificationToken).where(
            EmailVerificationToken.token_hash == hash_token(raw_token),
            EmailVerificationToken.used_at.is_(None),
        )
    ).scalar_one_or_none()
    if not token_record or token_record.expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification token is invalid or expired")

    user = db.get(User, token_record.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.is_verified = True
    token_record.used_at = datetime.utcnow()
    db.commit()
    return ActionResponse(message="Email verified.")
