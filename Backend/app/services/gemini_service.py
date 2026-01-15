from __future__ import annotations

import os
from typing import Any

import httpx

from app.services.gemini_prompts import WEEKLY_SUMMARY_SYSTEM, WEEKLY_SUMMARY_USER

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


class GeminiService:
    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or GEMINI_API_KEY
        self.model = model or GEMINI_MODEL

    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def generate_weekly_summary(self, data: dict[str, Any]) -> str:
        if not self.api_key:
            raise RuntimeError("Gemini API key not configured")

        user_prompt = WEEKLY_SUMMARY_USER.format(
            total_sessions=data.get("total_sessions", 0),
            total_focus_minutes=data.get("total_focus_minutes", 0),
            average_mood=data.get("average_mood", "n/a"),
            average_energy=data.get("average_energy", "n/a"),
            top_task_type=data.get("top_task_type", "n/a"),
            best_windows=data.get("best_windows", "n/a"),
            mood_energy_insight=data.get("mood_energy_insight", "n/a"),
        )

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": WEEKLY_SUMMARY_SYSTEM},
                        {"text": user_prompt},
                    ],
                }
            ]
        }

        url = GEMINI_URL.format(model=self.model)
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(url, params={"key": self.api_key}, json=payload)
            response.raise_for_status()
            data = response.json()

        candidates = data.get("candidates", [])
        if not candidates:
            raise RuntimeError("Gemini returned no candidates")

        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts:
            raise RuntimeError("Gemini returned empty content")

        return parts[0].get("text", "").strip()
