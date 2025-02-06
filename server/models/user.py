from beanie import Document
from datetime import datetime
from typing import Optional, List

class User(Document):
    username: str
    password: str

    class Settings:
        collection = "users"  # Corrected to string

class PeriodTracking(Document):
    username: str
    period_history: List[datetime]
    cycle_length: int  # in days
    symptoms: Optional[List[str]]
    notes: Optional[str]

    class Settings:
        collection = "period_tracking"