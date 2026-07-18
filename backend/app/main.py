import os
import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import engine, Base
from app.config import settings
from app.api import auth, athlete, meals, analytics


# Create database tables automatically
Base.metadata.create_all(bind=engine)


def _background_model_warmup():
    """
    Runs in a daemon thread at startup.
    Loads all deep-learning models into GPU memory so the first real
    request doesn't block waiting for a 700MB download.
    Models that aren't cached yet will be downloaded now silently.
    """
    try:
        from app.services.model_registry import preload_all
        preload_all()
    except Exception as e:
        print(f"[Startup] Model warmup error (non-fatal): {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Kick off model loading in background — doesn't block server startup
    t = threading.Thread(target=_background_model_warmup, daemon=True, name="model-warmup")
    t.start()
    print("[Startup] Background model warmup thread started")
    yield
    # Shutdown — nothing to clean up (models auto-release with process)


app = FastAPI(
    title="NutriVision AI — Indian Food Nutrition Scanner API",
    description="Backend API powering the computer vision food scanning, segmenting, portion sizing, and athlete coaching engine.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware to allow React frontend (typically on localhost:5173 or localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In development, allow all.
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


@app.get("/health")
def health_check():
    """Health check endpoint for monitoring and smoke tests."""
    from app.services.model_registry import get_registry, get_model_status
    registry = get_registry()
    return {
        "status": "healthy",
        "version": "1.0.0",
        "pipeline": "4-tier (DINO+CLIP+SAM2+DepthV2 -> Gemini -> OpenCV)",
        "models_loaded": list(registry.loaded_models.keys()),
        "model_status": get_model_status(),
        "ifct_foods": 155
    }

