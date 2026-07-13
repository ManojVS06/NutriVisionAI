"""
NutriVision AI — API Routes

All endpoints for the NutriVision AI backend.
"""

import time
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from loguru import logger
import json

from services.pipeline import run_analysis_pipeline
from recommendation_engine.ai_coach import AICoach
from nutrition_engine.calculator import calculate_meal_nutrition
from recommendation_engine.health_scorer import calculate_health_score

router = APIRouter()
ai_coach = AICoach()

# ─────────────────────────────────────────────────────────────────────────────
# Mock history data for demo
# ─────────────────────────────────────────────────────────────────────────────

MOCK_HISTORY = [
    {
        "id": 1, "meal_type": "breakfast", "logged_at": "2026-06-25T08:30:00",
        "detected_foods": ["idli", "sambar", "chutney"],
        "total_nutrition": {"calories": 285, "protein": 10.2, "carbs": 52.0, "fat": 4.8, "fiber": 8.5},
        "health_score": 82, "health_grade": "Good",
    },
    {
        "id": 2, "meal_type": "lunch", "logged_at": "2026-06-25T13:15:00",
        "detected_foods": ["basmati rice", "dal tadka", "mixed vegetable", "curd", "papad"],
        "total_nutrition": {"calories": 620, "protein": 22.5, "carbs": 108.0, "fat": 8.5, "fiber": 12.0},
        "health_score": 78, "health_grade": "Good",
    },
    {
        "id": 3, "meal_type": "dinner", "logged_at": "2026-06-24T19:45:00",
        "detected_foods": ["roti", "chicken curry", "raita", "green salad"],
        "total_nutrition": {"calories": 540, "protein": 38.0, "carbs": 55.0, "fat": 16.0, "fiber": 7.5},
        "health_score": 85, "health_grade": "Excellent",
    },
    {
        "id": 4, "meal_type": "snack", "logged_at": "2026-06-24T16:00:00",
        "detected_foods": ["samosa", "chai"],
        "total_nutrition": {"calories": 382, "protein": 6.0, "carbs": 50.5, "fat": 16.5, "fiber": 3.5},
        "health_score": 42, "health_grade": "Poor",
    },
    {
        "id": 5, "meal_type": "breakfast", "logged_at": "2026-06-24T08:00:00",
        "detected_foods": ["poha", "chai"],
        "total_nutrition": {"calories": 250, "protein": 5.5, "carbs": 46.5, "fat": 4.5, "fiber": 2.5},
        "health_score": 65, "health_grade": "Fair",
    },
    {
        "id": 6, "meal_type": "lunch", "logged_at": "2026-06-23T13:00:00",
        "detected_foods": ["chicken biryani", "raita", "green salad"],
        "total_nutrition": {"calories": 580, "protein": 32.5, "carbs": 75.0, "fat": 14.0, "fiber": 5.5},
        "health_score": 79, "health_grade": "Good",
    },
    {
        "id": 7, "meal_type": "dinner", "logged_at": "2026-06-23T20:00:00",
        "detected_foods": ["roti", "dal makhani", "paneer butter masala"],
        "total_nutrition": {"calories": 720, "protein": 28.5, "carbs": 82.0, "fat": 28.5, "fiber": 9.0},
        "health_score": 68, "health_grade": "Fair",
    },
]

MOCK_USER_PROFILE = {
    "id": 1,
    "name": "Arjun Singh",
    "email": "arjun@example.com",
    "weight_kg": 72,
    "height_cm": 178,
    "age": 24,
    "sport": "sprinting",
    "training_phase": "competition",
    "goal": "performance",
    "is_vegetarian": False,
}


# ─────────────────────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/analyze", tags=["Analysis"])
async def analyze_meal(
    image: UploadFile = File(..., description="Meal photo (JPEG/PNG)"),
    user_id: Optional[str] = Form(None),
    user_profile: Optional[str] = Form(None),
):
    """
    **Full meal analysis pipeline.**

    Runs: Image Preprocessing → YOLOv11 Detection → ConvNeXt Classification →
          SAM2 Segmentation → Depth Estimation → IFCT Nutrition Lookup →
          Health Scoring

    Returns complete nutrition breakdown and health score.
    """
    # Validate file type
    allowed_types = {"image/jpeg", "image/png", "image/webp", "image/jpg"}
    if image.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {image.content_type}. Use JPEG, PNG, or WebP."
        )

    # Read image bytes
    image_bytes = await image.read()
    if len(image_bytes) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=413, detail="Image too large. Max 10MB.")

    # Parse user profile
    profile = None
    if user_profile:
        try:
            profile = json.loads(user_profile)
        except Exception:
            profile = MOCK_USER_PROFILE

    try:
        result = await run_analysis_pipeline(image_bytes, user_profile=profile)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/recommend", tags=["AI Coach"])
async def get_recommendation(
    detected_foods: str = Form(...),
    total_nutrition: str = Form(...),
    user_profile: Optional[str] = Form(None),
    health_score_data: Optional[str] = Form(None),
):
    """
    **AI Coach recommendation.**

    Takes meal analysis results and returns personalized advice using
    Gemma/Llama LLM (or rule-based fallback).
    """
    try:
        foods = json.loads(detected_foods)
        nutrition = json.loads(total_nutrition)
        profile = json.loads(user_profile) if user_profile else MOCK_USER_PROFILE
        hs_data = json.loads(health_score_data) if health_score_data else None

        # Build meal nutrition structure for coach
        meal_nutrition = {"totals": nutrition, "items": []}

        recommendation = await ai_coach.get_recommendation(
            meal_nutrition=meal_nutrition,
            food_items=foods,
            user_profile=profile,
            health_score=hs_data,
        )
        return JSONResponse(content=recommendation)
    except Exception as e:
        logger.error(f"Recommendation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{user_id}", tags=["History"])
async def get_meal_history(user_id: int, limit: int = 10, offset: int = 0):
    """
    **Get meal history for a user.**

    Returns paginated list of past meal analyses with nutrition summaries.
    """
    # In production: query PostgreSQL
    # For demo: return mock data
    paginated = MOCK_HISTORY[offset:offset + limit]
    return JSONResponse(content={
        "user_id": user_id,
        "total": len(MOCK_HISTORY),
        "limit": limit,
        "offset": offset,
        "meals": paginated,
    })


@router.get("/dashboard/{user_id}", tags=["Dashboard"])
async def get_dashboard(user_id: int):
    """
    **Get dashboard analytics for a user.**

    Returns aggregated daily/weekly/monthly nutrition trends.
    """
    # Compute aggregates from mock history
    today_meals = [m for m in MOCK_HISTORY if "2026-06-25" in m["logged_at"]]
    week_meals = MOCK_HISTORY

    today_totals = {
        "calories": sum(m["total_nutrition"]["calories"] for m in today_meals),
        "protein": sum(m["total_nutrition"]["protein"] for m in today_meals),
        "carbs": sum(m["total_nutrition"]["carbs"] for m in today_meals),
        "fat": sum(m["total_nutrition"]["fat"] for m in today_meals),
        "fiber": sum(m["total_nutrition"]["fiber"] for m in today_meals),
    }

    avg_score = sum(m["health_score"] for m in week_meals) / max(len(week_meals), 1)

    weekly_trends = {
        "calories": [620, 850, 740, 680, 910, 755, today_totals["calories"]],
        "protein": [45, 68, 52, 60, 72, 55, today_totals["protein"]],
        "health_score": [75, 62, 80, 78, 71, 82, round(avg_score)],
        "labels": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Today"],
    }

    return JSONResponse(content={
        "user_id": user_id,
        "user_profile": MOCK_USER_PROFILE,
        "today": {
            "totals": today_totals,
            "meals_logged": len(today_meals),
            "avg_health_score": round(avg_score),
        },
        "weekly_trends": weekly_trends,
        "recent_meals": MOCK_HISTORY[:5],
        "top_foods": [
            {"name": "Basmati Rice", "frequency": 5, "avg_portion_g": 210},
            {"name": "Dal Tadka", "frequency": 4, "avg_portion_g": 165},
            {"name": "Roti", "frequency": 4, "avg_portion_g": 42},
            {"name": "Curd", "frequency": 3, "avg_portion_g": 110},
            {"name": "Green Salad", "frequency": 3, "avg_portion_g": 85},
        ],
        "nutrient_gaps": [
            {"nutrient": "Vitamin C", "current_avg": 28, "target": 40, "unit": "mg"},
            {"nutrient": "Calcium", "current_avg": 620, "target": 800, "unit": "mg"},
            {"nutrient": "Iron", "current_avg": 12, "target": 17, "unit": "mg"},
        ],
    })


@router.post("/profile", tags=["User"])
async def update_profile(
    user_id: int = Form(...),
    name: Optional[str] = Form(None),
    weight_kg: Optional[float] = Form(None),
    height_cm: Optional[float] = Form(None),
    age: Optional[int] = Form(None),
    sport: Optional[str] = Form(None),
    training_phase: Optional[str] = Form(None),
    goal: Optional[str] = Form(None),
):
    """
    **Update user profile and athlete settings.**
    """
    # In production: update PostgreSQL
    updated = {k: v for k, v in {
        "user_id": user_id, "name": name, "weight_kg": weight_kg,
        "height_cm": height_cm, "age": age, "sport": sport,
        "training_phase": training_phase, "goal": goal
    }.items() if v is not None}

    return JSONResponse(content={
        "success": True,
        "message": "Profile updated successfully",
        "updated_fields": updated,
    })


@router.get("/athlete-plan/{user_id}", tags=["Athlete Mode"])
async def get_athlete_plan(user_id: int):
    """
    **Get sport-specific nutrition plan for the user.**

    Returns daily macro targets based on sport + training phase.
    """
    plan = ai_coach.get_athlete_plan(MOCK_USER_PROFILE)
    return JSONResponse(content={"user_id": user_id, "plan": plan})


@router.get("/foods/search", tags=["Database"])
async def search_foods(q: str):
    """
    **Search IFCT food database.**

    Fuzzy search for Indian foods and their nutritional info.
    """
    from nutrition_engine.ifct_database import search_food, IFCT_DATABASE
    results = []
    q_lower = q.lower()
    for food_name, data in IFCT_DATABASE.items():
        if q_lower in food_name or any(q_lower in alias.lower() for alias in data.get("aliases", [])):
            results.append({
                "name": food_name,
                "category": data.get("category"),
                "region": data.get("region"),
                "per_100g": {
                    "calories": data.get("calories"),
                    "protein": data.get("protein"),
                    "carbs": data.get("carbs"),
                    "fat": data.get("fat"),
                    "fiber": data.get("fiber"),
                }
            })
    return JSONResponse(content={"query": q, "results": results, "count": len(results)})


@router.get("/foods/all", tags=["Database"])
async def get_all_foods():
    """List all foods available in the IFCT database."""
    from nutrition_engine.ifct_database import IFCT_DATABASE
    foods = [
        {"name": name, "category": data.get("category"), "region": data.get("region")}
        for name, data in IFCT_DATABASE.items()
    ]
    return JSONResponse(content={"foods": foods, "total": len(foods)})


@router.get("/models/status", tags=["System"])
async def model_status():
    """Check the status of all loaded ML models."""
    from services.pipeline import get_models
    detector, classifier, segmentor, estimator = get_models()
    return JSONResponse(content={
        "yolov11": {"status": "real" if not detector.demo_mode else "demo", "demo": detector.demo_mode},
        "convnext": {"status": "real" if not classifier.demo_mode else "demo", "demo": classifier.demo_mode},
        "sam2": {"status": "real" if not segmentor.demo_mode else "demo", "demo": segmentor.demo_mode},
        "depth_anything_v2": {"status": "real" if not estimator.demo_mode else "demo", "demo": estimator.demo_mode},
        "llm_provider": ai_coach.provider,
        "llm_model": ai_coach.model,
    })
