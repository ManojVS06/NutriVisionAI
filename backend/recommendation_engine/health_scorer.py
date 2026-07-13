"""
NutriVision AI — Health Score Calculator

10-Factor Wellness Algorithm (0-100 score).

Factors:
  1. Protein adequacy
  2. Fiber content
  3. Sugar penalty
  4. Sodium penalty
  5. Vegetable coverage
  6. Healthy fat ratio
  7. Processing level penalty
  8. Micronutrient diversity
  9. Calorie appropriateness
  10. Meal balance (variety)
"""

from typing import Optional

# Scoring weights (must sum to 100)
FACTOR_WEIGHTS = {
    "protein_adequacy": 15,
    "fiber_content": 12,
    "sugar_penalty": 10,
    "sodium_penalty": 10,
    "vegetable_coverage": 12,
    "healthy_fat_ratio": 10,
    "processing_penalty": 8,
    "micronutrient_diversity": 10,
    "calorie_appropriateness": 8,
    "meal_balance": 5,
}

# Categories for health scoring
VEGETABLE_CATEGORIES = {"vegetable", "salad", "lentil-soup"}
HIGH_FIBER_FOODS = {"green salad", "kachumber salad", "rajma", "chana masala", "mixed vegetable"}
HIGHLY_PROCESSED = {"samosa", "pakora", "puri", "gulab jamun", "vada pav"}
HEALTHY_FAT_FOODS = {"paneer", "curd", "raita", "egg", "fish"}
REFINED_CARB_FOODS = {"puri", "naan", "gulab jamun", "kheer"}

# Ideal macronutrient ranges per meal (assumes 3 meals/day)
MEAL_PROTEIN_IDEAL = (15, 35)   # grams
MEAL_FIBER_IDEAL = (5, 15)      # grams
MEAL_SODIUM_LIMIT = 800         # mg per meal
MEAL_SUGAR_LIMIT = 15           # grams per meal
MEAL_CALORIES_RANGE = (400, 750) # kcal per meal


def calculate_health_score(
    meal_nutrition: dict,
    food_items: list[dict],
    user_profile: Optional[dict] = None
) -> dict:
    """
    Calculate a comprehensive health score (0-100) for a meal.

    Args:
        meal_nutrition: Output from calculate_meal_nutrition()
        food_items: List of detected food items with food_name
        user_profile: Optional user profile for personalization

    Returns:
        Dict with overall score, factor scores, grade, and feedback
    """
    totals = meal_nutrition.get("totals", {})
    items = meal_nutrition.get("items", [])
    categories = [item.get("category", "unknown") for item in items]
    food_names = [item.get("food_name", "").lower() for item in items]

    scores = {}
    feedbacks = []

    # ─────────────────────────────────────────────────────────────────
    # Factor 1: Protein Adequacy
    # ─────────────────────────────────────────────────────────────────
    protein_g = totals.get("protein", 0)
    if protein_g >= MEAL_PROTEIN_IDEAL[1]:
        scores["protein_adequacy"] = 100
    elif protein_g >= MEAL_PROTEIN_IDEAL[0]:
        scores["protein_adequacy"] = int(
            60 + 40 * (protein_g - MEAL_PROTEIN_IDEAL[0]) / (MEAL_PROTEIN_IDEAL[1] - MEAL_PROTEIN_IDEAL[0])
        )
    else:
        scores["protein_adequacy"] = int(60 * protein_g / MEAL_PROTEIN_IDEAL[0])
        feedbacks.append(f"🥩 Low protein ({protein_g:.1f}g). Add dal, paneer, eggs, or chicken.")

    # ─────────────────────────────────────────────────────────────────
    # Factor 2: Fiber Content
    # ─────────────────────────────────────────────────────────────────
    fiber_g = totals.get("fiber", 0)
    if fiber_g >= MEAL_FIBER_IDEAL[1]:
        scores["fiber_content"] = 100
    elif fiber_g >= MEAL_FIBER_IDEAL[0]:
        scores["fiber_content"] = int(
            60 + 40 * (fiber_g - MEAL_FIBER_IDEAL[0]) / (MEAL_FIBER_IDEAL[1] - MEAL_FIBER_IDEAL[0])
        )
    else:
        scores["fiber_content"] = int(60 * fiber_g / max(MEAL_FIBER_IDEAL[0], 1))
        if fiber_g < 3:
            feedbacks.append(f"🥦 Very low fiber ({fiber_g:.1f}g). Add more vegetables or whole grains.")

    # ─────────────────────────────────────────────────────────────────
    # Factor 3: Sugar Penalty
    # ─────────────────────────────────────────────────────────────────
    sugar_g = totals.get("sugar", 0)
    if sugar_g <= MEAL_SUGAR_LIMIT * 0.4:
        scores["sugar_penalty"] = 100
    elif sugar_g <= MEAL_SUGAR_LIMIT:
        scores["sugar_penalty"] = int(
            100 - 40 * (sugar_g - MEAL_SUGAR_LIMIT * 0.4) / (MEAL_SUGAR_LIMIT * 0.6)
        )
    else:
        scores["sugar_penalty"] = max(0, int(60 - 4 * (sugar_g - MEAL_SUGAR_LIMIT)))
        feedbacks.append(f"🍬 High sugar ({sugar_g:.1f}g). Reduce sweet dishes or sugary drinks.")

    # ─────────────────────────────────────────────────────────────────
    # Factor 4: Sodium Penalty
    # ─────────────────────────────────────────────────────────────────
    sodium_mg = totals.get("sodium", 0)
    if sodium_mg <= 400:
        scores["sodium_penalty"] = 100
    elif sodium_mg <= MEAL_SODIUM_LIMIT:
        scores["sodium_penalty"] = int(
            100 - 40 * (sodium_mg - 400) / (MEAL_SODIUM_LIMIT - 400)
        )
    else:
        scores["sodium_penalty"] = max(0, int(60 - 0.03 * (sodium_mg - MEAL_SODIUM_LIMIT)))
        feedbacks.append(f"🧂 High sodium ({sodium_mg:.0f}mg). Reduce pickle, papad, or processed foods.")

    # ─────────────────────────────────────────────────────────────────
    # Factor 5: Vegetable Coverage
    # ─────────────────────────────────────────────────────────────────
    veg_count = sum(1 for cat in categories if cat in VEGETABLE_CATEGORIES)
    if veg_count >= 2:
        scores["vegetable_coverage"] = 100
    elif veg_count == 1:
        scores["vegetable_coverage"] = 70
    else:
        scores["vegetable_coverage"] = 30
        feedbacks.append("🥗 No vegetables detected. Add a salad or vegetable dish.")

    # ─────────────────────────────────────────────────────────────────
    # Factor 6: Healthy Fat Ratio
    # ─────────────────────────────────────────────────────────────────
    fat_g = totals.get("fat", 0)
    calories = totals.get("calories", 1)
    fat_pct = (fat_g * 9 / max(calories, 1)) * 100
    has_healthy_fat_source = any(f in food_names for f in HEALTHY_FAT_FOODS)

    if 20 <= fat_pct <= 35 and has_healthy_fat_source:
        scores["healthy_fat_ratio"] = 100
    elif 15 <= fat_pct <= 40:
        scores["healthy_fat_ratio"] = 75
    elif fat_pct < 15:
        scores["healthy_fat_ratio"] = 60
        feedbacks.append("🥑 Low healthy fats. Add curd, paneer, or a small amount of ghee.")
    else:
        scores["healthy_fat_ratio"] = max(30, int(100 - fat_pct))
        feedbacks.append(f"🛑 High fat content ({fat_pct:.0f}% of calories). Reduce fried foods.")

    # ─────────────────────────────────────────────────────────────────
    # Factor 7: Processing Level
    # ─────────────────────────────────────────────────────────────────
    processed_count = sum(1 for f in food_names if f in HIGHLY_PROCESSED)
    if processed_count == 0:
        scores["processing_penalty"] = 100
    elif processed_count == 1:
        scores["processing_penalty"] = 60
        feedbacks.append("🚫 Contains processed/fried food. Opt for healthier cooking methods.")
    else:
        scores["processing_penalty"] = max(10, 60 - 25 * (processed_count - 1))
        feedbacks.append(f"🚫 {processed_count} processed/fried items. This is too high.")

    # ─────────────────────────────────────────────────────────────────
    # Factor 8: Micronutrient Diversity
    # ─────────────────────────────────────────────────────────────────
    iron_mg = totals.get("iron", 0)
    calcium_mg = totals.get("calcium", 0)
    vitamin_c_mg = totals.get("vitamin_c", 0)
    vitamin_a_mcg = totals.get("vitamin_a", 0)

    micro_score = 0
    if iron_mg >= 5: micro_score += 25
    elif iron_mg >= 2: micro_score += 12
    if calcium_mg >= 250: micro_score += 25
    elif calcium_mg >= 100: micro_score += 12
    if vitamin_c_mg >= 20: micro_score += 25
    elif vitamin_c_mg >= 10: micro_score += 12
    if vitamin_a_mcg >= 150: micro_score += 25
    elif vitamin_a_mcg >= 50: micro_score += 12

    scores["micronutrient_diversity"] = micro_score

    # ─────────────────────────────────────────────────────────────────
    # Factor 9: Calorie Appropriateness
    # ─────────────────────────────────────────────────────────────────
    if MEAL_CALORIES_RANGE[0] <= calories <= MEAL_CALORIES_RANGE[1]:
        scores["calorie_appropriateness"] = 100
    elif calories < MEAL_CALORIES_RANGE[0]:
        scores["calorie_appropriateness"] = int(70 * calories / MEAL_CALORIES_RANGE[0])
        feedbacks.append(f"📉 Low calorie meal ({calories:.0f} kcal). You may be undereating.")
    else:
        excess = calories - MEAL_CALORIES_RANGE[1]
        scores["calorie_appropriateness"] = max(20, int(100 - 0.1 * excess))
        if excess > 300:
            feedbacks.append(f"📈 High calorie meal ({calories:.0f} kcal). Consider smaller portions.")

    # ─────────────────────────────────────────────────────────────────
    # Factor 10: Meal Balance (Variety)
    # ─────────────────────────────────────────────────────────────────
    unique_categories = len(set(categories))
    if unique_categories >= 4:
        scores["meal_balance"] = 100
    elif unique_categories == 3:
        scores["meal_balance"] = 80
    elif unique_categories == 2:
        scores["meal_balance"] = 55
    else:
        scores["meal_balance"] = 30
        feedbacks.append("🍽️ Limited variety. Aim for grain + protein + vegetable + dairy.")

    # ─────────────────────────────────────────────────────────────────
    # Weighted Final Score
    # ─────────────────────────────────────────────────────────────────
    overall = sum(
        scores[factor] * weight / 100
        for factor, weight in FACTOR_WEIGHTS.items()
        if factor in scores
    )
    overall = round(overall)
    overall = max(0, min(100, overall))

    # Grade
    if overall >= 85:
        grade = "Excellent"
        grade_emoji = "🌟"
        grade_color = "#22c55e"
    elif overall >= 70:
        grade = "Good"
        grade_emoji = "✅"
        grade_color = "#84cc16"
    elif overall >= 55:
        grade = "Fair"
        grade_emoji = "⚠️"
        grade_color = "#f59e0b"
    elif overall >= 40:
        grade = "Poor"
        grade_emoji = "❌"
        grade_color = "#ef4444"
    else:
        grade = "Very Poor"
        grade_emoji = "🚨"
        grade_color = "#dc2626"

    # Positive notes
    positives = []
    if scores["protein_adequacy"] >= 80:
        positives.append("✅ Good protein content")
    if scores["fiber_content"] >= 80:
        positives.append("✅ Excellent fiber intake")
    if scores["vegetable_coverage"] >= 70:
        positives.append("✅ Good vegetable coverage")
    if scores["sodium_penalty"] >= 80:
        positives.append("✅ Low sodium")
    if scores["processing_penalty"] == 100:
        positives.append("✅ Minimally processed meal")

    return {
        "overall_score": overall,
        "grade": grade,
        "grade_emoji": grade_emoji,
        "grade_color": grade_color,
        "factor_scores": scores,
        "factor_weights": FACTOR_WEIGHTS,
        "feedback": feedbacks,
        "positives": positives,
        "summary": f"Your meal scored {overall}/100 ({grade}). {feedbacks[0] if feedbacks else 'Great meal choice!'}",
    }
