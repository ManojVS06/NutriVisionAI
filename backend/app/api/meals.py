import os
import uuid
import json
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Header, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.api.auth import get_current_user
from app import models, schemas
from app.config import settings
from app.services.cv_pipeline import analyze_uploaded_image, FOOD_DENSITY_NUTRITION
from app.services.nutrition import calculate_healthy_score
from app.services.llm_coach import generate_coach_recommendation

router = APIRouter(prefix="/meals", tags=["Meals & Nutrition Engine"])

@router.post("/upload", response_model=schemas.MealResponse, status_code=status.HTTP_201_CREATED)
async def upload_meal(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Validate file extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".jpg", ".jpeg", ".png"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported image format. Please upload JPEG or PNG."
        )

    # Generate unique filename
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
    
    # Save the uploaded file
    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save uploaded image: {str(e)}"
        )

    # Process image through CV pipeline
    try:
        cv_result = analyze_uploaded_image(unique_filename, db)
    except Exception as e:
        # Clean up file in case of failure
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Computer Vision processing failed: {str(e)}"
        )

    # Get user profile for coach context
    profile = db.query(models.AthleteProfile).filter(models.AthleteProfile.user_id == current_user.id).first()

    # Calculate overall health score
    health_score = calculate_healthy_score(cv_result["food_items"])
    
    # Generate coach notes
    coach_notes = generate_coach_recommendation(
        profile=profile,
        meal_foods=cv_result["food_items"]
    )

    # Create Meal record
    new_meal = models.Meal(
        user_id=current_user.id,
        image_url=cv_result["original_url"],
        processed_url=cv_result["processed_url"],
        mask_url=cv_result["mask_url"],
        depth_url=cv_result["depth_url"],
        health_score=health_score,
        coach_notes=coach_notes,
        quality_score=cv_result.get("quality_score", 100.0),
        detection_method=cv_result.get("detection_method", "opencv_fallback")
    )
    db.add(new_meal)
    db.commit()
    db.refresh(new_meal)

    # Create individual FoodItem records
    total_cal = 0.0
    total_prot = 0.0
    total_carb = 0.0
    total_fat = 0.0
    total_fib = 0.0
    total_sod = 0.0
    total_sug = 0.0

    for item in cv_result["food_items"]:
        food_item = models.FoodItem(
            meal_id=new_meal.id,
            name=item["name"],
            weight_g=item["weight_g"],
            volume_cm3=item["volume_cm3"],
            density=item["density"],
            bounding_box=item["bounding_box"],
            calories=item["calories"],
            protein=item["protein"],
            carbs=item["carbs"],
            fat=item["fat"],
            fiber=item["fiber"],
            sodium=item["sodium"],
            sugar=item["sugar"],
            confidence=item.get("confidence", 1.0),
            detection_method=item.get("detection_method", "opencv_fallback")
        )
        db.add(food_item)
        
        # Aggregate macros
        total_cal += item["calories"]
        total_prot += item["protein"]
        total_carb += item["carbs"]
        total_fat += item["fat"]
        total_fib += item["fiber"]
        total_sod += item["sodium"]
        total_sug += item["sugar"]

    # Update Meal aggregates
    new_meal.total_calories = round(total_cal, 1)
    new_meal.total_protein = round(total_prot, 2)
    new_meal.total_carbs = round(total_carb, 2)
    new_meal.total_fat = round(total_fat, 2)
    new_meal.total_fiber = round(total_fib, 2)
    new_meal.total_sodium = round(total_sod, 1)
    new_meal.total_sugar = round(total_sug, 2)
    
    db.commit()
    db.refresh(new_meal)
    
    return new_meal

@router.get("", response_model=List[schemas.MealResponse])
def get_user_meals(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(models.Meal).filter(models.Meal.user_id == current_user.id).order_by(models.Meal.created_at.desc()).all()

@router.get("/{meal_id}", response_model=schemas.MealResponse)
def get_meal_details(
    meal_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    meal = db.query(models.Meal).filter(
        models.Meal.id == meal_id,
        models.Meal.user_id == current_user.id
    ).first()
    
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")
        
    return meal

@router.put("/{meal_id}", response_model=schemas.MealResponse)
def update_meal_portions(
    meal_id: int,
    update_req: schemas.MealUpdateRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
    x_gemini_key: Optional[str] = Header(None)
):
    meal = db.query(models.Meal).filter(
        models.Meal.id == meal_id,
        models.Meal.user_id == current_user.id
    ).first()
    
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")
        
    # Update individual food items weights and recalculate values
    for update_item in update_req.food_items:
        db_food = db.query(models.FoodItem).filter(
            models.FoodItem.id == update_item.id,
            models.FoodItem.meal_id == meal.id
        ).first()
        
        if db_food:
            new_weight = update_item.weight_g
            old_weight = db_food.weight_g
            
            # Recalculate volumetrics and macros based on ratio
            ratio = new_weight / (old_weight if old_weight > 0 else 1)
            
            db_food.weight_g = new_weight
            db_food.volume_cm3 = round(db_food.volume_cm3 * ratio, 1)
            
            # Recalculate using static values or ratio
            food_ref = FOOD_DENSITY_NUTRITION.get(db_food.name)
            if food_ref:
                db_food.calories = round((food_ref["calories_100g"] * new_weight) / 100.0, 1)
                db_food.protein = round((food_ref["protein_100g"] * new_weight) / 100.0, 2)
                db_food.carbs = round((food_ref["carbs_100g"] * new_weight) / 100.0, 2)
                db_food.fat = round((food_ref["fat_100g"] * new_weight) / 100.0, 2)
                db_food.fiber = round((food_ref["fiber_100g"] * new_weight) / 100.0, 2)
                db_food.sodium = round((food_ref["sodium_100g"] * new_weight) / 100.0, 1)
                db_food.sugar = round((food_ref["sugar_100g"] * new_weight) / 100.0, 2)
            else:
                # Proportional scaling
                db_food.calories = round(db_food.calories * ratio, 1)
                db_food.protein = round(db_food.protein * ratio, 2)
                db_food.carbs = round(db_food.carbs * ratio, 2)
                db_food.fat = round(db_food.fat * ratio, 2)
                db_food.fiber = round(db_food.fiber * ratio, 2)
                db_food.sodium = round(db_food.sodium * ratio, 1)
                db_food.sugar = round(db_food.sugar * ratio, 2)
                
    db.commit()
    db.refresh(meal)
    
    # Recalculate aggregates of the meal
    total_cal = 0.0
    total_prot = 0.0
    total_carb = 0.0
    total_fat = 0.0
    total_fib = 0.0
    total_sod = 0.0
    total_sug = 0.0
    
    cv_foods_format = []
    
    for food in meal.food_items:
        total_cal += food.calories
        total_prot += food.protein
        total_carb += food.carbs
        total_fat += food.fat
        total_fib += food.fiber
        total_sod += food.sodium
        total_sug += food.sugar
        
        cv_foods_format.append({
            "name": food.name,
            "weight_g": food.weight_g,
            "calories": food.calories,
            "protein": food.protein,
            "carbs": food.carbs,
            "fat": food.fat,
            "fiber": food.fiber,
            "sodium": food.sodium,
            "sugar": food.sugar
        })
        
    meal.total_calories = round(total_cal, 1)
    meal.total_protein = round(total_prot, 2)
    meal.total_carbs = round(total_carb, 2)
    meal.total_fat = round(total_fat, 2)
    meal.total_fiber = round(total_fib, 2)
    meal.total_sodium = round(total_sod, 1)
    meal.total_sugar = round(total_sug, 2)
    
    # Recalculate Healthy Score
    meal.health_score = calculate_healthy_score(cv_foods_format)
    
    # Recalculate coach advice
    profile = db.query(models.AthleteProfile).filter(models.AthleteProfile.user_id == current_user.id).first()
    meal.coach_notes = generate_coach_recommendation(
        profile=profile,
        meal_foods=cv_foods_format,
        api_key_override=x_gemini_key
    )
    
    db.commit()
    db.refresh(meal)
    return meal

@router.delete("/{meal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meal(
    meal_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    meal = db.query(models.Meal).filter(
        models.Meal.id == meal_id,
        models.Meal.user_id == current_user.id
    ).first()
    
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")
        
    # Clean up image files from static uploads if they exist
    for path_attr in ["image_url", "processed_url", "mask_url", "depth_url"]:
        relative_path = getattr(meal, path_attr)
        if relative_path:
            # path starts with /static/
            full_path = os.path.join(settings.STATIC_DIR, relative_path.replace("/static/", "", 1).replace("/", os.sep))
            if os.path.exists(full_path):
                try:
                    os.remove(full_path)
                except Exception:
                    pass
                    
    db.delete(meal)
    db.commit()
    return None
