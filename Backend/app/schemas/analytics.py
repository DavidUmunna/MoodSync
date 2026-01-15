from pydantic import BaseModel


class DeepWorkSlot(BaseModel):
    dayOfWeek: int
    hour: int
    score: float


class WarningCard(BaseModel):
    title: str
    message: str
    severity: str


class InsightsResponse(BaseModel):
    bestDeepWorkSlots: list[DeepWorkSlot]
    moodEnergyInsight: str
    warningCard: WarningCard | None = None
