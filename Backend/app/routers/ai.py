from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends

from app.core.redis_Client import redisClient
from app.db.mongo import get_mongo_db
from app.dependencies.auth import get_current_user
from app.services.analytics_service import AnalyticsService
from app.services.gemini_service import GeminiService

router = APIRouter(prefix="/ai", tags=["AI"])


@router.get("/summary")
async def weekly_summary(user=Depends(get_current_user)):
    user_id = str(user.user_id)
    week_start = _week_start_key()
    cache_key = f"ai:summary:{user_id}:{week_start}"

    cached = await redisClient.get(cache_key)
    if cached:
        return {"summary": cached, "source": "cache"}

    analytics = AnalyticsService(get_mongo_db())
    weekly_data = await analytics.weekly_summary_data(user_id)
    insights = await analytics.build_insights(user_id)
    weekly_data["mood_energy_insight"] = insights.moodEnergyInsight
    weekly_data["best_windows"] = _format_best_windows(insights.bestDeepWorkSlots)

    gemini = GeminiService()
    if gemini.is_configured():
        try:
            summary = await gemini.generate_weekly_summary(weekly_data)
            await redisClient.set(cache_key, summary, ex=_cache_ttl_seconds())
            return {"summary": summary, "source": "gemini"}
        except Exception:
            pass

    fallback = _fallback_summary(weekly_data)
    await redisClient.set(cache_key, fallback, ex=_cache_ttl_seconds())
    return {"summary": fallback, "source": "fallback"}


def _week_start_key() -> str:
    now = datetime.now(tz=timezone.utc)
    start = now - timedelta(days=now.weekday())
    return start.date().isoformat()


def _cache_ttl_seconds() -> int:
    now = datetime.now(tz=timezone.utc)
    end = now + timedelta(days=7 - now.weekday())
    return int((end - now).total_seconds())


def _format_best_windows(slots) -> str:
    top = sorted(slots, key=lambda s: s.score, reverse=True)[:3]
    if not top:
        return "n/a"
    return ", ".join([f"{_day_label(s.dayOfWeek)} {s.hour}:00" for s in top])


def _day_label(day_index: int) -> str:
    labels = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    if 0 <= day_index < len(labels):
        return labels[day_index]
    return "Day"


def _fallback_summary(data: dict) -> str:
    return (
        f"You logged {data.get('total_sessions', 0)} sessions for "
        f"{data.get('total_focus_minutes', 0)} minutes this week. "
        f"Your top task was {data.get('top_task_type', 'n/a')}. "
        f"Average mood was {data.get('average_mood', 'n/a')} and energy {data.get('average_energy', 'n/a')}. "
        f"Best deep work windows: {data.get('best_windows', 'n/a')}. "
        "Pick one window next week and protect it for focused work."
    )
