import os
import sys
from datetime import datetime, timedelta
import numpy as np
import cv2

# Set path so Python can find app modules
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

from app.database import SessionLocal, engine, Base
from app import models
from app.api.auth import hash_password
from app.api.athlete import calculate_athlete_targets
from app.services.cv_pipeline import FOOD_DENSITY_NUTRITION
from app.config import settings

def create_dummy_images():
    """Generates simple solid-color placeholder images for historical meals to avoid 404s"""
    print("Generating placeholder images in static uploads...")
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # 500x500 images
    dummy_meals = {
        "dosa": (240, 220, 180),      # Tan
        "biryani": (180, 120, 80),    # Brownish red
        "thali": (200, 200, 150),     # Grayish yellow
        "salad": (100, 200, 100)      # Green
    }
    
    for prefix, color in dummy_meals.items():
        # Base image
        img = np.zeros((500, 500, 3), dtype=np.uint8)
        img[:] = color
        
        # Add text
        cv2.putText(img, f"{prefix.upper()} IMAGE", (100, 250), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        
        # Save original and processed variations
        cv2.imwrite(os.path.join(settings.UPLOAD_DIR, f"{prefix}.jpg"), img)
        
        # Processed with bounding box
        processed = img.copy()
        cv2.rectangle(processed, (50, 50), (450, 450), (0, 255, 0), 3)
        cv2.putText(processed, "DETECTION", (60, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.imwrite(os.path.join(settings.UPLOAD_DIR, f"{prefix}_processed.jpg"), processed)
        
        # Mask overlay
        mask = img.copy()
        cv2.circle(mask, (250, 250), 180, (255, 0, 0), -1)
        cv2.addWeighted(mask, 0.4, img, 0.6, 0, mask)
        cv2.imwrite(os.path.join(settings.UPLOAD_DIR, f"{prefix}_mask.jpg"), mask)
        
        # Depth Map
        depth = np.zeros((500, 500, 1), dtype=np.uint8)
        cv2.circle(depth, (250, 250), 180, 255, -1)
        depth = cv2.distanceTransform(depth, cv2.DIST_L2, 3)
        cv2.normalize(depth, depth, 0, 255, cv2.NORM_MINMAX)
        depth_color = cv2.applyColorMap(depth.astype(np.uint8), cv2.COLORMAP_INFERNO)
        cv2.imwrite(os.path.join(settings.UPLOAD_DIR, f"{prefix}_depth.jpg"), depth_color)

def seed_database():
    print("Starting database seeding...")
    db = SessionLocal()
    
    # 1. Clear existing database tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    # 2. Seed Nutrition reference table (IFCT data)
    print("Seeding IFCT reference database...")
    for food_name, nutrition in FOOD_DENSITY_NUTRITION.items():
        db_nutrition = models.NutritionDB(
            name=food_name,
            category=nutrition["category"],
            calories_per_100g=nutrition["calories_100g"],
            protein_per_100g=nutrition["protein_100g"],
            carbs_per_100g=nutrition["carbs_100g"],
            fat_per_100g=nutrition["fat_100g"],
            fiber_per_100g=nutrition["fiber_100g"],
            sodium_per_100g=nutrition["sodium_100g"],
            sugar_per_100g=nutrition["sugar_100g"],
            density_g_cm3=nutrition["density"]
        )
        db.add(db_nutrition)
        
    db.commit()
    
    # 3. Seed Demo User
    print("Creating demouser...")
    demo_user = models.User(
        username="demouser",
        email="demo@nutrivision.ai",
        password_hash=hash_password("demopassword")
    )
    db.add(demo_user)
    db.commit()
    db.refresh(demo_user)
    
    # 4. Create Athlete Profile for demouser
    # Weight: 74 kg, Height: 178 cm, Age: 25, Sport: Bodybuilder, Phase: Hypertrophy
    targets = calculate_athlete_targets(74.0, 178.0, 25, "Male", "Bodybuilder", "Hypertrophy")
    demo_profile = models.AthleteProfile(
        user_id=demo_user.id,
        weight=74.0,
        height=178.0,
        age=25,
        gender="Male",
        sport="Bodybuilder",
        training_phase="Bulk", # Hypertrophy bulk
        calorie_target=targets["calorie_target"],
        protein_target=targets["protein_target"],
        carbs_target=targets["carbs_target"],
        fat_target=targets["fat_target"]
    )
    db.add(demo_profile)
    db.commit()
    
    # Create the images in the static folder
    create_dummy_images()
    
    # 5. Seed 7-Day History of meals
    print("Seeding 7 days of meal logs...")
    today = datetime.now()
    
    # Define meals for each day
    # We will log breakfast, lunch, and dinner with different calorie loads
    history_meals = [
        # Today - Breakfast
        {
            "days_ago": 0,
            "hour": 8,
            "prefix": "dosa",
            "foods": [
                {"name": "Idli", "weight": 130.0, "vol": 200.0, "bbox": "[100,100,250,250]"},
                {"name": "Sambar", "weight": 150.0, "vol": 150.0, "bbox": "[280,100,380,200]"}
            ]
        },
        # Yesterday - Dinner
        {
            "days_ago": 1,
            "hour": 20,
            "prefix": "thali",
            "foods": [
                {"name": "Roti / Chapati", "weight": 72.0, "vol": 120.0, "bbox": "[80,180,230,320]"},
                {"name": "Paneer Butter Masala", "weight": 150.0, "vol": 142.0, "bbox": "[190,50,300,150]"},
                {"name": "Mixed Vegetable Salad", "weight": 30.0, "vol": 100.0, "bbox": "[310,90,390,170]"}
            ]
        },
        # Yesterday - Lunch
        {
            "days_ago": 1,
            "hour": 13,
            "prefix": "thali",
            "foods": [
                {"name": "Cooked White Rice", "weight": 164.0, "vol": 200.0, "bbox": "[240,180,390,320]"},
                {"name": "Yellow Dal Tadka", "weight": 180.0, "vol": 180.0, "bbox": "[60,50,170,150]"},
                {"name": "Mixed Vegetable Salad", "weight": 40.0, "vol": 130.0, "bbox": "[310,90,390,170]"}
            ]
        },
        # 2 Days Ago - Cheat Meal Biryani
        {
            "days_ago": 2,
            "hour": 14,
            "prefix": "biryani",
            "foods": [
                {"name": "Chicken Biryani", "weight": 350.0, "vol": 388.0, "bbox": "[60,60,420,420]"},
                {"name": "Boiled Egg", "weight": 60.5, "vol": 55.0, "bbox": "[120,120,200,200]"}
            ]
        },
        # 3 Days Ago - Breakfast
        {
            "days_ago": 3,
            "hour": 9,
            "prefix": "dosa",
            "foods": [
                {"name": "Idli", "weight": 195.0, "vol": 300.0, "bbox": "[100,100,300,300]"},
                {"name": "Sambar", "weight": 200.0, "vol": 200.0, "bbox": "[320,100,450,230]"}
            ]
        },
        # 4 Days Ago - Dinner
        {
            "days_ago": 4,
            "hour": 21,
            "prefix": "thali",
            "foods": [
                {"name": "Roti / Chapati", "weight": 108.0, "vol": 180.0, "bbox": "[80,180,230,320]"},
                {"name": "Yellow Dal Tadka", "weight": 200.0, "vol": 200.0, "bbox": "[60,50,170,150]"}
            ]
        },
        # 5 Days Ago - Lunch
        {
            "days_ago": 5,
            "hour": 13,
            "prefix": "thali",
            "foods": [
                {"name": "Cooked White Rice", "weight": 200.0, "vol": 243.0, "bbox": "[240,180,390,320]"},
                {"name": "Paneer Butter Masala", "weight": 160.0, "vol": 152.0, "bbox": "[190,50,300,150]"}
            ]
        },
        # 6 Days Ago - Breakfast
        {
            "days_ago": 6,
            "hour": 8,
            "prefix": "dosa",
            "foods": [
                {"name": "Idli", "weight": 130.0, "vol": 200.0, "bbox": "[100,100,250,250]"},
                {"name": "Sambar", "weight": 150.0, "vol": 150.0, "bbox": "[280,100,380,200]"}
            ]
        }
    ]

    for m_data in history_meals:
        meal_time = today - timedelta(days=m_data["days_ago"])
        # Set hour
        meal_time = meal_time.replace(hour=m_data["hour"], minute=0, second=0, microsecond=0)
        
        prefix = m_data["prefix"]
        
        # Create meal
        meal = models.Meal(
            user_id=demo_user.id,
            image_url=f"/static/uploads/{prefix}.jpg",
            processed_url=f"/static/uploads/{prefix}_processed.jpg",
            mask_url=f"/static/uploads/{prefix}_mask.jpg",
            depth_url=f"/static/uploads/{prefix}_depth.jpg",
            created_at=meal_time
        )
        db.add(meal)
        db.commit()
        db.refresh(meal)
        
        # Add food items
        total_cal = 0.0
        total_prot = 0.0
        total_carb = 0.0
        total_fat = 0.0
        total_fib = 0.0
        total_sod = 0.0
        total_sug = 0.0
        
        food_list_for_score = []
        
        for f in m_data["foods"]:
            ref = FOOD_DENSITY_NUTRITION[f["name"]]
            w = f["weight"]
            
            cal = (ref["calories_100g"] * w) / 100.0
            prot = (ref["protein_100g"] * w) / 100.0
            carb = (ref["carbs_100g"] * w) / 100.0
            fat = (ref["fat_100g"] * w) / 100.0
            fib = (ref["fiber_100g"] * w) / 100.0
            sod = (ref["sodium_100g"] * w) / 100.0
            sug = (ref["sugar_100g"] * w) / 100.0
            
            food_item = models.FoodItem(
                meal_id=meal.id,
                name=f["name"],
                weight_g=w,
                volume_cm3=f["vol"],
                density=ref["density"],
                bounding_box=f["bbox"],
                calories=round(cal, 1),
                protein=round(prot, 2),
                carbs=round(carb, 2),
                fat=round(fat, 2),
                fiber=round(fib, 2),
                sodium=round(sod, 1),
                sugar=round(sug, 2)
            )
            db.add(food_item)
            
            total_cal += cal
            total_prot += prot
            total_carb += carb
            total_fat += fat
            total_fib += fib
            total_sod += sod
            total_sug += sug
            
            food_list_for_score.append({
                "name": f["name"],
                "weight_g": w,
                "calories": cal,
                "protein": prot,
                "carbs": carb,
                "fat": fat,
                "fiber": fib,
                "sodium": sod,
                "sugar": sug
            })
            
        meal.total_calories = round(total_cal, 1)
        meal.total_protein = round(total_prot, 2)
        meal.total_carbs = round(total_carb, 2)
        meal.total_fat = round(total_fat, 2)
        meal.total_fiber = round(total_fib, 2)
        meal.total_sodium = round(total_sod, 1)
        meal.total_sugar = round(total_sug, 2)
        
        # Score & Advice
        from app.services.nutrition import calculate_healthy_score
        from app.services.llm_coach import generate_coach_recommendation
        
        meal.health_score = calculate_healthy_score(food_list_for_score)
        meal.coach_notes = generate_coach_recommendation(demo_profile, food_list_for_score)
        
        db.commit()
        
    db.close()
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    seed_database()
