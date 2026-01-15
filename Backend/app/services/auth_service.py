from datetime import datetime, timezone
import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis_Client import redisClient
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.repositories.auth_sessions import AuthSessionRepository
from app.repositories.users import UserRepository


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repo = UserRepository(session)
        self.auth_repo = AuthSessionRepository(session)

    async def register(self, email: str, password: str, first_name: str | None, last_name: str | None):
        existing = await self.user_repo.get_by_email(email)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

        hashed = hash_password(password)
        user = await self.user_repo.create(email=email, hashed_password=hashed, first_name=first_name, last_name=last_name)
        return await self._issue_tokens(
            user.user_id, user.email, user.has_onboarded, None, None, None, None
        )

    async def login(
        self,
        email: str,
        password: str,
        device_name: str | None,
        device_id: str | None,
        ip_address: str | None,
        user_agent: str | None,
    ):
        user = await self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        return await self._issue_tokens(
            user.user_id,
            user.email,
            user.has_onboarded,
            device_name,
            device_id,
            ip_address,
            user_agent,
        )

    async def refresh(self, refresh_token: str):
        payload = decode_token(refresh_token, "refresh")
        jti = payload["jti"]
        session_id = payload["sid"]
        user_id = payload["sub"]

        stored = await redisClient.get(self._refresh_key(jti))
        if not stored or stored != session_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")

        auth_session = await self.auth_repo.get_by_id(session_id)
        if not auth_session or auth_session.is_revoked:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token revoked")

        if auth_session.refresh_token_hash != hash_token(refresh_token):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token mismatch")

        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        await redisClient.delete(self._refresh_key(jti))
        await self.auth_repo.revoke(session_id)

        return await self._issue_tokens(
            user.user_id, user.email, user.has_onboarded, None, None, None, None
        )

    async def logout(self, refresh_token: str):
        payload = decode_token(refresh_token, "refresh")
        jti = payload["jti"]
        session_id = payload["sid"]

        await redisClient.delete(self._refresh_key(jti))
        await self.auth_repo.revoke(session_id)

    async def _issue_tokens(
        self,
        user_id: uuid.UUID,
        email: str,
        has_onboarded: bool,
        device_name: str | None,
        device_id: str | None,
        ip_address: str | None,
        user_agent: str | None,
    ):
        access = create_access_token(user_id, email)
        session_id = uuid.uuid4()
        refresh = create_refresh_token(user_id, session_id)
        refresh_hash = hash_token(refresh["token"])

        auth_session = await self.auth_repo.create(
            session_id=str(session_id),
            user_id=str(user_id),
            refresh_token_hash=refresh_hash,
            expires_at=refresh["expires_at"],
            device_name=device_name,
            device_id=device_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        ttl = int((refresh["expires_at"] - datetime.now(tz=timezone.utc)).total_seconds())
        await redisClient.set(self._refresh_key(refresh["jti"]), str(auth_session.id), ex=ttl)

        return {
            "user_id": str(user_id),
            "access_token": access["token"],
            "refresh_token": refresh["token"],
            "expires_at": access["expires_at"],
            "has_onboarded": has_onboarded,
        }

    def _refresh_key(self, jti: str) -> str:
        return f"refresh:{jti}"
