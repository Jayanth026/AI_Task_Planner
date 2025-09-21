from typing import List, Dict, Any
from pydantic import BaseModel


class DayPlan(BaseModel):
    day: str
    items: List[str]
    notes: List[str] = []


class GeneratedPlan(BaseModel):
    goal: str
    days: List[DayPlan]
    metadata: Dict[str, Any] = {}   # weather, sources, etc.
