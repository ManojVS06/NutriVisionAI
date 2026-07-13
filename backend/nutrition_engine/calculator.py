"""
NutriVision AI — Nutrition Calculation Engine

Calculates total meal nutrition from individual food items.
"""
from typing import Optional
from nutrition_engine.ifct_database import search_food


NUTRIENT_KEYS = [
    "calories", "protein", "carbs", "fat", "fiber",
    "sugar", "sodium", "calcium", "iron", "potassium",
    "vitamin_c", "vitamin_a", "folate", "zinc"
]

NUTRIENT_UNITS = {
    "calories": "kcal", "protein": "g", "carbs": "g", "fat": "g",
    "fiber": "g", "sugar": "g", "sodium": "mg", "calcium": "mg",
    "iron": "mg", "potassium": "mg", "vitamin_c": "mg",
    "vitamin_a": "mcg", "folate": "mcg", "zinc": "mg"
}

# Daily reference values (ICMR, India — adult male 2000 kcal)
DAILY_REFERENCE_VALUES = {
    "calories": 2000, "protein": 60, "carbs": 275, "fat": 65,
    "fiber": 25, "sugar": 50, "sodium": 2000, "calcium": 800,
    "iron": 17, "potassium": 3500, "vitamin_c": 40,
    "vitamin_a": 600, "folate": 200, "zinc": 10
}


def calculate_nutrition_for_item(food_name: str, weight_g: float) -> Optional[dict]:
    """
    Calculate nutrition for a single food item given weight in grams.

    Args:
        food_name: Name of the food (searched in IFCT database)
        weight_g: Weight of the food in grams

    Returns:
        Dict with all nutrient values scaled to weight, or None if not found
    """
    result = search_food(food_name)
    if result is None:
        return None

    canonical_name, per_100g = result
    scale = weight_g / 100.0

    nutrition = {
        "food_name": canonical_name,
        "query_name": food_name,
        "weight_g": weight_g,
        "per_100g": {},
        "total": {},
        "daily_percent": {},
        "category": per_100g.get("category", "unknown"),
        "region": per_100g.get("region", "unknown"),
    }

    for key in NUTRIENT_KEYS:
        base_val = per_100g.get(key, 0)
        total_val = round(base_val * scale, 1)
        dvp = round((total_val / DAILY_REFERENCE_VALUES[key]) * 100, 1) if DAILY_REFERENCE_VALUES[key] > 0 else 0

        nutrition["per_100g"][key] = base_val
        nutrition["total"][key] = total_val
        nutrition["daily_percent"][key] = dvp

    nutrition["units"] = NUTRIENT_UNITS
    return nutrition


def calculate_meal_nutrition(food_items: list[dict]) -> dict:
    """
    Calculate total nutrition for a meal with multiple food items.

    Args:
        food_items: List of dicts, each with 'food_name' and 'weight_g'

    Returns:
        Complete meal nutrition breakdown
    """
    individual_items = []
    totals = {key: 0.0 for key in NUTRIENT_KEYS}
    not_found = []

    for item in food_items:
        food_name = item.get("food_name", "")
        weight_g = item.get("weight_g", 0)

        nutrition = calculate_nutrition_for_item(food_name, weight_g)
        if nutrition:
            individual_items.append(nutrition)
            for key in NUTRIENT_KEYS:
                totals[key] += nutrition["total"].get(key, 0)
        else:
            not_found.append(food_name)

    # Round totals
    totals = {k: round(v, 1) for k, v in totals.items()}

    # Macro percentages
    total_cals = totals["calories"]
    macro_cals = {
        "protein_kcal": round(totals["protein"] * 4, 1),
        "carbs_kcal": round(totals["carbs"] * 4, 1),
        "fat_kcal": round(totals["fat"] * 9, 1),
    }
    macro_pct = {}
    if total_cals > 0:
        macro_pct["protein_pct"] = round((macro_cals["protein_kcal"] / total_cals) * 100, 1)
        macro_pct["carbs_pct"] = round((macro_cals["carbs_kcal"] / total_cals) * 100, 1)
        macro_pct["fat_pct"] = round((macro_cals["fat_kcal"] / total_cals) * 100, 1)
    else:
        macro_pct = {"protein_pct": 0, "carbs_pct": 0, "fat_pct": 0}

    # Daily value percentages for totals
    daily_percent = {
        key: round((totals[key] / DAILY_REFERENCE_VALUES[key]) * 100, 1)
        for key in NUTRIENT_KEYS
        if DAILY_REFERENCE_VALUES.get(key, 0) > 0
    }

    return {
        "items": individual_items,
        "totals": totals,
        "macro_percentages": macro_pct,
        "macro_calories": macro_cals,
        "daily_value_percent": daily_percent,
        "units": NUTRIENT_UNITS,
        "not_found_foods": not_found,
        "item_count": len(individual_items),
        "total_weight_g": sum(item.get("weight_g", 0) for item in food_items),
    }


def get_nutrient_summary(meal_nutrition: dict) -> str:
    """Generate a human-readable nutrition summary for the AI coach."""
    t = meal_nutrition["totals"]
    mp = meal_nutrition["macro_percentages"]
    return (
        f"Meal contains {t['calories']:.0f} kcal "
        f"({mp.get('protein_pct', 0):.0f}% protein / "
        f"{mp.get('carbs_pct', 0):.0f}% carbs / "
        f"{mp.get('fat_pct', 0):.0f}% fat). "
        f"Protein: {t['protein']:.1f}g, Carbs: {t['carbs']:.1f}g, "
        f"Fat: {t['fat']:.1f}g, Fiber: {t['fiber']:.1f}g, "
        f"Sodium: {t['sodium']:.0f}mg."
    )
