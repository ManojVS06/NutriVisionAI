import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import engine, Base
from app.config import settings
from app.api import auth, athlete, meals, analytics

# Create database tables automatically
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="NutriVision AI — Indian Food Nutrition Scanner API",
    description="Backend API powering the computer vision food scanning, segmenting, portion sizing, and athlete coaching engine.",
    version="1.0.0"
)

# CORS middleware to allow React frontend (typically on localhost:5173 or localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In development, allow all.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure the static files directory exists and mount it
os.makedirs(settings.STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")

# Include Routers
app.include_router(auth.router, prefix="/api")
app.include_router(athlete.router, prefix="/api")
app.include_router(meals.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")

@app.get("/")
def read_root():
    return {
        "message": "Welcome to NutriVision AI API.",
        "docs_url": "/docs",
        "status": "online"
    }
