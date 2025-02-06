from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth, user, chatbot
from database import lifespan
import uvicorn

app = FastAPI(lifespan=lifespan)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routes
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(chatbot.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Period Tracker API!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
