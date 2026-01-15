from fastapi import APIRouter, Depends, Response, status

from app.db.mongo import get_mongo_db
from app.dependencies.auth import get_current_user
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/recommendation", tags=["Recommendation"])


@router.get("")
async def get_recommendation(user=Depends(get_current_user)):
    service = RecommendationService(get_mongo_db())
    recommendation = await service.recommend(str(user.user_id))
    if not recommendation:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    return recommendation
