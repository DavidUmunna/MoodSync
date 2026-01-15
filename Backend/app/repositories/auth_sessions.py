from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sqlalchemy_models import AuthSession


class AuthSessionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        session_id: str,
        user_id: str,
        refresh_token_hash: str,
        expires_at: datetime,
        device_name: str | None,
        device_id: str | None,
        ip_address: str | None,
        user_agent: str | None,
    ) -> AuthSession:
        auth_session = AuthSession(
            id=session_id,
            user_id=user_id,
            refresh_token_hash=refresh_token_hash,
            expires_at=expires_at,
            device_name=device_name,
            device_id=device_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.session.add(auth_session)
        await self.session.commit()
        await self.session.refresh(auth_session)
        return auth_session

    async def get_by_id(self, session_id: str) -> AuthSession | None:
        result = await self.session.execute(select(AuthSession).where(AuthSession.id == session_id))
        return result.scalar_one_or_none()

    async def revoke(self, session_id: str) -> None:
        auth_session = await self.get_by_id(session_id)
        if not auth_session:
            return
        auth_session.is_revoked = True
        auth_session.revoked_at = datetime.utcnow()
        await self.session.commit()
