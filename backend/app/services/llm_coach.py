import os
import requests
import json
from google import genai
from typing import List, Dict, Any, Optional
from app.config import settings

def query_openrouter(messages: List[Dict[str, str]]) -> Optional[str]:
    """
    Queries OpenRouter with a cascade of top-ranked models suited for instruction/chat.
    """
    api_key = settings.OPENROUTER_API_KEY
    if not api_key:
        print("[OpenRouter] API Key is not configured.")
        return None

    # Top models on OpenRouter suited for this task (instruction, chat, reasoning)
    models = [
        "deepseek/deepseek-chat",
        "meta-llama/llama-3.3-70b-instruct",
        "qwen/qwen-2.5-72b-instruct",
        "google/gemini-2.0-flash-exp",
        "anthropic/claude-3.5-sonnet"
    ]

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/NutriVisionAI",
        "X-Title": "NutriVisionAI"
    }

    for model in models:
        try:
            # Inject active model name into the system prompt dynamically so the model can identify itself
            model_messages = []
            has_system = False
            for msg in messages:
                if msg["role"] == "system":
                    has_system = True
                    injected_content = msg["content"] + f"\n\n[SYSTEM INFO: Your active model engine is '{model}'. If the user asks which model is being used, what model is running, or who you are, you must answer that you are NutriVision AI Coach running on '{model}' via OpenRouter.]"
                    model_messages.append({"role": "system", "content": injected_content})
                else:
                    model_messages.append(msg)
            
            if not has_system:
                model_messages.insert(0, {
                    "role": "system",
                    "content": f"[SYSTEM INFO: Your active model engine is '{model}'. If the user asks which model is being used, what model is running, or who you are, you must answer that you are NutriVision AI Coach running on '{model}' via OpenRouter.]"
                })

            payload = {
                "model": model,
                "messages": model_messages,
                "temperature": 0.7,
                "max_tokens": 500
            }
            print(f"[OpenRouter] Trying model: {model}")
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                data=json.dumps(payload),
                timeout=12
            )
            if response.status_code == 200:
                res_data = response.json()
                reply = res_data["choices"][0]["message"]["content"]
                print(f"[OpenRouter] Successfully generated reply with model: {model}")
                return reply
            else:
                print(f"[OpenRouter] Model {model} failed (HTTP {response.status_code}): {response.text}")
        except Exception as e:
            print(f"[OpenRouter] Connection error with model {model}: {e}")

    return None

def generate_coach_recommendation(
    profile: Any,
    meal_foods: List[Dict[str, Any]]
) -> str:
    """
    Generates sport-specific, athlete-centric nutrition advice for the uploaded meal.
    Tries OpenRouter first (using top ranked models), falls back to Gemini API,
    and finally falls back to a highly customized rule-based nutrition coach system.
    """
    # 1. Gather facts
    meal_calories = sum(item["calories"] for item in meal_foods)
    meal_protein = sum(item["protein"] for item in meal_foods)
    meal_carbs = sum(item["carbs"] for item in meal_foods)
    meal_fat = sum(item["fat"] for item in meal_foods)
    
    food_names = [item["name"] for item in meal_foods]
    
    sport = profile.sport if profile else "General Fitness"
    phase = profile.training_phase if profile else "Rest Day"
    protein_target = profile.protein_target if profile else 80
    calorie_target = profile.calorie_target if profile else 2000
    carbs_target = profile.carbs_target if profile else 200
    fat_target = profile.fat_target if profile else 60

    prompt = f"""
You are NutriVision AI Coach, an elite sports-nutritionist specialized in Indian dietary patterns and foods.

Athlete Profile:
- Sport: {sport}
- Training Phase: {phase}
- Daily Targets: {calorie_target} kcal, {protein_target}g Protein, {carbs_target}g Carbs, {fat_target}g Fat

Current Meal details:
- Foods: {', '.join(food_names)}
- Meal Nutrition: {meal_calories:.0f} kcal, {meal_protein:.1f}g Protein, {meal_carbs:.1f}g Carbs, {meal_fat:.1f}g Fat

Please provide a concise, high-value, action-oriented evaluation (max 120 words) in bullet points:
1. Evaluation of this meal relative to the athlete's sport and training phase.
2. Recommendations to optimize (e.g., adding specific Indian protein sources like paneer, eggs, sattu, or carb sources like sweet potato).
3. A rating out of 10 for sport compatibility.
"""

    # Try OpenRouter first
    if settings.OPENROUTER_API_KEY:
        try:
            messages = [
                {"role": "system", "content": "You are NutriVision AI Coach, an elite sports-nutritionist specialized in Indian dietary patterns and foods."},
                {"role": "user", "content": prompt}
            ]
            response_text = query_openrouter(messages)
            if response_text:
                return response_text
        except Exception as e:
            print(f"[Coach Recommendation] OpenRouter fallback triggered due to: {e}")

    # Try Gemini second
    active_key = settings.GEMINI_API_KEY
    if active_key:
        try:
            client = genai.Client(api_key=active_key)
            response = None
            last_error = None
            for model_name in ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-2.5-flash", "gemini-3.5-flash"]:
                try:
                    response = client.models.generate_content(model=model_name, contents=prompt)
                    print(f"[Gemini Coach] Successfully generated recommendation with: {model_name}")
                    break
                except Exception as model_err:
                    last_error = model_err
                    print(f"[Gemini Coach] Model {model_name} failed: {model_err}")
            
            if response is not None:
                return response.text
        except Exception as e:
            print(f"[Gemini Coach] Error generating recommendation: {e}")
            pass

    # 3. RULE-BASED EXPERT COACH SYSTEM (FALLBACK / OFFLINE MODE)
    feedback_bullets = []
    compatibility_score = 7
    
    # Analyze protein content
    if meal_protein < 15:
        compatibility_score -= 2
        if sport in ["Bodybuilder", "Sprinting", "Strength/Power"]:
            feedback_bullets.append("• **Protein Deficient**: This meal contains only {:.1f}g protein. For a {}, this is insufficient to trigger muscle protein synthesis (MPS).".format(meal_protein, sport))
            feedback_bullets.append("• **Action Item**: Add 150g low-fat paneer (yields ~27g protein), 4 egg whites, or 1 scoop of whey protein isolate.")
        else:
            feedback_bullets.append("• **Low Protein**: Consider adding a cup of Yellow Dal Tadka or 150g curd to balance the macro ratio.")
    elif meal_protein >= 30:
        compatibility_score += 2
        feedback_bullets.append("• **Excellent Protein**: {:.1f}g protein is optimal for muscle recovery and cell repair. MPS threshold met!".format(meal_protein))
        
    # Analyze Carbohydrates relative to training phase
    if phase == "Competition Day" and sport in ["Sprinting", "Marathon"]:
        carb_ratio = (meal_carbs * 4) / (meal_calories + 1)
        if carb_ratio < 0.6:
            compatibility_score -= 1
            feedback_bullets.append("• **Carb Loading needed**: On a Competition Day, your muscles require glycogen saturation. Your carbohydrate ratio is low.")
            feedback_bullets.append("• **Action Item**: Add 1 extra medium Roti or a cup of Steamed Rice to fuel explosive sprinting / endurance runs.")
        else:
            feedback_bullets.append("• **Fueled for Performance**: Good carbohydrate ratio ({:.1f}g) to support glycogen levels today.".format(meal_carbs))
            
    elif phase == "Cut" or phase == "Rest Day":
        if meal_carbs > 80:
            compatibility_score -= 1
            feedback_bullets.append("• **Carb Heavy for Rest Day**: {:.1f}g carbs is high for an inactive/recovery day on a deficit.".format(meal_carbs))
            feedback_bullets.append("• **Action Item**: Swap rice/roti portions for high-fiber Mixed Vegetable Salad or green vegetables to maintain satiety.")

    # Saturated fat / processing penalty
    has_heavy_food = any(x in [f.lower() for f in food_names] for x in ["paneer butter masala", "chicken biryani"])
    if has_heavy_food:
        compatibility_score -= 1
        feedback_bullets.append("• **High Calorie Density**: Butter/ghee additions increase fats ({:.1f}g). Fit for bulking, but monitor overall daily fat ceilings.".format(meal_fat))
        
    # Sport-specific recommendations
    if sport == "Bodybuilder":
        if phase == "Bulk":
            feedback_bullets.append("• **Bulking Recommendation**: Ideal caloric density. Prioritize nutrient partitioning by keeping active workouts heavy.")
        else:
            feedback_bullets.append("• **Shredding Recommendation**: Watch hidden fats. Prioritize lean protein sources (egg whites, boiled chicken, double-toned milk curd).")
    elif sport == "Sprinting":
        feedback_bullets.append("• **Sprinter Fuel**: Ensure adequate hydration and sodium intake today, especially in hot conditions, to maintain muscle contractile force.")
    elif sport == "Marathon":
        feedback_bullets.append("• **Endurance Tip**: Aim for easily digestible carbs and minimize fiber 2 hours prior to long endurance runs to avoid gastrointestinal stress.")
    
    # Cap compatibility score
    compatibility_score = max(1, min(10, compatibility_score))
    feedback_bullets.append(f"\n• **Sport Compatibility Rating**: {compatibility_score}/10")
    
    return "\n".join(feedback_bullets)

def handle_chatbot_conversation(
    profile: Any,
    history: List[Dict[str, str]],
    user_message: str
) -> str:
    """
    Handles chatbot questions from the AI Nutrition Coach view.
    Tries OpenRouter first (using top ranked models), falls back to Gemini API,
    and finally falls back to a template helper response.
    """
    sport = profile.sport if profile else "General Fitness"
    phase = profile.training_phase if profile else "Rest Day"
    weight = profile.weight if profile else 70
    height = profile.height if profile else 175
    calorie_target = profile.calorie_target if profile else 2000

    # Try OpenRouter first
    if settings.OPENROUTER_API_KEY:
        try:
            messages = []
            messages.append({
                "role": "system",
                "content": f"You are NutriVision AI Coach, a premium personal sports-nutritionist for Indian athletes.\n\nAthlete context:\n- Sport: {sport}\n- Training Phase: {phase}\n- Current weight: {weight} kg, Height: {height} cm"
            })
            for msg in history[-5:]:
                role = "user" if msg["sender"] == "user" else "assistant"
                messages.append({"role": role, "content": msg["text"]})
            
            messages.append({"role": "user", "content": user_message})

            response_text = query_openrouter(messages)
            if response_text:
                return response_text
        except Exception as e:
            print(f"[Coach Chat] OpenRouter fallback triggered due to: {e}")

    # Try Gemini second
    active_key = settings.GEMINI_API_KEY
    if active_key:
        try:
            client = genai.Client(api_key=active_key)
            chat_context = ""
            for msg in history[-5:]:
                role = "User" if msg["sender"] == "user" else "Coach"
                chat_context += f"{role}: {msg['text']}\n"
                
            prompt = f"""
You are NutriVision AI Coach, a premium personal sports-nutritionist for Indian athletes.

Athlete context:
- Sport: {sport}
- Training Phase: {phase}
- Current weight: {weight} kg, Height: {height} cm

Chat History:
{chat_context}

User's new message: "{user_message}"

Please respond directly, offering specific, scientifically backed, and action-oriented nutrition advice.
Include Indian food options (sattu, chana, paneer, sprouts, chicken tikka, eggs, ragi, dal). Keep the tone encouraging, professional, and clear. Max 150 words.
"""
            response = None
            last_error = None
            for model_name in ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-2.5-flash", "gemini-3.5-flash"]:
                try:
                    response = client.models.generate_content(model=model_name, contents=prompt)
                    print(f"[Gemini Chat] Successfully generated chat with: {model_name}")
                    break
                except Exception as model_err:
                    last_error = model_err
                    print(f"[Gemini Chat] Model {model_name} failed: {model_err}")
            
            if response is not None:
                return response.text
        except Exception as e:
            print(f"[Gemini Chat] Chatbot API call failed: {e}")
            pass
            
    # Fallback chat advisor (Rule-based)
    msg_lower = user_message.lower()
    if "protein" in msg_lower:
        return f"For a {sport} ({phase}), I recommend targeting high-quality protein sources. Excellent Indian options include: egg whites (4g protein each), double-toned curd (15g per cup), sattu powder (20g per 100g), paneer (18g per 100g), and sprouts (7g per cup). Aim for 20-30g of protein in your post-workout window."
    elif "carb" in msg_lower or "fuel" in msg_lower or "energy" in msg_lower:
        return f"To optimize your energy as a {sport}, carbs are crucial. For slow-release energy, consume whole grains like oats, brown rice, or multi-grain rotis. If you need quick energy before training, try a banana, ragi malt, or sweet potato. During your {phase} phase, ensure your carbs align with your output!"
    elif "weight" in msg_lower or "lose" in msg_lower or "cut" in msg_lower:
        return f"To support weight management in your {phase} phase, focus on high-volume, low-calorie foods. Load up on green leaf salad, cucumber, and dal soup. Keep protein high to preserve muscle mass, and use a small calorie deficit (200-500 kcal below maintenance)."
    else:
        return f"That's a great question! As a {sport} in your {phase} phase, consistency is key. Ensure you are logging your meals, meeting your calorie target ({calorie_target} kcal), and keeping hydrated. What other specific questions do you have about your meal timing or macro split?"

