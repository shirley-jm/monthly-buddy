import os
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from fastapi import FastAPI
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)
db = client.period_tracker

# Lifespan Event Handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    from models import user  # Import models inside the function to avoid circular imports
    await init_beanie(database=db, document_models=[user.User, user.PeriodTracking])
    yield
    client.close()  # Close MongoDB connection on shutdown
