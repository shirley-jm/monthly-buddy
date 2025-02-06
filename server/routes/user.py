from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta, timezone
from typing import Optional, List
from models.user import PeriodTracking

# User Router
router = APIRouter()

# Period Tracking Routes
@router.post("/track-period")
async def track_period(username: str, last_period_date: datetime, cycle_length: int, symptoms: Optional[List[str]] = None, notes: Optional[str] = None):
    period_data = await PeriodTracking.find_one({"username": username})
    if not period_data:
        period_data = PeriodTracking(
            username=username, 
            period_history=[last_period_date], 
            cycle_length=cycle_length, 
            symptoms=symptoms or [], 
            notes=notes or ""
            )
    else:
        if not period_data.period_history:
            period_data.period_history = []
        period_data.period_history.append(last_period_date)
        period_data.cycle_length = cycle_length
        if symptoms is not None: 
            period_data.symptoms = symptoms
        if notes is not None:
            period_data.notes = notes
    await period_data.save()
    return {"message": "Period data recorded successfully"}

@router.get("/get-period/{username}")
async def get_period_data(username: str):
    period_data = await PeriodTracking.find_one({"username": username})
    if not period_data:
        raise HTTPException(status_code=404, detail="No period data found")
    return period_data

@router.get("/predict-period/{username}")
async def predict_next_period(username: str):
    period_data = await PeriodTracking.find_one({"username": username})
    if not period_data or not period_data.period_history:
        raise HTTPException(status_code=404, detail="No period data found")
    last_period_date = period_data.period_history[-1]
    next_period_date = last_period_date + timedelta(days=period_data.cycle_length)
    ovulation_date = last_period_date + timedelta(days=period_data.cycle_length // 2)
    return {
        "next_period_date": next_period_date.strftime("%Y-%m-%d"),
        "ovulation_date": ovulation_date.strftime("%Y-%m-%d")
    }

@router.get("/send-reminder/{username}")
async def send_reminder(username: str):
    period_data = await PeriodTracking.find_one({"username": username})
    if not period_data or not period_data.period_history:
        raise HTTPException(status_code=404, detail="No period data found")
    last_period_date = period_data.period_history[-1]
    if last_period_date.tzinfo is None:
        last_period_date = last_period_date.replace(tzinfo=timezone.utc)
    next_period_date = last_period_date + timedelta(days=period_data.cycle_length)
    if next_period_date.tzinfo is None:
        next_period_date = next_period_date.replace(tzinfo=timezone.utc)
    days_until_next_period = (next_period_date - datetime.now(timezone.utc)).days
    if days_until_next_period <= 3 and days_until_next_period >= 0:
        return {"message": f"Reminder: Your next period is expected in {days_until_next_period} days!"}
    return {"message": "No reminder needed at this time."}

