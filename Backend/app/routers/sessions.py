from fastapi import APIRouter, Depends, Query, Response
from redis.asyncio import Redis

from app.core.redis_Client import redisClient
from app.db.mongo import get_mongo_db
from app.dependencies.auth import get_current_user
from app.schemas.sessions import (
    SessionCreate,
    SessionDetailResponse,
    SessionHistoryResponse,
    SessionResponse,
    TodaySummaryResponse,
)
from app.services.sessions_service import SessionsService

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.post("", response_model=SessionResponse)
async def log_session(
    payload: SessionCreate,
    user=Depends(get_current_user),
):
    service = SessionsService(get_mongo_db(), redisClient)
    session_id = await service.log_session(str(user.user_id), payload)
    return SessionResponse(id=session_id)


@router.get("/today", response_model=TodaySummaryResponse)
async def get_today(user=Depends(get_current_user)):
    service = SessionsService(get_mongo_db(), redisClient)
    return await service.get_today_summary(str(user.user_id))


@router.get("/history", response_model=SessionHistoryResponse)
async def get_history(
    user=Depends(get_current_user),
    limit: int = Query(10, ge=1, le=50),
    cursor: str | None = None,
):
    service = SessionsService(get_mongo_db(), redisClient)
    return await service.get_history(str(user.user_id), limit, cursor)


@router.get("/{session_id}", response_model=SessionDetailResponse)
async def get_session_detail(session_id: str, user=Depends(get_current_user)):
    service = SessionsService(get_mongo_db(), redisClient)
    detail = await service.get_detail(str(user.user_id), session_id)
    if not detail:
        return Response(status_code=404)
    return detail
