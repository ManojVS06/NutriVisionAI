"""
NutriVision AI — FastAPI Backend Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
from loguru import logger

from api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    logger.info("🚀 NutriVision AI Backend starting...")

    # Create upload directory
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("weights", exist_ok=True)

    logger.success("✅ NutriVision AI Backend ready!")
    yield

    logger.info("🛑 NutriVision AI Backend shutting down...")


app = FastAPI(
    title="NutriVision AI",
    description="""
    🍛 **NutriVision AI** — End-to-end AI nutrition scanner for Indian meals.

    ## Features
    * 🔍 **Food Detection** — YOLOv11 detects every food item in your meal photo
    * 🏷️ **Classification** — ConvNeXt distinguishes similar-looking foods (e.g., Veg vs Chicken Biryani)
    * ✂️ **Segmentation** — SAM2 provides exact food shape for accurate portion estimation
    * 📐 **Portion Estimation** — Depth Anything V2 + reference object calibration
    * 🥗 **Nutrition** — IFCT database lookup for 500+ Indian foods
    * 💯 **Health Score** — 10-factor wellness algorithm (0-100)
    * 🤖 **AI Coach** — LLM-powered personalized recommendations
    * 🏃 **Athlete Mode** — Sport-specific periodized nutrition planning
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploads
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Register API routes
app.include_router(router, prefix="/api")


@app.get("/", tags=["Health"])
async def root():
    return {
        "name": "NutriVision AI",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "message": "🍛 Indian AI Nutrition Scanner — Ready for analysis!",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": "NutriVision AI Backend"}
