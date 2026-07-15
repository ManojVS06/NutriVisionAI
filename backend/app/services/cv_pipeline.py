import os
import cv2
import numpy as np
import json
import math
import base64
from PIL import Image
from app.config import settings

# ── Phase 1: Import production-grade pipeline services ──────────────────────
from app.services.quality_checker import assess_image_quality
from app.services.semantic_matcher import match_food_semantic
from app.services.nutrition_validator import validate_nutrition

# ============================================================================
# EXPANDED IFCT FOOD DENSITY & NUTRITION DATABASE (per 100g)
# ============================================================================
FOOD_DENSITY_NUTRITION = {
    # Cereals & Breads
    "Cooked White Rice": {"density": 0.82, "calories_100g": 130, "protein_100g": 2.7, "carbs_100g": 28.0, "fat_100g": 0.3, "fiber_100g": 0.4, "sodium_100g": 1.0, "sugar_100g": 0.1, "category": "Cereal"},
    "Jeera Rice": {"density": 0.82, "calories_100g": 142, "protein_100g": 2.8, "carbs_100g": 26.0, "fat_100g": 3.2, "fiber_100g": 0.5, "sodium_100g": 120.0, "sugar_100g": 0.2, "category": "Cereal"},
    "Roti / Chapati": {"density": 0.60, "calories_100g": 264, "protein_100g": 8.0, "carbs_100g": 48.0, "fat_100g": 3.0, "fiber_100g": 7.0, "sodium_100g": 5.0, "sugar_100g": 0.4, "category": "Cereal"},
    "Naan": {"density": 0.55, "calories_100g": 310, "protein_100g": 9.0, "carbs_100g": 54.0, "fat_100g": 6.5, "fiber_100g": 2.0, "sodium_100g": 400.0, "sugar_100g": 3.0, "category": "Cereal"},
    "Paratha": {"density": 0.58, "calories_100g": 326, "protein_100g": 7.0, "carbs_100g": 44.0, "fat_100g": 14.0, "fiber_100g": 3.0, "sodium_100g": 290.0, "sugar_100g": 1.0, "category": "Cereal"},
    "Puri": {"density": 0.40, "calories_100g": 350, "protein_100g": 6.5, "carbs_100g": 42.0, "fat_100g": 18.0, "fiber_100g": 2.5, "sodium_100g": 310.0, "sugar_100g": 1.2, "category": "Cereal"},
    "Idli": {"density": 0.65, "calories_100g": 120, "protein_100g": 6.0, "carbs_100g": 28.0, "fat_100g": 0.5, "fiber_100g": 1.5, "sodium_100g": 180.0, "sugar_100g": 0.2, "category": "Cereal"},
    "Dosa": {"density": 0.50, "calories_100g": 168, "protein_100g": 4.0, "carbs_100g": 28.0, "fat_100g": 4.5, "fiber_100g": 1.0, "sodium_100g": 200.0, "sugar_100g": 0.5, "category": "Cereal"},
    "Masala Dosa": {"density": 0.55, "calories_100g": 190, "protein_100g": 4.5, "carbs_100g": 30.0, "fat_100g": 6.0, "fiber_100g": 1.5, "sodium_100g": 220.0, "sugar_100g": 0.6, "category": "Cereal"},
    "Upma": {"density": 0.75, "calories_100g": 135, "protein_100g": 3.5, "carbs_100g": 18.0, "fat_100g": 5.5, "fiber_100g": 1.8, "sodium_100g": 250.0, "sugar_100g": 0.4, "category": "Cereal"},
    "Poha": {"density": 0.60, "calories_100g": 130, "protein_100g": 2.8, "carbs_100g": 22.0, "fat_100g": 3.8, "fiber_100g": 1.5, "sodium_100g": 210.0, "sugar_100g": 0.5, "category": "Cereal"},

    # Pulses & Dals
    "Yellow Dal Tadka": {"density": 1.00, "calories_100g": 86, "protein_100g": 5.0, "carbs_100g": 12.0, "fat_100g": 2.2, "fiber_100g": 3.0, "sodium_100g": 280.0, "sugar_100g": 0.5, "category": "Pulses"},
    "Dal Makhani": {"density": 1.05, "calories_100g": 120, "protein_100g": 5.5, "carbs_100g": 12.0, "fat_100g": 5.5, "fiber_100g": 3.5, "sodium_100g": 320.0, "sugar_100g": 1.0, "category": "Pulses"},
    "Rajma": {"density": 1.00, "calories_100g": 110, "protein_100g": 6.5, "carbs_100g": 16.0, "fat_100g": 2.0, "fiber_100g": 5.0, "sodium_100g": 310.0, "sugar_100g": 0.8, "category": "Pulses"},
    "Chole / Chana Masala": {"density": 1.00, "calories_100g": 125, "protein_100g": 7.0, "carbs_100g": 18.0, "fat_100g": 3.0, "fiber_100g": 5.0, "sodium_100g": 340.0, "sugar_100g": 1.5, "category": "Pulses"},
    "Sambar": {"density": 1.00, "calories_100g": 55, "protein_100g": 2.5, "carbs_100g": 8.5, "fat_100g": 1.2, "fiber_100g": 2.0, "sodium_100g": 320.0, "sugar_100g": 1.1, "category": "Pulses"},

    # Dairy & Paneer
    "Paneer Butter Masala": {"density": 1.05, "calories_100g": 229, "protein_100g": 9.2, "carbs_100g": 6.8, "fat_100g": 18.5, "fiber_100g": 0.8, "sodium_100g": 340.0, "sugar_100g": 3.2, "category": "Dairy"},
    "Shahi Paneer": {"density": 1.05, "calories_100g": 245, "protein_100g": 10.0, "carbs_100g": 8.0, "fat_100g": 19.0, "fiber_100g": 0.5, "sodium_100g": 350.0, "sugar_100g": 3.5, "category": "Dairy"},
    "Palak Paneer": {"density": 1.02, "calories_100g": 175, "protein_100g": 9.5, "carbs_100g": 6.0, "fat_100g": 13.0, "fiber_100g": 2.5, "sodium_100g": 310.0, "sugar_100g": 1.5, "category": "Dairy"},
    "Curd / Raita": {"density": 1.03, "calories_100g": 60, "protein_100g": 3.5, "carbs_100g": 4.0, "fat_100g": 3.3, "fiber_100g": 0.0, "sodium_100g": 45.0, "sugar_100g": 4.0, "category": "Dairy"},
    "Lassi": {"density": 1.03, "calories_100g": 72, "protein_100g": 3.0, "carbs_100g": 10.0, "fat_100g": 2.5, "fiber_100g": 0.0, "sodium_100g": 50.0, "sugar_100g": 8.0, "category": "Dairy"},

    # Vegetables
    "Mixed Vegetable Salad": {"density": 0.30, "calories_100g": 25, "protein_100g": 1.2, "carbs_100g": 4.5, "fat_100g": 0.2, "fiber_100g": 2.5, "sodium_100g": 10.0, "sugar_100g": 2.0, "category": "Vegetables"},
    "Aloo Gobi": {"density": 0.85, "calories_100g": 100, "protein_100g": 2.5, "carbs_100g": 12.0, "fat_100g": 5.0, "fiber_100g": 2.5, "sodium_100g": 260.0, "sugar_100g": 1.0, "category": "Vegetables"},
    "Bhindi / Okra Fry": {"density": 0.70, "calories_100g": 90, "protein_100g": 2.0, "carbs_100g": 8.0, "fat_100g": 6.0, "fiber_100g": 3.0, "sodium_100g": 190.0, "sugar_100g": 0.5, "category": "Vegetables"},
    "Baingan Bharta": {"density": 0.85, "calories_100g": 80, "protein_100g": 1.8, "carbs_100g": 7.0, "fat_100g": 5.0, "fiber_100g": 3.0, "sodium_100g": 240.0, "sugar_100g": 1.5, "category": "Vegetables"},
    "Green Chutney": {"density": 0.95, "calories_100g": 40, "protein_100g": 1.0, "carbs_100g": 5.0, "fat_100g": 1.5, "fiber_100g": 1.5, "sodium_100g": 350.0, "sugar_100g": 1.0, "category": "Vegetables"},
    "Pickle / Achar": {"density": 1.00, "calories_100g": 150, "protein_100g": 1.5, "carbs_100g": 8.0, "fat_100g": 12.0, "fiber_100g": 2.0, "sodium_100g": 1200.0, "sugar_100g": 3.0, "category": "Vegetables"},

    # Meat & Non-Veg
    "Chicken Biryani": {"density": 0.90, "calories_100g": 163, "protein_100g": 10.5, "carbs_100g": 22.0, "fat_100g": 5.6, "fiber_100g": 1.6, "sodium_100g": 310.0, "sugar_100g": 0.8, "category": "Meat"},
    "Chicken Curry": {"density": 1.00, "calories_100g": 150, "protein_100g": 14.0, "carbs_100g": 5.0, "fat_100g": 8.5, "fiber_100g": 1.0, "sodium_100g": 380.0, "sugar_100g": 1.0, "category": "Meat"},
    "Butter Chicken": {"density": 1.02, "calories_100g": 195, "protein_100g": 12.0, "carbs_100g": 7.0, "fat_100g": 14.0, "fiber_100g": 1.0, "sodium_100g": 420.0, "sugar_100g": 3.0, "category": "Meat"},
    "Mutton Curry": {"density": 1.02, "calories_100g": 180, "protein_100g": 15.0, "carbs_100g": 4.0, "fat_100g": 12.0, "fiber_100g": 0.5, "sodium_100g": 350.0, "sugar_100g": 0.8, "category": "Meat"},
    "Fish Curry": {"density": 1.00, "calories_100g": 120, "protein_100g": 15.0, "carbs_100g": 4.0, "fat_100g": 5.5, "fiber_100g": 0.5, "sodium_100g": 380.0, "sugar_100g": 0.5, "category": "Meat"},
    "Boiled Egg": {"density": 1.10, "calories_100g": 155, "protein_100g": 13.0, "carbs_100g": 1.1, "fat_100g": 11.0, "fiber_100g": 0.0, "sodium_100g": 124.0, "sugar_100g": 1.1, "category": "Meat"},
    "Egg Curry": {"density": 1.00, "calories_100g": 145, "protein_100g": 10.0, "carbs_100g": 5.0, "fat_100g": 10.0, "fiber_100g": 0.8, "sodium_100g": 330.0, "sugar_100g": 1.2, "category": "Meat"},

    # Sweets & Snacks
    "Gulab Jamun": {"density": 1.10, "calories_100g": 320, "protein_100g": 3.5, "carbs_100g": 50.0, "fat_100g": 12.0, "fiber_100g": 0.0, "sodium_100g": 80.0, "sugar_100g": 40.0, "category": "Sweets"},
    "Papad": {"density": 0.30, "calories_100g": 330, "protein_100g": 20.0, "carbs_100g": 45.0, "fat_100g": 7.0, "fiber_100g": 5.0, "sodium_100g": 1600.0, "sugar_100g": 0.5, "category": "Snack"},
}

# Pre-defined demo foods coordinate mappings for portfolio showcase
DEMO_MEALS = {
    "dosa": [
        {"name": "Masala Dosa", "bbox": [50, 120, 480, 360], "volume_cm3": 250.0, "density": 0.55, "weight_g": 137.5},
        {"name": "Sambar", "bbox": [180, 20, 280, 110], "volume_cm3": 150.0, "density": 1.00, "weight_g": 150.0},
        {"name": "Green Chutney", "bbox": [320, 30, 410, 115], "volume_cm3": 40.0, "density": 0.95, "weight_g": 38.0}
    ],
    "biryani": [
        {"name": "Chicken Biryani", "bbox": [60, 60, 420, 420], "volume_cm3": 380.0, "density": 0.90, "weight_g": 342.0},
        {"name": "Boiled Egg", "bbox": [120, 120, 200, 200], "volume_cm3": 55.0, "density": 1.10, "weight_g": 60.5}
    ],
    "thali": [
        {"name": "Yellow Dal Tadka", "bbox": [60, 50, 170, 150], "volume_cm3": 180.0, "density": 1.00, "weight_g": 180.0},
        {"name": "Paneer Butter Masala", "bbox": [190, 50, 300, 150], "volume_cm3": 150.0, "density": 1.05, "weight_g": 157.5},
        {"name": "Roti / Chapati", "bbox": [80, 180, 230, 320], "volume_cm3": 120.0, "density": 0.60, "weight_g": 72.0},
        {"name": "Cooked White Rice", "bbox": [240, 180, 390, 320], "volume_cm3": 200.0, "density": 0.82, "weight_g": 164.0},
        {"name": "Mixed Vegetable Salad", "bbox": [310, 90, 390, 170], "volume_cm3": 80.0, "density": 0.30, "weight_g": 24.0}
    ]
}


# ============================================================================
# GEMINI VISION FOOD IDENTIFIER
# ============================================================================
def classify_foods_with_gemini(file_path: str, api_key: str) -> list:
    """
    Sends the meal image to Gemini Vision API to identify all food items,
    their approximate bounding box percentages, and estimated portion weights.
    Returns a list of dicts or None on failure.
    """
    try:
        from google import genai

        client = genai.Client(api_key=api_key)

        # Read image as base64
        with open(file_path, "rb") as f:
            image_bytes = f.read()

        # Determine mime type from extension
        ext = os.path.splitext(file_path)[1].lower()
        mime_type = "image/jpeg"
        if ext == ".png":
            mime_type = "image/png"

        prompt = """Analyze this food plate image. Identify EVERY distinct food item visible.

For each food item, return a JSON array with objects containing:
- "name": The specific Indian food name (e.g. "Roti / Chapati", "Yellow Dal Tadka", "Paneer Butter Masala", "Cooked White Rice", "Chicken Curry", "Sambar", "Curd / Raita", "Mixed Vegetable Salad", "Naan", "Papad", "Green Chutney", "Pickle / Achar", "Aloo Gobi", "Palak Paneer", "Chicken Biryani", "Boiled Egg", "Dosa", "Idli", etc.)
- "bbox_pct": [xmin%, ymin%, xmax%, ymax%] as percentages of image dimensions (0-100)
- "weight_g": Estimated portion weight in grams

IMPORTANT: 
- Identify ALL separate food items, including small sides like chutneys, pickles, salads, papad.
- Be specific: don't say "curry" generically, identify it as "Paneer Butter Masala" or "Chicken Curry" or "Dal Makhani" etc.
- Return ONLY valid JSON array, no markdown fences, no explanation.

Example response:
[{"name": "Roti / Chapati", "bbox_pct": [5, 30, 45, 85], "weight_g": 80}, {"name": "Yellow Dal Tadka", "bbox_pct": [50, 5, 80, 40], "weight_g": 150}]"""

        response = None
        last_error = None
        # Order of preference: 2.0-flash -> 1.5-flash -> 2.5-pro -> 3.5-flash
        for model_name in ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-2.5-pro", "gemini-3.5-flash"]:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=[
                        genai.types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                        prompt
                    ]
                )
                print(f"[Gemini Vision] Successfully executed model: {model_name}")
                break
            except Exception as e:
                last_error = e
                print(f"[Gemini Vision] Model {model_name} failed: {e}")
                
        if response is None:
            raise last_error

        text = response.text.strip()

        # Clean any markdown formatting
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        if text.startswith("json"):
            text = text[4:].strip()

        items = json.loads(text)
        if isinstance(items, list) and len(items) > 0:
            print(f"[Gemini Vision] Successfully identified {len(items)} food items")
            return items
    except Exception as e:
        print(f"[Gemini Vision] Classification failed: {e}")

    return None


def classify_foods_with_openrouter(file_path: str, api_key: str) -> list:
    """
    Sends the meal image to OpenRouter Vision API using a cascade of top-ranked vision models
    to identify all food items, their approximate bounding box percentages, and portion weights.
    """
    try:
        import base64
        import requests
        import json

        # Read image and convert to base64
        with open(file_path, "rb") as f:
            image_bytes = f.read()
        
        ext = os.path.splitext(file_path)[1].lower()
        mime_type = "image/jpeg"
        if ext == ".png":
            mime_type = "image/png"
            
        base64_image = base64.b64encode(image_bytes).decode("utf-8")
        
        prompt = """Analyze this food plate image. Identify EVERY distinct food item visible.

For each food item, return a JSON array with objects containing:
- "name": The specific Indian food name (e.g. "Roti / Chapati", "Yellow Dal Tadka", "Paneer Butter Masala", "Cooked White Rice", "Chicken Curry", "Sambar", "Curd / Raita", "Mixed Vegetable Salad", "Naan", "Papad", "Green Chutney", "Pickle / Achar", "Aloo Gobi", "Palak Paneer", "Chicken Biryani", "Boiled Egg", "Dosa", "Idli", etc.)
- "bbox_pct": [xmin%, ymin%, xmax%, ymax%] as percentages of image dimensions (0-100)
- "weight_g": Estimated portion weight in grams

IMPORTANT: 
- Identify ALL separate food items, including small sides like chutneys, pickles, salads, papad.
- Be specific: don't say "curry" generically, identify it as "Paneer Butter Masala" or "Chicken Curry" or "Dal Makhani" etc.
- Return ONLY valid JSON array, no markdown fences, no explanation.

Example response:
[{"name": "Roti / Chapati", "bbox_pct": [5, 30, 45, 85], "weight_g": 80}, {"name": "Yellow Dal Tadka", "bbox_pct": [50, 5, 80, 40], "weight_g": 150}]"""

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/NutriVisionAI",
            "X-Title": "NutriVisionAI"
        }
        
        # Vision-capable models on OpenRouter
        models = [
            "google/gemini-2.0-flash-exp",
            "anthropic/claude-3.5-sonnet",
            "meta-llama/llama-3.2-11b-vision-instruct"
        ]
        
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "temperature": 0.2
        }
        
        for model in models:
            try:
                print(f"[OpenRouter Vision] Trying model: {model}")
                payload["model"] = model
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    data=json.dumps(payload),
                    timeout=20
                )
                if response.status_code == 200:
                    res_data = response.json()
                    text = res_data["choices"][0]["message"]["content"].strip()
                    
                    # Clean any markdown formatting
                    if text.startswith("```"):
                        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
                    if text.endswith("```"):
                        text = text[:-3]
                    text = text.strip()
                    if text.startswith("json"):
                        text = text[4:].strip()
                        
                    items = json.loads(text)
                    if isinstance(items, list) and len(items) > 0:
                        print(f"[OpenRouter Vision] Successfully identified {len(items)} items using {model}")
                        return items
                else:
                    print(f"[OpenRouter Vision] Model {model} failed (HTTP {response.status_code}): {response.text}")
            except Exception as e:
                print(f"[OpenRouter Vision] Error with model {model}: {e}")
                
    except Exception as e:
        print(f"[OpenRouter Vision] General failure: {e}")
        
    return None


def match_food_to_database(food_name: str) -> tuple:
    """
    [Phase 1 Upgrade] Semantically matches a VLM/detector food name to the
    IFCT database using TF-IDF + character n-gram cosine similarity.
    Falls back to keyword map → ultimate fallback if needed.
    Returns (matched_name, food_info_dict).
    """
    # Try semantic matching first
    matched_name, score = match_food_semantic(food_name)
    if matched_name in FOOD_DENSITY_NUTRITION:
        return matched_name, FOOD_DENSITY_NUTRITION[matched_name]

    # Hard direct match as secondary safety net
    name_lower = food_name.lower().strip()
    for db_name, info in FOOD_DENSITY_NUTRITION.items():
        if db_name.lower() == name_lower:
            return db_name, info

    # Ultimate fallback
    return "Paneer Butter Masala", FOOD_DENSITY_NUTRITION["Paneer Butter Masala"]


# ============================================================================
# IMPROVED OPENCV SEGMENTATION (FALLBACK WHEN NO GEMINI KEY)
# ============================================================================
def segment_food_regions_opencv(image):
    """
    Uses HSV color-space analysis, K-means clustering, and watershed-style
    separation to find distinct food regions on a plate. Returns a list of
    contours representing individual food items.
    """
    h, w = image.shape[:2]

    # 1. Detect the plate (circular region) to focus analysis
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (9, 9), 2)

    # Try Hough circle detection for the plate
    circles = cv2.HoughCircles(
        blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=min(h, w) // 2,
        param1=80, param2=40,
        minRadius=min(h, w) // 4, maxRadius=min(h, w) // 2
    )

    plate_mask = np.ones((h, w), dtype=np.uint8) * 255
    plate_center = (w // 2, h // 2)
    plate_radius = min(h, w) // 2

    if circles is not None:
        circles = np.uint16(np.around(circles))
        # Take the largest circle as the plate
        best = circles[0][0]
        plate_center = (int(best[0]), int(best[1]))
        plate_radius = int(best[2])
        plate_mask = np.zeros((h, w), dtype=np.uint8)
        cv2.circle(plate_mask, plate_center, plate_radius, 255, -1)

    # 2. Convert to HSV and apply K-means clustering for region separation
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Mask the plate area
    plate_pixels_hsv = cv2.bitwise_and(hsv, hsv, mask=plate_mask)
    plate_pixels_bgr = cv2.bitwise_and(image, image, mask=plate_mask)

    # Reshape for K-means
    Z = plate_pixels_bgr.reshape((-1, 3))
    Z = np.float32(Z)

    # Remove black pixels (outside plate mask)
    non_zero_mask = np.any(Z > 0, axis=1)
    Z_filtered = Z[non_zero_mask]

    if len(Z_filtered) < 100:
        return [], plate_center, plate_radius

    # K-means with K=6 (expect ~4-6 food items on a thali)
    K = min(8, max(3, len(Z_filtered) // 5000))
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
    try:
        _, labels_filtered, centers = cv2.kmeans(Z_filtered, K, None, criteria, 5, cv2.KMEANS_PP_CENTERS)
    except Exception:
        return [], plate_center, plate_radius

    # Reconstruct the label image
    labels_full = np.zeros(Z.shape[0], dtype=np.int32) - 1
    labels_full[non_zero_mask] = labels_filtered.flatten()
    label_image = labels_full.reshape((h, w))

    # 3. Extract contours for each cluster
    food_contours = []
    min_area = h * w * 0.008  # At least 0.8% of image

    for k in range(K):
        cluster_mask = np.uint8(label_image == k) * 255

        # Apply morphological cleaning
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        cluster_mask = cv2.morphologyEx(cluster_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        cluster_mask = cv2.morphologyEx(cluster_mask, cv2.MORPH_OPEN, kernel, iterations=1)

        # Ensure within plate boundary
        cluster_mask = cv2.bitwise_and(cluster_mask, plate_mask)

        contours, _ = cv2.findContours(cluster_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > min_area and area < (h * w * 0.7):
                food_contours.append(cnt)

    # 4. Sort by area descending and limit to 8 detections
    food_contours = sorted(food_contours, key=cv2.contourArea, reverse=True)[:8]

    # 5. Merge overlapping contours (IoU > 0.5)
    merged = []
    used = set()
    for i, c1 in enumerate(food_contours):
        if i in used:
            continue
        x1, y1, w1, h1 = cv2.boundingRect(c1)
        merged_contour = c1
        for j, c2 in enumerate(food_contours):
            if j <= i or j in used:
                continue
            x2, y2, w2, h2 = cv2.boundingRect(c2)
            # Calculate IoU of bounding boxes
            xi = max(x1, x2)
            yi = max(y1, y2)
            xa = min(x1 + w1, x2 + w2)
            ya = min(y1 + h1, y2 + h2)
            inter = max(0, xa - xi) * max(0, ya - yi)
            union = w1 * h1 + w2 * h2 - inter
            if union > 0 and inter / union > 0.45:
                used.add(j)
                # Merge by taking the convex hull of both
                merged_contour = cv2.convexHull(np.vstack([merged_contour, c2]))
        merged.append(merged_contour)
        used.add(i)

    return merged, plate_center, plate_radius


def classify_by_hsv_analysis(image, contour) -> str:
    """
    Enhanced color-based classifier using HSV color space analysis
    instead of raw BGR values for much better Indian food identification.
    """
    h_img, w_img = image.shape[:2]
    mask = np.zeros((h_img, w_img), dtype=np.uint8)
    cv2.drawContours(mask, [contour], -1, 255, -1)

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mean_hsv = cv2.mean(hsv, mask=mask)[:3]
    mean_bgr = cv2.mean(image, mask=mask)[:3]

    hue, sat, val = mean_hsv
    b, g, r = mean_bgr

    area = cv2.contourArea(contour)
    total_area = h_img * w_img

    # Aspect ratio of bounding rect
    x, y, bw, bh = cv2.boundingRect(contour)
    aspect = bw / (bh + 1e-6)

    # Flat item, large, low saturation, light tan → Roti / Chapati / Naan
    if sat < 90 and val > 120 and 15 < hue < 30 and area > total_area * 0.04:
        if aspect > 1.5 or aspect < 0.66:
            return "Naan"
        return "Roti / Chapati"

    # Very white/bright with low saturation → Rice
    if val > 160 and sat < 60:
        return "Cooked White Rice"

    # Bright green → Salad / Chutney
    if 35 < hue < 80 and sat > 80 and val > 80:
        if area < total_area * 0.03:
            return "Green Chutney"
        return "Mixed Vegetable Salad"

    # Deep yellow/orange with high saturation → Dal
    if 15 < hue < 28 and sat > 100 and val > 100:
        return "Yellow Dal Tadka"

    # Orange-red with medium-high sat → Curry (paneer/chicken)
    if 5 < hue < 18 and sat > 100 and val > 80:
        if r > 160 and g < 100:
            return "Chicken Curry"
        return "Paneer Butter Masala"

    # Dark red/brown, rich → Biryani or heavy curry
    if hue < 15 and sat > 60 and val > 60 and val < 160:
        if area > total_area * 0.15:
            return "Chicken Biryani"
        return "Butter Chicken"

    # Very small area → likely a side (pickle, chutney, papad)
    if area < total_area * 0.02:
        if sat > 100:
            return "Pickle / Achar"
        return "Papad"

    # White with slight yellow tint → Curd / Raita
    if val > 150 and sat < 50 and hue < 30:
        return "Curd / Raita"

    # Dark green → Palak Paneer
    if 35 < hue < 70 and sat > 50 and val < 120:
        return "Palak Paneer"

    # Brown medium sat → could be Rajma or Chole
    if 10 < hue < 25 and 40 < sat < 110 and 60 < val < 140:
        return "Chole / Chana Masala"

    # Fallback: cycle through common items based on region position
    cx = x + bw // 2
    cy = y + bh // 2
    # Items closer to the center of plate are usually rice/main
    dist_from_center = math.sqrt((cx - w_img / 2) ** 2 + (cy - h_img / 2) ** 2)
    rel_dist = dist_from_center / (max(w_img, h_img) / 2)

    if rel_dist < 0.25:
        return "Cooked White Rice"
    elif rel_dist < 0.5:
        return "Yellow Dal Tadka"
    else:
        return "Roti / Chapati"


# ============================================================================
# MAIN ANALYSIS FUNCTION
# ============================================================================
def analyze_uploaded_image(file_name: str, db_session) -> dict:
    """
    [Phase 1 Upgrade] Processes an uploaded meal image through the production pipeline.

    Pipeline order:
      1. Image Quality Check (blur, brightness, plate detection)
      2. Demo mode short-circuit (if filename matches preset)
      3. Gemini Vision API (primary AI detection)
      4. OpenRouter Vision API (fallback AI detection)
      5. OpenCV HSV + K-means (offline fallback)
      6. Nutrition Validation (rule engine + optional LLM)
    """
    file_path = os.path.join(settings.UPLOAD_DIR, file_name)
    base_name, ext = os.path.splitext(file_name)

    processed_file_name = f"{base_name}_processed{ext}"
    mask_file_name = f"{base_name}_mask{ext}"
    depth_file_name = f"{base_name}_depth{ext}"

    processed_path = os.path.join(settings.UPLOAD_DIR, processed_file_name)
    mask_path = os.path.join(settings.UPLOAD_DIR, mask_file_name)
    depth_path = os.path.join(settings.UPLOAD_DIR, depth_file_name)

    image = cv2.imread(file_path)
    if image is None:
        raise ValueError(f"Could not load image at {file_path}")

    h, w, c = image.shape
    detected_items = []

    # ── Phase 1: Image Quality Gate ─────────────────────────────────────────
    # Skip quality check for demo meals (pre-built 1x1 pixel blobs)
    is_demo = any(key in file_name.lower() for key in DEMO_MEALS.keys())
    if not is_demo:
        quality_report = assess_image_quality(file_path)
        if not quality_report.is_acceptable:
            issue_summary = " | ".join(quality_report.issues) if quality_report.issues else "Low quality score"
            raise ValueError(
                f"Image quality check failed (score={quality_report.quality_score:.0f}/100): {issue_summary}. "
                f"Please upload a clearer image with the food plate visible."
            )

    # Check for demo meals
    matched_demo = None
    for key in DEMO_MEALS.keys():
        if key in file_name.lower():
            matched_demo = key
            break

    mask_colors = [
        (255, 80, 80), (80, 255, 80), (80, 80, 255),
        (255, 255, 80), (255, 80, 255), (80, 255, 255),
        (200, 160, 80), (160, 80, 200)
    ]

    bbox_img = image.copy()
    mask_img = image.copy()
    depth_img = np.zeros((h, w), dtype=np.uint8)

    if matched_demo:
        # =============== DEMO MODE ===============
        demo_items = DEMO_MEALS[matched_demo]
        for idx, item in enumerate(demo_items):
            xmin, ymin, xmax, ymax = item["bbox"]
            sx = int((xmin / 500.0) * w)
            sy = int((ymin / 500.0) * h)
            ex = int((xmax / 500.0) * w)
            ey = int((ymax / 500.0) * h)
            bbox = [sx, sy, ex, ey]
            color = mask_colors[idx % len(mask_colors)]

            cv2.rectangle(bbox_img, (sx, sy), (ex, ey), color, 3)
            label = f"{item['name']} ({int(item['weight_g'])}g)"
            cv2.putText(bbox_img, label, (sx, sy - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            cx, cy = (sx + ex) // 2, (sy + ey) // 2
            rx, ry = (ex - sx) // 2, (ey - sy) // 2
            cv2.ellipse(mask_img, (cx, cy), (rx, ry), 0, 0, 360, color, -1)

            item_depth = np.zeros((h, w), dtype=np.uint8)
            cv2.ellipse(item_depth, (cx, cy), (rx, ry), 0, 0, 360, 255, -1)
            dist = cv2.distanceTransform(item_depth, cv2.DIST_L2, 3)
            cv2.normalize(dist, dist, 0, 200, cv2.NORM_MINMAX)
            depth_img = np.maximum(depth_img, dist.astype(np.uint8))

            food_name = item["name"]
            matched_name, food_info = match_food_to_database(food_name)
            weight = item["weight_g"]

            detected_items.append({
                "name": matched_name,
                "weight_g": round(weight, 1),
                "volume_cm3": round(item["volume_cm3"], 1),
                "bounding_box": json.dumps(bbox),
                "density": food_info["density"],
                "calories": round((food_info["calories_100g"] * weight) / 100.0, 1),
                "protein": round((food_info["protein_100g"] * weight) / 100.0, 2),
                "carbs": round((food_info["carbs_100g"] * weight) / 100.0, 2),
                "fat": round((food_info["fat_100g"] * weight) / 100.0, 2),
                "fiber": round((food_info["fiber_100g"] * weight) / 100.0, 2),
                "sodium": round((food_info["sodium_100g"] * weight) / 100.0, 1),
                "sugar": round((food_info["sugar_100g"] * weight) / 100.0, 2)
            })

        cv2.addWeighted(mask_img, 0.4, image, 0.6, 0, mask_img)
        depth_color = cv2.applyColorMap(depth_img, cv2.COLORMAP_INFERNO)

    else:
        # =============== GEMINI / OPENROUTER VISION MODE ===============
        gemini_items = None
        
        # Try primary Gemini API key
        if settings.GEMINI_API_KEY:
            gemini_items = classify_foods_with_gemini(file_path, settings.GEMINI_API_KEY)
            
        # Try OpenRouter API key as fallback/alternative
        if not gemini_items and settings.OPENROUTER_API_KEY:
            gemini_items = classify_foods_with_openrouter(file_path, settings.OPENROUTER_API_KEY)

        if gemini_items:
            # Use Gemini's results for accurate detection
            plate_pixel_diameter = max(w, h) * 0.85
            pixels_per_cm = plate_pixel_diameter / 26.0

            for idx, gi in enumerate(gemini_items):
                food_name = gi.get("name", "Unknown")
                bbox_pct = gi.get("bbox_pct", [10, 10, 40, 40])
                est_weight = gi.get("weight_g", 100)

                # Convert percentage bbox to pixel coords
                xmin = int(bbox_pct[0] / 100.0 * w)
                ymin = int(bbox_pct[1] / 100.0 * h)
                xmax = int(bbox_pct[2] / 100.0 * w)
                ymax = int(bbox_pct[3] / 100.0 * h)
                xmin, ymin = max(0, xmin), max(0, ymin)
                xmax, ymax = min(w, xmax), min(h, ymax)
                bbox = [xmin, ymin, xmax, ymax]

                color = mask_colors[idx % len(mask_colors)]

                # Draw bounding box
                cv2.rectangle(bbox_img, (xmin, ymin), (xmax, ymax), color, 3)
                label = f"{food_name} ({int(est_weight)}g)"
                # Draw label background
                (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)
                cv2.rectangle(bbox_img, (xmin, ymin - th - 10), (xmin + tw + 6, ymin), color, -1)
                cv2.putText(bbox_img, label, (xmin + 3, ymin - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 2)

                # Elliptical mask
                cx, cy = (xmin + xmax) // 2, (ymin + ymax) // 2
                rx, ry = (xmax - xmin) // 2, (ymax - ymin) // 2
                cv2.ellipse(mask_img, (cx, cy), (max(1, rx), max(1, ry)), 0, 0, 360, color, -1)

                # Depth map
                item_depth = np.zeros((h, w), dtype=np.uint8)
                cv2.ellipse(item_depth, (cx, cy), (max(1, rx), max(1, ry)), 0, 0, 360, 255, -1)
                dist = cv2.distanceTransform(item_depth, cv2.DIST_L2, 3)
                cv2.normalize(dist, dist, 0, 200, cv2.NORM_MINMAX)
                depth_img = np.maximum(depth_img, dist.astype(np.uint8))

                # Volume estimation from bbox dimensions
                area_cm2 = ((xmax - xmin) / pixels_per_cm) * ((ymax - ymin) / pixels_per_cm) * 0.785
                est_height_cm = 2.0 + (min(rx, ry) / max(w, h)) * 3.0
                volume = area_cm2 * est_height_cm

                matched_name, food_info = match_food_to_database(food_name)
                weight = max(15.0, min(float(est_weight), 500.0))

                detected_items.append({
                    "name": matched_name,
                    "weight_g": round(weight, 1),
                    "volume_cm3": round(volume, 1),
                    "bounding_box": json.dumps(bbox),
                    "density": food_info["density"],
                    "calories": round((food_info["calories_100g"] * weight) / 100.0, 1),
                    "protein": round((food_info["protein_100g"] * weight) / 100.0, 2),
                    "carbs": round((food_info["carbs_100g"] * weight) / 100.0, 2),
                    "fat": round((food_info["fat_100g"] * weight) / 100.0, 2),
                    "fiber": round((food_info["fiber_100g"] * weight) / 100.0, 2),
                    "sodium": round((food_info["sodium_100g"] * weight) / 100.0, 1),
                    "sugar": round((food_info["sugar_100g"] * weight) / 100.0, 2)
                })

            cv2.addWeighted(mask_img, 0.4, image, 0.6, 0, mask_img)
            depth_img = cv2.GaussianBlur(depth_img, (11, 11), 0)
            depth_color = cv2.applyColorMap(depth_img, cv2.COLORMAP_INFERNO)

        else:
            # =============== IMPROVED OPENCV FALLBACK ===============
            food_contours, plate_center, plate_radius = segment_food_regions_opencv(image)

            pixels_per_cm = (plate_radius * 2.0) / 26.0
            cm2_per_pixel2 = 1.0 / (pixels_per_cm ** 2)

            if not food_contours:
                # Emergency fallback: quadrant split
                qw, qh = int(w * 0.4), int(h * 0.4)
                c1 = np.array([[[int(w*0.05), int(h*0.05)]], [[int(w*0.05), int(h*0.45)]], [[int(w*0.45), int(h*0.45)]], [[int(w*0.45), int(h*0.05)]]], dtype=np.int32)
                c2 = np.array([[[int(w*0.55), int(h*0.05)]], [[int(w*0.55), int(h*0.45)]], [[int(w*0.95), int(h*0.45)]], [[int(w*0.95), int(h*0.05)]]], dtype=np.int32)
                c3 = np.array([[[int(w*0.05), int(h*0.55)]], [[int(w*0.05), int(h*0.95)]], [[int(w*0.45), int(h*0.95)]], [[int(w*0.45), int(h*0.55)]]], dtype=np.int32)
                c4 = np.array([[[int(w*0.55), int(h*0.55)]], [[int(w*0.55), int(h*0.95)]], [[int(w*0.95), int(h*0.95)]], [[int(w*0.95), int(h*0.55)]]], dtype=np.int32)
                food_contours = [c1, c2, c3, c4]

            for idx, contour in enumerate(food_contours[:8]):
                cx_coord, cy_coord, cw_coord, ch_coord = cv2.boundingRect(contour)
                bbox = [cx_coord, cy_coord, cx_coord + cw_coord, cy_coord + ch_coord]

                area_pixels = cv2.contourArea(contour)
                if area_pixels == 0:
                    area_pixels = cw_coord * ch_coord * 0.785
                area_cm2 = area_pixels * cm2_per_pixel2

                single_mask = np.zeros((h, w), dtype=np.uint8)
                cv2.drawContours(single_mask, [contour], -1, 255, -1)

                dist = cv2.distanceTransform(single_mask, cv2.DIST_L2, 3)
                cv2.normalize(dist, dist, 0, 200, cv2.NORM_MINMAX)
                depth_img = np.maximum(depth_img, dist.astype(np.uint8))

                mean_val = cv2.mean(dist, mask=single_mask)[0]
                est_height_cm = 1.5 + (mean_val / 200.0) * 2.5
                volume = area_cm2 * est_height_cm

                # Classify using improved HSV analysis
                food_name = classify_by_hsv_analysis(image, contour)
                food_info = FOOD_DENSITY_NUTRITION[food_name]
                weight = volume * food_info["density"]
                weight = max(15.0, min(weight, 500.0))

                color = mask_colors[idx % len(mask_colors)]
                cv2.rectangle(bbox_img, (cx_coord, cy_coord), (cx_coord + cw_coord, cy_coord + ch_coord), color, 3)
                label = f"{food_name} ({int(weight)}g)"
                (tw, th_text), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)
                cv2.rectangle(bbox_img, (cx_coord, cy_coord - th_text - 10), (cx_coord + tw + 6, cy_coord), color, -1)
                cv2.putText(bbox_img, label, (cx_coord + 3, cy_coord - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 2)

                cv2.drawContours(mask_img, [contour], -1, color, -1)

                detected_items.append({
                    "name": food_name,
                    "weight_g": round(weight, 1),
                    "volume_cm3": round(volume, 1),
                    "bounding_box": json.dumps(bbox),
                    "density": food_info["density"],
                    "calories": round((food_info["calories_100g"] * weight) / 100.0, 1),
                    "protein": round((food_info["protein_100g"] * weight) / 100.0, 2),
                    "carbs": round((food_info["carbs_100g"] * weight) / 100.0, 2),
                    "fat": round((food_info["fat_100g"] * weight) / 100.0, 2),
                    "fiber": round((food_info["fiber_100g"] * weight) / 100.0, 2),
                    "sodium": round((food_info["sodium_100g"] * weight) / 100.0, 1),
                    "sugar": round((food_info["sugar_100g"] * weight) / 100.0, 2)
                })

            cv2.addWeighted(mask_img, 0.4, image, 0.6, 0, mask_img)
            depth_img = cv2.GaussianBlur(depth_img, (11, 11), 0)
            depth_color = cv2.applyColorMap(depth_img, cv2.COLORMAP_INFERNO)

    # Save all visualizations
    cv2.imwrite(processed_path, bbox_img)
    cv2.imwrite(mask_path, mask_img)
    cv2.imwrite(depth_path, depth_color)

    # ── Phase 1: Nutrition Validation ────────────────────────────────────────
    if detected_items:
        validation = validate_nutrition(
            food_items=detected_items,
            food_db=FOOD_DENSITY_NUTRITION,
            use_llm=True   # LLM fallback only fires when critical issues found
        )
        # Attach validation metadata to the result (non-blocking)
        validation_summary = validation.to_dict()
    else:
        validation_summary = {"is_valid": True, "issues": [], "warnings": []}

    return {
        "original_url": f"/static/uploads/{file_name}",
        "processed_url": f"/static/uploads/{processed_file_name}",
        "mask_url": f"/static/uploads/{mask_file_name}",
        "depth_url": f"/static/uploads/{depth_file_name}",
        "food_items": detected_items,
        "validation": validation_summary
    }
