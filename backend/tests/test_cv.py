import os
import sys
# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from app.services.nutrition import calculate_healthy_score
from app.api.athlete import calculate_athlete_targets

def test_calculate_healthy_score():
    # 1. Test clean salad meal
    salad_meal = [
        {
            "name": "Mixed Vegetable Salad",
            "weight_g": 100.0,
            "calories": 25.0,
            "protein": 1.2,
            "carbs": 4.5,
            "fat": 0.2,
            "fiber": 2.5,
            "sodium": 10.0,
            "sugar": 2.0
        }
    ]
    salad_score = calculate_healthy_score(salad_meal)
    assert salad_score > 75, f"Salad score should be high, got {salad_score}"
    
    # 2. Test high sodium, processed meal
    processed_meal = [
        {
            "name": "Paneer Butter Masala",
            "weight_g": 200.0,
            "calories": 450.0,
            "protein": 18.0,
            "carbs": 12.0,
            "fat": 37.0,
            "fiber": 1.5,
            "sodium": 800.0,
            "sugar": 8.0
        }
    ]
    processed_score = calculate_healthy_score(processed_meal)
    assert processed_score < salad_score, "Processed rich meal should score lower than salad"

def test_athlete_targets():
    # Male sprinter weight 70kg, 175cm, age 25
    sprint_targets = calculate_athlete_targets(
        weight_kg=70.0,
        height_cm=175.0,
        age=25,
        gender="Male",
        sport="Sprinting",
        training_phase="Bulk"
    )
    
    assert sprint_targets["calorie_target"] > 2000
    assert sprint_targets["protein_target"] == 140 # 70 * 2.0
    
    # Rest Day target should be lower in calories
    rest_targets = calculate_athlete_targets(
        weight_kg=70.0,
        height_cm=175.0,
        age=25,
        gender="Male",
        sport="Sprinting",
        training_phase="Rest Day"
    )
    assert rest_targets["calorie_target"] < sprint_targets["calorie_target"]
