from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.users import UserRepository


class OnboardingService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repo = UserRepository(session)

    async def complete(self, user_id: str):
        user = await self.user_repo.set_onboarded(user_id)
        return user
