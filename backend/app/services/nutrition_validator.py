"""
Phase 1: Nutrition Macro Sanity Validator
Validates that detected nutrition values are physically plausible
using hard biochemical constraints and soft plausibility rules.

Two-layer validation:
  Layer 1 — Rule Engine: fast deterministic checks (no API call)
  Layer 2 — LLM Validation: OpenRouter for flagged edge cases
"""

from __future__ import annotations

import json
import requests
from dataclasses import dataclass, field
from typing import Optional
from app.config import settings

# ─── Physical constants ───────────────────────────────────────────────────────
KCAL_PER_G_PROTEIN  = 4.0
KCAL_PER_G_CARBS    = 4.0
KCAL_PER_G_FAT      = 9.0
MAX_KCAL_PER_G_FOOD = 9.0      # Maximum possible: pure fat  (9 kcal/g)
MIN_KCAL_PER_G_FOOD = 0.0      # Minimum possible: plain water

# Plausibility bands: [min_g_per_serving, max_g_per_serving]
PORTION_BANDS: dict[str, tuple[float, float]] = {
    "Cereal":     (30,  500),
    "Pulses":     (50,  500),
    "Dairy":      (20,  400),
    "Vegetables": (15,  400),
    "Meat":       (30,  500),
    "Sweets":     (10,  250),
    "Snack":      (5,   200),
}

DEFAULT_PORTION_BAND = (10, 600)

MACRO_TOLERANCE = 0.20   # Allow 20% discrepancy between declared and computed kcal
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class ValidationResult:
    is_valid: bool
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    corrected_items: list[dict] = field(default_factory=list)   # Items after corrections

    def to_dict(self) -> dict:
        return {
            "is_valid": self.is_valid,
            "issues": self.issues,
            "warnings": self.warnings,
            "corrections_applied": len(self.corrected_items) > 0
        }


# ─── Rule Engine ─────────────────────────────────────────────────────────────

def _validate_energy_consistency(item: dict) -> list[str]:
    """
    Check that declared calories are consistent with macro grams.
    Expected kcal = protein*4 + carbs*4 + fat*9
    Allow ±20% tolerance.
    """
    issues = []
    weight    = item.get("weight_g", 0)
    calories  = item.get("calories", 0)
    protein   = item.get("protein", 0)
    carbs     = item.get("carbs", 0)
    fat       = item.get("fat", 0)

    computed_kcal = (protein * KCAL_PER_G_PROTEIN +
                     carbs   * KCAL_PER_G_CARBS   +
                     fat     * KCAL_PER_G_FAT)

    if calories > 0 and computed_kcal > 0:
        ratio = abs(calories - computed_kcal) / max(computed_kcal, calories)
        if ratio > MACRO_TOLERANCE:
            issues.append(
                f"[{item['name']}] Energy inconsistency: "
                f"declared={calories:.0f} kcal, computed from macros={computed_kcal:.0f} kcal "
                f"({ratio*100:.0f}% deviation)"
            )

    return issues


def _validate_calorie_density(item: dict) -> list[str]:
    """
    Check that kcal/g ratio is physically possible.
    Pure fat = 9 kcal/g (maximum). Water = 0.
    """
    issues = []
    weight   = item.get("weight_g", 1)
    calories = item.get("calories", 0)

    if weight <= 0:
        issues.append(f"[{item['name']}] Weight is zero or negative.")
        return issues

    kcal_per_g = calories / weight
    if kcal_per_g > MAX_KCAL_PER_G_FOOD:
        issues.append(
            f"[{item['name']}] Impossible calorie density: {kcal_per_g:.2f} kcal/g "
            f"(max physically possible = {MAX_KCAL_PER_G_FOOD}). "
            f"Likely weight underestimate."
        )
    elif kcal_per_g < 0:
        issues.append(f"[{item['name']}] Negative calorie density — impossible.")

    return issues


def _validate_portion_size(item: dict, category: str) -> list[str]:
    """
    Check that the portion weight is within a plausible serving range
    for the food category.
    """
    issues = []
    weight = item.get("weight_g", 0)
    min_g, max_g = PORTION_BANDS.get(category, DEFAULT_PORTION_BAND)

    if weight < min_g:
        issues.append(
            f"[{item['name']}] Weight {weight:.0f}g is suspiciously low "
            f"(typical minimum for {category}: {min_g}g)"
        )
    elif weight > max_g:
        issues.append(
            f"[{item['name']}] Weight {weight:.0f}g is suspiciously high "
            f"(typical maximum for {category}: {max_g}g)"
        )

    return issues


def _validate_macro_realism(item: dict) -> list[str]:
    """
    Food-category-specific macro plausibility checks.
    E.g., rice should not have 50g of protein per 100g.
    """
    issues = []
    name     = item.get("name", "").lower()
    weight   = item.get("weight_g", 1)
    protein  = item.get("protein", 0)
    fat      = item.get("fat", 0)
    carbs    = item.get("carbs", 0)
    calories = item.get("calories", 0)

    if weight <= 0:
        return issues

    protein_per_100g = (protein / weight) * 100
    fat_per_100g     = (fat     / weight) * 100
    carbs_per_100g   = (carbs   / weight) * 100

    # Rice / Cereal should not be high in protein
    if any(k in name for k in ["rice", "roti", "naan", "chapati", "idli", "dosa"]):
        if protein_per_100g > 15:
            issues.append(
                f"[{item['name']}] Unusually high protein ({protein_per_100g:.1f}g/100g) "
                f"for a cereal item. Expected < 10g/100g."
            )

    # Dal should have meaningful protein
    if any(k in name for k in ["dal", "lentil", "rajma", "chole", "chana"]):
        if protein_per_100g < 2:
            issues.append(
                f"[{item['name']}] Unusually low protein ({protein_per_100g:.1f}g/100g) "
                f"for a pulse item. Expected ≥ 4g/100g."
            )

    # Salad / vegetables should not be calorie-dense
    if any(k in name for k in ["salad", "chutney", "vegetable", "raita"]):
        kcal_per_100g = (calories / weight) * 100
        if kcal_per_100g > 250:
            issues.append(
                f"[{item['name']}] High calorie density ({kcal_per_100g:.0f} kcal/100g) "
                f"unexpected for a vegetable/condiment."
            )

    return issues


def run_rule_engine(food_items: list[dict], food_db: dict) -> ValidationResult:
    """
    Layer 1: Deterministic rule-based nutrition validation.

    Args:
        food_items: List of food item dicts from the CV pipeline.
        food_db:    The FOOD_DENSITY_NUTRITION reference dict.

    Returns:
        ValidationResult with all issues and warnings found.
    """
    all_issues: list[str] = []
    all_warnings: list[str] = []

    for item in food_items:
        name     = item.get("name", "Unknown")
        category = food_db.get(name, {}).get("category", "Unknown")

        issues_energy  = _validate_energy_consistency(item)
        issues_density = _validate_calorie_density(item)
        issues_portion = _validate_portion_size(item, category)
        issues_macro   = _validate_macro_realism(item)

        all_issues.extend(issues_energy)
        all_issues.extend(issues_density)
        all_warnings.extend(issues_portion)
        all_warnings.extend(issues_macro)

    is_valid = len(all_issues) == 0
    result = ValidationResult(
        is_valid=is_valid,
        issues=all_issues,
        warnings=all_warnings,
        corrected_items=food_items   # Unchanged at rule-engine stage
    )

    if all_issues:
        print(f"[NutritionValidator] Rule engine found {len(all_issues)} critical issue(s):")
        for issue in all_issues:
            print(f"  ✗ {issue}")
    if all_warnings:
        print(f"[NutritionValidator] {len(all_warnings)} plausibility warning(s):")
        for w in all_warnings:
            print(f"  ⚠ {w}")

    return result


# ─── LLM Validation (Layer 2) ────────────────────────────────────────────────

LLM_VALIDATION_PROMPT = """You are a clinical nutritionist AI.
Evaluate whether the following nutrition values for a single food item are biologically plausible.

Food Item:
{food_json}

Check:
1. Are the calories consistent with the macro breakdown? (protein*4 + carbs*4 + fat*9 ≈ total calories)
2. Is the portion weight realistic for a single serving?
3. Are the per-100g macros reasonable for this type of food?

Respond with ONLY a JSON object in this format:
{{"valid": true|false, "reason": "brief one-line explanation"}}"""


def _call_openrouter_validation(food_item: dict) -> Optional[dict]:
    """
    Sends a single food item to OpenRouter for LLM-based plausibility check.
    Returns parsed JSON or None on failure.
    """
    if not settings.OPENROUTER_API_KEY:
        return None

    prompt = LLM_VALIDATION_PROMPT.format(
        food_json=json.dumps(food_item, indent=2)
    )

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/NutriVisionAI",
                "X-Title": "NutriVisionAI"
            },
            json={
                "model": "google/gemini-2.0-flash-exp",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 80,
                "temperature": 0.1
            },
            timeout=10
        )
        if response.status_code == 200:
            text = response.json()["choices"][0]["message"]["content"].strip()
            # Strip markdown fences if present
            if text.startswith("```"):
                text = text.split("\n", 1)[-1]
            if text.endswith("```"):
                text = text[:-3]
            return json.loads(text.strip())
    except Exception as e:
        print(f"[NutritionValidator] LLM validation failed: {e}")
    return None


def validate_with_llm(flagged_items: list[dict]) -> list[str]:
    """
    Layer 2: LLM validation for items flagged by the rule engine.
    Only called when rule engine finds issues.

    Args:
        flagged_items: Food items that failed rule-engine checks.

    Returns:
        List of additional LLM-identified issues.
    """
    llm_issues = []
    for item in flagged_items[:3]:    # Limit to 3 LLM calls max per request
        result = _call_openrouter_validation(item)
        if result and not result.get("valid", True):
            llm_issues.append(
                f"[LLM] {item.get('name', 'Unknown')}: {result.get('reason', 'Flagged as implausible')}"
            )
            print(f"[NutritionValidator] LLM flagged: {item.get('name')} — {result.get('reason')}")

    return llm_issues


def validate_nutrition(food_items: list[dict], food_db: dict,
                       use_llm: bool = True) -> ValidationResult:
    """
    Full two-layer nutrition validation pipeline.

    Args:
        food_items: Detected food items list from cv_pipeline.
        food_db:    FOOD_DENSITY_NUTRITION reference dict.
        use_llm:    Whether to call LLM for flagged items (default True).

    Returns:
        ValidationResult with all findings.
    """
    # Layer 1: Rule engine
    result = run_rule_engine(food_items, food_db)

    # Layer 2: LLM validation for critical failures (optional, API cost)
    if use_llm and not result.is_valid and settings.OPENROUTER_API_KEY:
        print(f"[NutritionValidator] Escalating {len(food_items)} item(s) to LLM validation...")
        llm_issues = validate_with_llm(food_items)
        result.issues.extend(llm_issues)

    print(f"[NutritionValidator] Final: valid={result.is_valid} | "
          f"issues={len(result.issues)} | warnings={len(result.warnings)}")

    return result
