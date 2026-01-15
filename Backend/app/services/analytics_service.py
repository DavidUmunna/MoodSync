from datetime import datetime, timedelta, timezone

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.schemas.analytics import DeepWorkSlot, InsightsResponse, WarningCard


class AnalyticsService:
    def __init__(self, mongo: AsyncIOMotorDatabase) -> None:
        self.mongo = mongo
        self.collection = mongo.get_collection("work_sessions")

    async def weekly_summary_data(self, user_id: str) -> dict:
        start = datetime.now(tz=timezone.utc) - timedelta(days=7)
        pipeline = [
            {"$match": {"user_id": user_id, "timestamp": {"$gte": start}}},
            {
                "$group": {
                    "_id": None,
                    "total_sessions": {"$sum": 1},
                    "total_focus_minutes": {"$sum": "$duration_minutes"},
                    "average_mood": {"$avg": "$mood"},
                    "average_energy": {"$avg": "$energy"},
                }
            },
        ]

        summary = await self.collection.aggregate(pipeline).to_list(length=1)
        top_task = await self.collection.aggregate(
            [
                {"$match": {"user_id": user_id, "timestamp": {"$gte": start}}},
                {"$group": {"_id": "$task_type", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 1},
            ]
        ).to_list(length=1)

        if not summary:
            return {
                "total_sessions": 0,
                "total_focus_minutes": 0,
                "average_mood": "n/a",
                "average_energy": "n/a",
                "top_task_type": "n/a",
            }

        average_mood = summary[0].get("average_mood")
        average_energy = summary[0].get("average_energy")

        return {
            "total_sessions": summary[0].get("total_sessions", 0),
            "total_focus_minutes": summary[0].get("total_focus_minutes", 0),
            "average_mood": round(average_mood, 1) if average_mood is not None else "n/a",
            "average_energy": round(average_energy, 1) if average_energy is not None else "n/a",
            "top_task_type": top_task[0]["_id"] if top_task else "n/a",
        }

    async def build_insights(self, user_id: str) -> InsightsResponse:
        slots = await self._deep_work_slots(user_id)
        mood_insight = await self._mood_energy_insight(user_id)

        warning_card = None
        if not slots:
            warning_card = WarningCard(
                title="Not enough data",
                message="Log a few deep work sessions to reveal your best focus windows.",
                severity="info",
            )

        return InsightsResponse(
            bestDeepWorkSlots=slots,
            moodEnergyInsight=mood_insight,
            warningCard=warning_card,
        )

    async def _deep_work_slots(self, user_id: str) -> list[DeepWorkSlot]:
        start = datetime.now(tz=timezone.utc) - timedelta(days=30)
        pipeline = [
            {
                "$match": {
                    "user_id": user_id,
                    "task_type": "Deep work",
                    "timestamp": {"$gte": start},
                }
            },
            {
                "$group": {
                    "_id": {
                        "dayOfWeek": {"$dayOfWeek": "$timestamp"},
                        "hour": {"$hour": "$timestamp"},
                    },
                    "avg_duration": {"$avg": "$duration_minutes"},
                    "count": {"$sum": 1},
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "dayOfWeek": {"$subtract": ["$_id.dayOfWeek", 1]},
                    "hour": "$_id.hour",
                    "score": {"$add": ["$avg_duration", "$count"]},
                }
            },
            {"$sort": {"score": -1}},
        ]

        results = await self.collection.aggregate(pipeline).to_list(length=84)
        return [DeepWorkSlot(**item) for item in results]

    async def _mood_energy_insight(self, user_id: str) -> str:
        start = datetime.now(tz=timezone.utc) - timedelta(days=30)
        pipeline = [
            {"$match": {"user_id": user_id, "timestamp": {"$gte": start}}},
            {
                "$group": {
                    "_id": {"mood": "$mood", "energy": "$energy"},
                    "avg_duration": {"$avg": "$duration_minutes"},
                    "count": {"$sum": 1},
                }
            },
            {"$sort": {"avg_duration": -1, "count": -1}},
            {"$limit": 1},
        ]
        results = await self.collection.aggregate(pipeline).to_list(length=1)
        if not results:
            return "Log more sessions to reveal how mood and energy affect performance."

        top = results[0]
        mood = top["_id"]["mood"]
        energy = top["_id"]["energy"]
        avg_duration = int(top["avg_duration"])
        return f"Your longest sessions happen when mood is {mood} and energy is {energy} (avg {avg_duration} min)."
