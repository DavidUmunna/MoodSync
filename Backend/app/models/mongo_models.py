from __future__ import annotations

from datetime import datetime, date
from typing import Any
import uuid

from bson import ObjectId
from pydantic import BaseModel, Field


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value: Any):
        if not ObjectId.is_valid(value):
            raise ValueError("Invalid ObjectId")
        return ObjectId(value)


class WorkSession(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: uuid.UUID
    mood: int = Field(ge=1, le=5)
    energy: str
    task_type: str
    duration_minutes: int = Field(ge=1)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, uuid.UUID: str}

    indexes = [
        [("user_id", 1), ("timestamp", -1)],
        [("task_type", 1)],
        [("energy", 1)],
        [("mood", 1)],
    ]


class DailySummary(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: uuid.UUID
    day: date
    total_sessions: int = Field(ge=0)
    total_focus_minutes: int = Field(ge=0)
    average_mood: float | None = None
    average_energy: float | None = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, uuid.UUID: str}

    indexes = [
        [("user_id", 1), ("day", 1)],
        [("day", -1)],
    ]
