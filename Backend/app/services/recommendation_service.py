from __future__ import annotations

from datetime import datetime, timedelta, timezone

from motor.motor_asyncio import AsyncIOMotorDatabase


class RecommendationService:
    def __init__(self, mongo: AsyncIOMotorDatabase) -> None:
        self.mongo = mongo
        self.collection = mongo.get_collection("work_sessions")

    async def recommend(self, user_id: str) -> dict[str, str] | None:
        now = datetime.now(tz=timezone.utc)
        start = now - timedelta(days=30)
        hour = now.hour

        recent = (
            await self.collection.find({"user_id": user_id})
            .sort("timestamp", -1)
            .limit(1)
            .to_list(length=1)
        )
        if not recent:
            return None

        recent_session = recent[0]
        mood = recent_session.get("mood")
        energy = recent_session.get("energy")

        pipeline = [
            {
                "$match": {
                    "user_id": user_id,
                    "timestamp": {"$gte": start},
                    "mood": mood,
                    "energy": energy,
                }
            },
            {
                "$addFields": {
                    "hour": {"$hour": "$timestamp"},
                }
            },
            {"$match": {"hour": {"$gte": hour - 2, "$lte": hour + 2}}},
            {
                "$group": {
                    "_id": "$task_type",
                    "avg_duration": {"$avg": "$duration_minutes"},
                    "count": {"$sum": 1},
                }
            },
            {
                "$project": {
                    "task_type": "$_id",
                    "score": {"$add": ["$avg_duration", "$count"]},
                }
            },
            {"$sort": {"score": -1}},
            {"$limit": 1},
        ]

        results = await self.collection.aggregate(pipeline).to_list(length=1)
        if not results:
            return None

        best = results[0]["task_type"]
        explanation = (
            f"Based on your recent sessions with mood {mood} and energy {energy}, "
            f"{best} tends to last longer around this time of day."
        )

        return {"taskType": best, "reason": explanation}
