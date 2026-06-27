from datetime import datetime, timedelta, timezone
from hashlib import sha256
from typing import Any

from cryptography.fernet import Fernet
from jose import jwt
from passlib.context import CryptContext

from .config import get_settings


settings = get_settings()
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
fernet = Fernet(settings.encryption_key.encode())


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload: dict[str, Any] = {"sub": subject, "type": "access", "exp": expires}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_refresh_token(subject: str) -> str:
    expires = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    payload: dict[str, Any] = {"sub": subject, "type": "refresh", "exp": expires}
    return jwt.encode(payload, settings.refresh_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])


def decode_refresh_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.refresh_secret, algorithms=[settings.jwt_algorithm])


def hash_token(token: str) -> str:
    return sha256(token.encode()).hexdigest()


def encrypt_text(value: str) -> str:
    return fernet.encrypt(value.encode()).decode()


def decrypt_text(value: str) -> str:
    return fernet.decrypt(value.encode()).decode()
