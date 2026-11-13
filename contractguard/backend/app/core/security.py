import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Union, Any
from jose import jwt, JWTError
from app.core.config import settings

ALGORITHM = settings.JWT_ALGORITHM


def _hash_pbkdf2(password: str, salt: Optional[str] = None) -> str:
    """Deterministic PBKDF2-HMAC-SHA256 password hashing for cross-platform robustness."""
    if not salt:
        salt = os.urandom(16).hex()
    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100_000,
    )
    return f"pbkdf2:sha256:100000${salt}${key.hex()}"


def _verify_pbkdf2(password: str, hash_val: str) -> bool:
    try:
        parts = hash_val.split("$")
        if len(parts) != 3:
            return False
        salt = parts[1]
        expected_hash = parts[2]
        computed = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            100_000,
        ).hex()
        return hmac.compare_digest(computed, expected_hash)
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    return _hash_pbkdf2(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if hashed_password.startswith("pbkdf2:"):
        return _verify_pbkdf2(plain_password, hashed_password)
    # Direct fallback for plain or legacy
    return hmac.compare_digest(plain_password, hashed_password)


def create_access_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
