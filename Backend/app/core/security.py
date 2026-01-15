import os
import uuid
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any
import jwt
import bcrypt

# Configuration
ACCESS_TOKEN_TTL_MINUTES = int(os.getenv("ACCESS_TOKEN_TTL_MINUTES", "15"))
REFRESH_TOKEN_TTL_DAYS = int(os.getenv("REFRESH_TOKEN_TTL_DAYS", "14"))
JWT_SECRET = os.getenv("JWT_SECRET", "change-me")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt with SHA256 pre-hashing.
    Pre-hashing ensures passwords of any length work with bcrypt's 72-byte limit.
    """
    # Pre-hash with SHA256 to handle any length password
    prehashed = hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    # Generate salt and hash with bcrypt
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(prehashed.encode('utf-8'), salt)
    
    # Return as string for database storage
    return hashed.decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a password against a bcrypt hash.
    """
    # Pre-hash with SHA256 (same as during hashing)
    prehashed = hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    # Verify with bcrypt
    return bcrypt.checkpw(prehashed.encode('utf-8'), hashed_password.encode('utf-8'))


def create_access_token(user_id: uuid.UUID, email: str) -> dict[str, Any]:
    now = datetime.now(tz=timezone.utc)
    expires_at = now + timedelta(minutes=ACCESS_TOKEN_TTL_MINUTES)
    payload = {
        "sub": str(user_id),
        "email": email,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
        "jti": str(uuid.uuid4()),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return {"token": token, "expires_at": expires_at}


def create_refresh_token(user_id: uuid.UUID, session_id: uuid.UUID) -> dict[str, Any]:
    now = datetime.now(tz=timezone.utc)
    expires_at = now + timedelta(days=REFRESH_TOKEN_TTL_DAYS)
    payload = {
        "sub": str(user_id),
        "sid": str(session_id),
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
        "jti": str(uuid.uuid4()),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return {"token": token, "expires_at": expires_at, "jti": payload["jti"]}


def decode_token(token: str, expected_type: str) -> dict[str, Any]:
    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    if payload.get("type") != expected_type:
        raise jwt.InvalidTokenError("Invalid token type")
    return payload


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()