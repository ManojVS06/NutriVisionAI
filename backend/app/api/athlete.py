from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional, List, Dict
from pydantic import BaseModel
from app.database import get_db
from app.api.auth import get_current_user
from app import models, schemas
from app.services.llm_coach import handle_chatbot_conversation

router = APIRouter(prefix="/athlete", tags=["Athlete & Coach"])

def calculate_athlete_targets(
    weight_kg: float,
    height_cm: float,
    age: int,
    gender: str,
    sport: str,
    training_phase: str
) -> dict:
    """
    Harris-Benedict equation to calculate BMR and apply activity factors
    and training phase offsets to get targeted macros.
    """
    # 1. BMR Calculation
    if gender.lower() == "male":
        bmr = 88.362 + (13.397 * weight_kg) + (4.799 * height_cm) - (5.677 * age)
    else:
        bmr = 447.593 + (9.247 * weight_kg) + (3.098 * height_cm) - (4.330 * age)
        
    # 2. Activity Multiplier based on sport selection
    multipliers = {
        "General Fitness": 1.375,  # Moderately active
        "Bodybuilder": 1.55,       # Active
        "Sprinting": 1.6,          # Active
        "Marathon": 1.725,         # Very active
        "Cricket": 1.5             # Active
    }
    multiplier = multipliers.get(sport, 1.4)
    tdee = bmr * multiplier
    
    # 3. Macro Splits based on Sport and Phase
    if training_phase == "Cut":
        calories = int(tdee - 450)
        protein_g = int(weight_kg * 2.2) # Save muscle
        fat_g = int((calories * 0.20) / 9)
        carbs_g = int((calories - (protein_g * 4) - (fat_g * 9)) / 4)
    elif training_phase == "Bulk" or training_phase == "Hypertrophy":
        calories = int(tdee + 400)
        protein_g = int(weight_kg * 2.0) # Muscle growth
        fat_g = int((calories * 0.25) / 9)
        carbs_g = int((calories - (protein_g * 4) - (fat_g * 9)) / 4)
    elif training_phase == "Competition Day":
        calories = int(tdee + 150)
        protein_g = int(weight_kg * 1.6)
        if sport in ["Sprinting", "Marathon"]:
            # High Carb loading
            carbs_g = int((calories * 0.65) / 4)
            fat_g = int((calories - (protein_g * 4) - (carbs_g * 4)) / 9)
        else:
            fat_g = int((calories * 0.25) / 9)
            carbs_g = int((calories - (protein_g * 4) - (fat_g * 9)) / 4)
    elif training_phase == "Rest Day":
        calories = int(tdee - 150)
        protein_g = int(weight_kg * 1.5)
        fat_g = int((calories * 0.30) / 9)
        carbs_g = int((calories - (protein_g * 4) - (fat_g * 9)) / 4)
    else: # General fitness / maintain
        calories = int(tdee)
        protein_g = int(weight_kg * 1.7)
        fat_g = int((calories * 0.25) / 9)
        carbs_g = int((calories - (protein_g * 4) - (fat_g * 9)) / 4)
        
    return {
        "calorie_target": max(1200, calories),
        "protein_target": max(40, protein_g),
        "carbs_target": max(80, carbs_g),
        "fat_target": max(30, fat_g)
    }

@router.get("/profile", response_model=schemas.AthleteProfileResponse)
def get_profile(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(models.AthleteProfile).filter(models.AthleteProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Athlete profile not found")
    return profile

@router.put("/profile", response_model=schemas.AthleteProfileResponse)
def update_profile(
    profile_in: schemas.AthleteProfileUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(models.AthleteProfile).filter(models.AthleteProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Athlete profile not found")
        
    # Update fields
    for field, value in profile_in.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
        
    # Recalculate targets
    targets = calculate_athlete_targets(
        profile.weight,
        profile.height,
        profile.age,
        profile.gender,
        profile.sport,
        profile.training_phase
    )
    
    profile.calorie_target = targets["calorie_target"]
    profile.protein_target = targets["protein_target"]
    profile.carbs_target = targets["carbs_target"]
    profile.fat_target = targets["fat_target"]
    
    db.commit()
    db.refresh(profile)
    return profile

class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, str]] = []

from pydantic import BaseModel

@router.post("/coach-chat")
def chatbot_interaction(
    request: ChatRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(models.AthleteProfile).filter(models.AthleteProfile.user_id == current_user.id).first()
    
    coach_reply = handle_chatbot_conversation(
        profile=profile,
        history=request.history,
        user_message=request.message
    )
    
    return {"reply": coach_reply}
