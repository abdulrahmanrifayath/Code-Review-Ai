import base64
import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import jwt
from cryptography.fernet import Fernet
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_fernet() -> Fernet:
    """
    Derive a valid 32-byte url-safe base64 Fernet key from configured ENCRYPTION_KEY or SECRET_KEY.
    """
    key_bytes = settings.ENCRYPTION_KEY.encode() if settings.ENCRYPTION_KEY else settings.SECRET_KEY.encode()
    derived = hashlib.sha256(key_bytes).digest()
    urlsafe_key = base64.urlsafe_b64encode(derived)
    return Fernet(urlsafe_key)


def encrypt_token(plain_token: str) -> str:
    """Encrypt a sensitive token (e.g. GitHub access token) for storage in DB."""
    if not plain_token:
        return ""
    fernet = get_fernet()
    return fernet.encrypt(plain_token.encode()).decode()


def decrypt_token(encrypted_token: str) -> str:
    """Decrypt an encrypted token from DB back into plaintext."""
    if not encrypted_token:
        return ""
    try:
        fernet = get_fernet()
        return fernet.decrypt(encrypted_token.encode()).decode()
    except Exception:
        return ""


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hashed version."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate bcrypt password hash."""
    return pwd_context.hash(password)


def create_access_token(
    subject: str,
    role: str = "DEVELOPER",
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Generate JWT access token with payload claims, role, and expiration.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {
        "sub": str(subject),
        "role": role,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }

    if extra_claims:
        to_encode.update(extra_claims)

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def create_refresh_token() -> str:
    """Generate a secure, opaque refresh token string."""
    return secrets.token_urlsafe(64)


def hash_refresh_token(token: str) -> str:
    """Generate SHA-256 hash of refresh token for database session comparison."""
    return hashlib.sha256(token.encode()).hexdigest()
