from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_db
from app.dependencies.auth import get_current_user
from app.services.onboarding_service import OnboardingService

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])


@router.post("/complete")
async def complete_onboarding(
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    service = OnboardingService(session)
    updated = await service.complete(str(user.user_id))
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"success": True, "has_onboarded": True}
