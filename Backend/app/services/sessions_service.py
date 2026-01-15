from datetime import datetime, timedelta, timezone
from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from redis.asyncio import Redis

from app.schemas.sessions import (
    SessionCreate,
    SessionDetailResponse,
    SessionHistoryItem,
    SessionHistoryResponse,
    TodaySummaryResponse,
)


class SessionsService:
    def __init__(self, mongo: AsyncIOMotorDatabase, redis: Redis) -> None:
        self.mongo = mongo
        self.redis = redis
        self.collection = mongo.get_collection("work_sessions")

    async def log_session(self, user_id: str, payload: SessionCreate) -> str:
        timestamp = payload.timestamp or datetime.now(tz=timezone.utc)
        duration_minutes = payload.duration_minutes or 0
        doc = {
            "user_id": user_id,
            "mood": payload.mood,
            "energy": payload.energy,
            "task_type": payload.task_type,
            "duration_minutes": duration_minutes,
            "good_session": payload.good_session,
            "timestamp": timestamp,
        }
        result = await self.collection.insert_one(doc)
        await self._update_today_cache(user_id, payload, timestamp)
        return str(result.inserted_id)

    async def get_today_summary(self, user_id: str) -> TodaySummaryResponse:
        cache_key = self._today_key(user_id)
        cached = await self.redis.hgetall(cache_key)
        if cached:
            return TodaySummaryResponse(
                current_mood=int(cached.get("current_mood")) if cached.get("current_mood") else None,
                current_energy=cached.get("current_energy"),
                sessions_today=int(cached.get("sessions_today", 0)),
                total_focus_minutes=int(cached.get("total_focus_minutes", 0)),
            )

        start, end = self._today_bounds()
        pipeline = [
            {"$match": {"user_id": user_id, "timestamp": {"$gte": start, "$lt": end}}},
            {
                "$group": {
                    "_id": None,
                    "sessions_today": {"$sum": 1},
                    "total_focus_minutes": {"$sum": "$duration_minutes"},
                    "last_mood": {"$last": "$mood"},
                    "last_energy": {"$last": "$energy"},
                }
            },
        ]
        cursor = self.collection.aggregate(pipeline)
        summary = await cursor.to_list(length=1)
        if not summary:
            return TodaySummaryResponse(
                current_mood=None,
                current_energy=None,
                sessions_today=0,
                total_focus_minutes=0,
            )

        data = summary[0]
        response = TodaySummaryResponse(
            current_mood=data.get("last_mood"),
            current_energy=data.get("last_energy"),
            sessions_today=data.get("sessions_today", 0),
            total_focus_minutes=data.get("total_focus_minutes", 0),
        )
        await self._cache_today_summary(user_id, response)
        return response

    async def get_history(self, user_id: str, limit: int, cursor: str | None) -> SessionHistoryResponse:
        query: dict[str, Any] = {"user_id": user_id}
        if cursor:
            query["_id"] = {"$lt": ObjectId(cursor)}

        docs = (
            await self.collection.find(query)
            .sort("_id", -1)
            .limit(limit + 1)
            .to_list(length=limit + 1)
        )

        next_cursor = None
        if len(docs) > limit:
            next_cursor = str(docs[-1]["_id"])
            docs = docs[:limit]

        items = [
            SessionHistoryItem(
                id=str(doc["_id"]),
                date=doc["timestamp"],
                taskType=doc["task_type"],
                mood=doc["mood"],
                durationMinutes=doc["duration_minutes"],
            )
            for doc in docs
        ]

        return SessionHistoryResponse(items=items, nextCursor=next_cursor)

    async def get_detail(self, user_id: str, session_id: str) -> SessionDetailResponse | None:
        doc = await self.collection.find_one({"_id": ObjectId(session_id), "user_id": user_id})
        if not doc:
            return None

        return SessionDetailResponse(
            id=str(doc["_id"]),
            date=doc["timestamp"],
            taskType=doc.get("task_type", ""),
            mood=doc.get("mood", 0),
            durationMinutes=doc.get("duration_minutes", 0),
            energy=doc.get("energy"),
            goodSession=doc.get("good_session"),
        )

    async def _update_today_cache(self, user_id: str, payload: SessionCreate, timestamp: datetime) -> None:
        cache_key = self._today_key(user_id)
        await self.redis.hincrby(cache_key, "sessions_today", 1)
        await self.redis.hincrby(cache_key, "total_focus_minutes", payload.duration_minutes)
        await self.redis.hset(cache_key, mapping={"current_mood": payload.mood, "current_energy": payload.energy})
        await self.redis.expireat(cache_key, int(self._end_of_day(timestamp).timestamp()))

    async def _cache_today_summary(self, user_id: str, summary: TodaySummaryResponse) -> None:
        cache_key = self._today_key(user_id)
        await self.redis.hset(
            cache_key,
            mapping={
                "current_mood": summary.current_mood or "",
                "current_energy": summary.current_energy or "",
                "sessions_today": summary.sessions_today,
                "total_focus_minutes": summary.total_focus_minutes,
            },
        )
        await self.redis.expireat(cache_key, int(self._end_of_day(datetime.now(tz=timezone.utc)).timestamp()))

    def _today_key(self, user_id: str) -> str:
        date_key = datetime.now(tz=timezone.utc).date().isoformat()
        return f"user:{user_id}:today:{date_key}"

    def _today_bounds(self) -> tuple[datetime, datetime]:
        now = datetime.now(tz=timezone.utc)
        start = datetime(year=now.year, month=now.month, day=now.day, tzinfo=timezone.utc)
        return start, start + timedelta(days=1)

    def _end_of_day(self, timestamp: datetime) -> datetime:
        start = datetime(year=timestamp.year, month=timestamp.month, day=timestamp.day, tzinfo=timezone.utc)
        return start + timedelta(days=1)
