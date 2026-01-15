import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sqlalchemy_models import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: str) -> User | None:
        value = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        result = await self.session.execute(select(User).where(User.user_id == value))
        return result.scalar_one_or_none()

    async def create(self, email: str, hashed_password: str, first_name: str | None, last_name: str | None) -> User:
        user = User(email=email, hashed_password=hashed_password, first_name=first_name, last_name=last_name)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def set_onboarded(self, user_id: str) -> User | None:
        user = await self.get_by_id(user_id)
        if not user:
            return None
        user.has_onboarded = True
        await self.session.commit()
        await self.session.refresh(user)
        return user
