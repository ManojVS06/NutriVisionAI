from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
from typing import List, Dict, Any
from app.database import get_db
from app.api.auth import get_current_user
from app import models, schemas

router = APIRouter(prefix="/analytics", tags=["Analytics & Historical Trends"])

@router.get("/summary", response_model=schemas.DashboardSummary)
def get_dashboard_summary(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    # 1. Fetch Athlete profile for goals
    profile = db.query(models.AthleteProfile).filter(models.AthleteProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Athlete profile not found")

    # 2. Get today's meals
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_end = datetime.combine(date.today(), datetime.max.time())
    
    meals_today = db.query(models.Meal).filter(
        models.Meal.user_id == current_user.id,
        models.Meal.created_at >= today_start,
        models.Meal.created_at <= today_end
    ).all()

    # 3. Sum up today's macros
    consumed_calories = sum(m.total_calories for m in meals_today)
    consumed_protein = sum(m.total_protein for m in meals_today)
    consumed_carbs = sum(m.total_carbs for m in meals_today)
    consumed_fat = sum(m.total_fat for m in meals_today)
    
    # 4. Average health score today
    avg_health_score = 0
    if meals_today:
        avg_health_score = int(sum(m.health_score for m in meals_today) / len(meals_today))
    else:
        avg_health_score = 0

    return schemas.DashboardSummary(
        consumed=schemas.DailyMacros(
            calories=round(consumed_calories, 1),
            protein=round(consumed_protein, 1),
            carbs=round(consumed_carbs, 1),
            fat=round(consumed_fat, 1)
        ),
        target=schemas.DailyTarget(
            calories=profile.calorie_target,
            protein=profile.protein_target,
            carbs=profile.carbs_target,
            fat=profile.fat_target
        ),
        health_score=avg_health_score,
        meals=meals_today
    )

@router.get("/trends")
def get_weekly_trends(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Returns total daily calorie and protein consumption for the last 7 days.
    """
    profile = db.query(models.AthleteProfile).filter(models.AthleteProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Athlete profile not found")

    trends = []
    
    # Loop last 7 days
    for i in range(6, -1, -1):
        day = date.today() - timedelta(days=i)
        day_start = datetime.combine(day, datetime.min.time())
        day_end = datetime.combine(day, datetime.max.time())
        
        day_meals = db.query(models.Meal).filter(
            models.Meal.user_id == current_user.id,
            models.Meal.created_at >= day_start,
            models.Meal.created_at <= day_end
        ).all()
        
        day_calories = sum(m.total_calories for m in day_meals)
        day_protein = sum(m.total_protein for m in day_meals)
        day_carbs = sum(m.total_carbs for m in day_meals)
        day_fat = sum(m.total_fat for m in day_meals)
        
        avg_health = 0
        if day_meals:
            avg_health = int(sum(m.health_score for m in day_meals) / len(day_meals))
            
        trends.append({
            "date": day.strftime("%a"),  # e.g., Mon, Tue
            "full_date": day.strftime("%Y-%m-%d"),
            "calories": round(day_calories, 1),
            "protein": round(day_protein, 1),
            "carbs": round(day_carbs, 1),
            "fat": round(day_fat, 1),
            "health_score": avg_health,
            "target_calories": profile.calorie_target,
            "target_protein": profile.protein_target,
            "target_carbs": profile.carbs_target,
            "target_fat": profile.fat_target
        })
        
    return trends
