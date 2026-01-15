from datetime import datetime
from pydantic import BaseModel, Field


class SessionCreate(BaseModel):
    mood: int = Field(ge=1, le=5)
    energy: str
    task_type: str = Field(alias="taskType")
    duration_minutes: int | None = Field(default=None, alias="durationMinutes")
    good_session: bool | None = Field(default=None, alias="goodSession")
    timestamp: datetime | None = None

    class Config:
        populate_by_name = True


class SessionResponse(BaseModel):
    id: str


class TodaySummaryResponse(BaseModel):
    current_mood: int | None
    current_energy: str | None
    sessions_today: int
    total_focus_minutes: int


class SessionHistoryItem(BaseModel):
    id: str
    date: datetime
    taskType: str
    mood: int
    durationMinutes: int


class SessionHistoryResponse(BaseModel):
    items: list[SessionHistoryItem]
    nextCursor: str | None = None


class SessionDetailResponse(BaseModel):
    id: str
    date: datetime
    taskType: str
    mood: int
    durationMinutes: int
    energy: str | None = None
    goodSession: bool | None = None
