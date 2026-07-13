"""
NutriVision AI — AI Coach (LLM-powered Nutrition Recommendations)

Builds context-aware prompts and queries Gemma/Llama via Ollama or HuggingFace.
Falls back to rule-based recommendations when LLM is not available.
"""

import os
from typing import Optional
from loguru import logger
from nutrition_engine.calculator import get_nutrient_summary


# ─────────────────────────────────────────────────────────────────────────────
# Athlete Sport Profiles
# ─────────────────────────────────────────────────────────────────────────────

SPORT_PROFILES = {
    "sprinting": {
        "protein_g_per_kg": 1.8,
        "competition_carb_g_per_kg": 8.0,
        "recovery_carb_g_per_kg": 4.0,
        "focus": "explosive power, fast-twitch muscle fiber repair",
    },
    "marathon": {
        "protein_g_per_kg": 1.6,
        "competition_carb_g_per_kg": 10.0,
        "recovery_carb_g_per_kg": 6.0,
        "focus": "endurance, glycogen replenishment, oxidative muscle repair",
    },
    "weightlifting": {
        "protein_g_per_kg": 2.2,
        "competition_carb_g_per_kg": 6.0,
        "recovery_carb_g_per_kg": 4.5,
        "focus": "muscle hypertrophy, leucine timing, creatine phosphate replenishment",
    },
    "cricket": {
        "protein_g_per_kg": 1.7,
        "competition_carb_g_per_kg": 6.0,
        "recovery_carb_g_per_kg": 4.0,
        "focus": "intermittent bursts, hydration, sustained energy",
    },
    "football": {
        "protein_g_per_kg": 1.7,
        "competition_carb_g_per_kg": 7.0,
        "recovery_carb_g_per_kg": 5.0,
        "focus": "aerobic + anaerobic capacity, muscle recovery",
    },
    "yoga": {
        "protein_g_per_kg": 1.3,
        "competition_carb_g_per_kg": 4.0,
        "recovery_carb_g_per_kg": 3.0,
        "focus": "flexibility, anti-inflammatory nutrition, mindful eating",
    },
    "general fitness": {
        "protein_g_per_kg": 1.5,
        "competition_carb_g_per_kg": 5.0,
        "recovery_carb_g_per_kg": 3.5,
        "focus": "balanced macros, body composition, general health",
    },
}

TRAINING_PHASE_GUIDANCE = {
    "competition": "High carbohydrate loading (7-10g/kg). Moderate protein. Easily digestible foods. Avoid high-fiber and high-fat right before.",
    "recovery": "High protein (2-2.5g/kg). Anti-inflammatory foods (turmeric, ginger). Moderate carbs for glycogen replenishment. Stay hydrated.",
    "gym": "Calorie surplus (250-500 kcal above TDEE). High protein timing (leucine-rich sources within 30 min post-workout).",
    "rest": "Calorie maintenance or slight deficit. Balanced meals. Focus on micronutrients and hydration.",
    "base_training": "Balanced macros. Periodized carbohydrate intake based on training volume.",
}


class AICoach:
    """
    LLM-powered nutrition coach that generates personalized meal advice.

    Supports:
    - Ollama (local Gemma/Llama)
    - HuggingFace API
    - Rule-based fallback (always available)
    """

    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "fallback")
        self.model = os.getenv("LLM_MODEL", "gemma2:9b")
        self.ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.hf_token = os.getenv("HF_API_TOKEN", "")
        self.client = None
        self._init_client()

    def _init_client(self):
        """Initialize LLM client."""
        if self.provider == "ollama":
            try:
                import ollama
                self.client = ollama.Client(host=self.ollama_url)
                logger.success(f"✅ Ollama client connected ({self.model})")
            except Exception as e:
                logger.warning(f"⚠️  Ollama not available: {e}. Using rule-based fallback.")
                self.provider = "fallback"
        elif self.provider == "huggingface":
            try:
                from huggingface_hub import InferenceClient
                self.client = InferenceClient(token=self.hf_token)
                logger.success("✅ HuggingFace Inference client ready")
            except Exception as e:
                logger.warning(f"⚠️  HuggingFace client failed: {e}. Using fallback.")
                self.provider = "fallback"
        else:
            logger.info("📝 AI Coach running in rule-based fallback mode.")

    def build_prompt(
        self,
        meal_nutrition: dict,
        food_items: list[str],
        user_profile: Optional[dict] = None,
        health_score: Optional[dict] = None,
    ) -> str:
        """Build a detailed system + user prompt for the LLM."""
        summary = get_nutrient_summary(meal_nutrition)
        foods_str = ", ".join(food_items)

        profile_str = ""
        if user_profile:
            profile_str = f"""
User Profile:
- Weight: {user_profile.get('weight_kg', 70)} kg
- Height: {user_profile.get('height_cm', 170)} cm
- Sport: {user_profile.get('sport', 'general fitness')}
- Goal: {user_profile.get('goal', 'maintain health')}
- Training Phase: {user_profile.get('training_phase', 'base_training')}
- Age: {user_profile.get('age', 25)}
"""

        score_str = ""
        if health_score:
            score_str = f"""
Meal Health Score: {health_score.get('overall_score', 'N/A')}/100 ({health_score.get('grade', '')})
Issues: {'; '.join(health_score.get('feedback', ['None']))}
"""

        prompt = f"""You are NutriVision AI Coach, an expert sports nutritionist specializing in Indian cuisine and athlete nutrition. You provide specific, actionable, science-backed advice.

{profile_str}

Today's Meal: {foods_str}
{summary}
{score_str}

Provide personalized nutrition coaching in this format:
1. **Meal Assessment** (2-3 sentences): What's good and what's lacking
2. **Specific Improvements** (3-5 bullet points): Exact Indian food swaps or additions
3. **Athlete-Specific Tip** (if profile provided): Sport/phase specific advice
4. **Quick Indian Food Fix**: One specific Indian food item with quantity that would most improve this meal

Keep advice practical, specific to Indian foods, and quantified (e.g., "add 150g paneer" not just "add protein").
"""
        return prompt

    async def get_recommendation(
        self,
        meal_nutrition: dict,
        food_items: list[str],
        user_profile: Optional[dict] = None,
        health_score: Optional[dict] = None,
    ) -> dict:
        """
        Get AI-powered meal recommendation.

        Returns:
            Dict with recommendation text and metadata
        """
        prompt = self.build_prompt(meal_nutrition, food_items, user_profile, health_score)

        if self.provider == "ollama":
            return await self._ollama_recommend(prompt)
        elif self.provider == "huggingface":
            return await self._hf_recommend(prompt)
        else:
            return self._rule_based_recommend(meal_nutrition, food_items, user_profile, health_score)

    async def _ollama_recommend(self, prompt: str) -> dict:
        """Query local Ollama instance."""
        try:
            response = self.client.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            return {
                "recommendation": response["message"]["content"],
                "provider": "ollama",
                "model": self.model,
            }
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            return {"recommendation": "Unable to get AI recommendation. Please check Ollama.", "provider": "error"}

    async def _hf_recommend(self, prompt: str) -> dict:
        """Query HuggingFace Inference API."""
        try:
            response = self.client.text_generation(
                prompt,
                model="google/gemma-7b-it",
                max_new_tokens=512,
                temperature=0.7,
            )
            return {
                "recommendation": response,
                "provider": "huggingface",
                "model": "gemma-7b-it",
            }
        except Exception as e:
            logger.error(f"HuggingFace error: {e}")
            return self._rule_based_recommend({}, [], None, None)

    def _rule_based_recommend(
        self,
        meal_nutrition: dict,
        food_items: list[str],
        user_profile: Optional[dict],
        health_score: Optional[dict],
    ) -> dict:
        """
        Rule-based recommendation engine (always available as fallback).
        Generates specific, helpful advice without an LLM.
        """
        totals = meal_nutrition.get("totals", {})
        protein_g = totals.get("protein", 0)
        fiber_g = totals.get("fiber", 0)
        sodium_mg = totals.get("sodium", 0)
        sugar_g = totals.get("sugar", 0)
        calories = totals.get("calories", 0)

        issues = []
        positives = []
        fixes = []

        # Protein assessment
        if protein_g < 15:
            issues.append(f"Low protein ({protein_g:.1f}g). Indian athletes need 1.6-2.2g/kg body weight.")
            fixes.append("🥚 Add 3 boiled eggs OR 150g paneer OR 200g dal to boost protein by 20-25g.")
        elif protein_g >= 25:
            positives.append(f"✅ Excellent protein intake ({protein_g:.1f}g)")

        # Fiber assessment
        if fiber_g < 5:
            issues.append(f"Low fiber ({fiber_g:.1f}g). Aim for 25-30g/day.")
            fixes.append("🥗 Add a kachumber salad (cucumber + tomato + onion) for 3-4g fiber at zero guilt.")

        # Sodium assessment
        if sodium_mg > 800:
            issues.append(f"High sodium ({sodium_mg:.0f}mg). Reduce pickle, papad, or canned foods.")
            fixes.append("🧂 Skip the pickle and papad to reduce sodium by 300-500mg instantly.")

        # Sugar assessment
        if sugar_g > 20:
            issues.append(f"High sugar ({sugar_g:.1f}g). Limit to 50g/day total.")
            fixes.append("🍬 Replace sweet lassi with plain curd to save 15-20g sugar.")

        # Calorie assessment
        if calories < 300:
            issues.append(f"Very low calorie meal ({calories:.0f} kcal). Risk of underfueling.")
            fixes.append("🍚 Add an extra roti or 100g rice to meet energy needs.")
        elif calories > 900:
            issues.append(f"High calorie meal ({calories:.0f} kcal). Consider smaller portions.")

        # Sport-specific advice
        sport_tip = ""
        if user_profile:
            sport = user_profile.get("sport", "general fitness").lower()
            phase = user_profile.get("training_phase", "base_training").lower()
            weight_kg = user_profile.get("weight_kg", 70)

            profile = SPORT_PROFILES.get(sport, SPORT_PROFILES["general fitness"])
            phase_guidance = TRAINING_PHASE_GUIDANCE.get(phase, "")

            protein_needed = profile["protein_g_per_kg"] * weight_kg
            sport_tip = (
                f"\n🏃 **{sport.title()} Athlete Tip ({phase.title()} Phase)**: "
                f"You need ~{protein_needed:.0f}g protein/day. "
                f"{phase_guidance}"
            )

        # Build recommendation text
        assessment_parts = []
        if positives:
            assessment_parts.append(" | ".join(positives))
        if issues:
            assessment_parts.append("Issues: " + " | ".join(issues))

        recommendation = f"""## Meal Assessment
{assessment_parts[0] if assessment_parts else "Balanced meal detected."}

## Specific Improvements
{chr(10).join(fixes) if fixes else "✅ This meal looks well-balanced! Maintain this quality."}

{sport_tip}

## Quick Fix
{fixes[0] if fixes else "Keep up the great nutrition habits! 🎉"}
"""

        return {
            "recommendation": recommendation.strip(),
            "provider": "rule-based",
            "model": "NutriVision Rules Engine v1.0",
        }

    def get_athlete_plan(self, user_profile: dict) -> dict:
        """Generate a sport-specific daily nutrition plan."""
        sport = user_profile.get("sport", "general fitness").lower()
        phase = user_profile.get("training_phase", "base_training").lower()
        weight_kg = user_profile.get("weight_kg", 70)
        goal = user_profile.get("goal", "maintain")

        profile = SPORT_PROFILES.get(sport, SPORT_PROFILES["general fitness"])
        phase_carb_key = f"{phase.replace(' ', '_')}_carb_g_per_kg"
        carb_g_per_kg = profile.get(phase_carb_key, profile.get("recovery_carb_g_per_kg", 4.0))
        protein_g_per_kg = profile["protein_g_per_kg"]

        daily_protein = round(protein_g_per_kg * weight_kg)
        daily_carbs = round(carb_g_per_kg * weight_kg)
        daily_fat_pct = 0.25
        daily_calories = daily_protein * 4 + daily_carbs * 4
        daily_fat = round((daily_calories * daily_fat_pct) / 9)
        daily_calories += daily_fat * 9

        if goal == "muscle_gain":
            daily_calories += 300
        elif goal == "fat_loss":
            daily_calories -= 300

        return {
            "sport": sport,
            "training_phase": phase,
            "daily_targets": {
                "calories": daily_calories,
                "protein_g": daily_protein,
                "carbs_g": daily_carbs,
                "fat_g": daily_fat,
            },
            "focus": profile["focus"],
            "phase_guidance": TRAINING_PHASE_GUIDANCE.get(phase, ""),
            "meal_timing": {
                "pre_workout": "1-2 hours before: High carb, moderate protein, low fat/fiber",
                "post_workout": "Within 30 min: 20-25g protein + fast carbs (banana + curd)",
                "before_bed": "Slow protein (paneer/curd) to prevent muscle breakdown overnight",
            },
        }
