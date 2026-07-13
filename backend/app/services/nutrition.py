from typing import List, Dict, Any

def calculate_healthy_score(food_items: List[Dict[str, Any]]) -> int:
    """
    Calculates a comprehensive Healthy Score (0-100) based on nutritional properties.
    Fibers, proteins, and low-processing elements raise the score.
    Saturates (fats), high sodium, and high sugar lower the score.
    """
    if not food_items:
        return 50

    # Sum up total values
    total_weight = sum(item["weight_g"] for item in food_items)
    if total_weight == 0:
        return 50

    total_calories = sum(item["calories"] for item in food_items)
    total_protein = sum(item["protein"] for item in food_items)
    total_carbs = sum(item["carbs"] for item in food_items)
    total_fat = sum(item["fat"] for item in food_items)
    total_fiber = sum(item["fiber"] for item in food_items)
    total_sodium = sum(item["sodium"] for item in food_items)
    total_sugar = sum(item["sugar"] for item in food_items)

    # Base score
    score = 60.0

    # 1. Protein Bonus: up to +15 points
    # 0.8g protein per kg is typical. A meal with high protein percentage relative to weight is good.
    protein_ratio = (total_protein / total_weight) * 100.0  # protein g per 100g
    score += min(15.0, protein_ratio * 1.5)

    # 2. Fiber Bonus: up to +15 points
    # High fiber indicates unprocessed whole grains / veggies.
    fiber_ratio = (total_fiber / total_weight) * 100.0
    score += min(15.0, fiber_ratio * 5.0)

    # 3. Vegetables & Salads Special Bonus: +10 points
    has_salad = any("salad" in item["name"].lower() or "vegetable" in item["name"].lower() for item in food_items)
    if has_salad:
        score += 10.0

    # 4. Sugar Penalty: up to -15 points
    # Sugar ratio in g per 100g
    sugar_ratio = (total_sugar / total_weight) * 100.0
    score -= min(15.0, sugar_ratio * 2.0)

    # 5. Sodium Penalty: up to -15 points
    # Sodium ratio in mg per 100g. Standard limit is 2300mg/day. A single meal shouldn't exceed 800mg.
    sodium_ratio = (total_sodium / total_weight) * 100.0 # mg per 100g
    score -= min(15.0, (sodium_ratio / 100.0) * 3.0)

    # 6. Saturated Fat Penalty: up to -15 points
    # Est. saturated fat is ~30% of total fat. Fat ratio in g per 100g
    fat_ratio = (total_fat / total_weight) * 100.0
    score -= min(15.0, fat_ratio * 0.8)

    # 7. Processing Level Adjustment
    # Processed categories (heavy cream, butter curry, deep fry) vs unprocessed (boiled, raw, steamed)
    for item in food_items:
        name = item["name"].lower()
        if any(x in name for x in ["butter", "biryani", "fried", "paneer"]):
            score -= 3.0  # Processed / rich
        if any(x in name for x in ["salad", "boiled egg", "idli", "roti"]):
            score += 2.0  # Clean / whole foods

    # Bound score between 1 and 100
    final_score = int(round(score))
    return max(1, min(100, final_score))
