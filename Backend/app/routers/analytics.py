from fastapi import APIRouter, Depends

from app.db.mongo import get_mongo_db
from app.dependencies.auth import get_current_user
from app.schemas.analytics import InsightsResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/insights", response_model=InsightsResponse)
async def insights(user=Depends(get_current_user)):
    service = AnalyticsService(get_mongo_db())
    return await service.build_insights(str(user.user_id))
