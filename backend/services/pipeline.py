"""
NutriVision AI — End-to-End Inference Pipeline

Orchestrates: Image → Detection → Classification → Segmentation →
              Portion Estimation → Nutrition → Health Score → Recommendations
"""

import time
import io
import numpy as np
from typing import Optional
from PIL import Image, ImageEnhance, ImageFilter
import cv2
from loguru import logger

from models.detector import FoodDetector
from models.classifier import FoodClassifier
from models.segmentor import FoodSegmentor
from models.depth_estimator import PortionEstimator
from nutrition_engine.calculator import calculate_meal_nutrition
from recommendation_engine.health_scorer import calculate_health_score


# Singleton model instances (loaded once at startup)
_detector: Optional[FoodDetector] = None
_classifier: Optional[FoodClassifier] = None
_segmentor: Optional[FoodSegmentor] = None
_estimator: Optional[PortionEstimator] = None


def get_models():
    """Lazy-load and cache all ML models."""
    global _detector, _classifier, _segmentor, _estimator
    if _detector is None:
        logger.info("🔄 Loading ML models...")
        _detector = FoodDetector()
        _classifier = FoodClassifier()
        _segmentor = FoodSegmentor()
        _estimator = PortionEstimator()
        logger.success("✅ All models ready")
    return _detector, _classifier, _segmentor, _estimator


def preprocess_image(image_bytes: bytes) -> tuple[np.ndarray, int, int]:
    """
    Preprocess uploaded image for model inference.

    Steps:
    1. Decode bytes → PIL Image
    2. Convert to RGB
    3. Resize to max 1024px (preserve aspect ratio)
    4. Enhance contrast slightly
    5. Reduce noise
    6. Convert to numpy array

    Returns:
        (image_array, width, height)
    """
    # Load image
    pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    original_w, original_h = pil_image.size

    # Resize (max 1024 on longest side)
    max_dim = 1024
    if max(original_w, original_h) > max_dim:
        scale = max_dim / max(original_w, original_h)
        new_w = int(original_w * scale)
        new_h = int(original_h * scale)
        pil_image = pil_image.resize((new_w, new_h), Image.LANCZOS)

    # Enhance contrast
    enhancer = ImageEnhance.Contrast(pil_image)
    pil_image = enhancer.enhance(1.1)

    # Convert to numpy
    image_array = np.array(pil_image)

    # Denoise with OpenCV
    image_array = cv2.fastNlMeansDenoisingColored(image_array, None, 5, 5, 7, 21)

    h, w = image_array.shape[:2]
    return image_array, w, h


async def run_analysis_pipeline(
    image_bytes: bytes,
    user_profile: Optional[dict] = None,
) -> dict:
    """
    Full meal analysis pipeline.

    Args:
        image_bytes: Raw image file bytes
        user_profile: Optional user profile for personalized recommendations

    Returns:
        Complete analysis result dict
    """
    pipeline_start = time.time()

    detector, classifier, segmentor, estimator = get_models()

    # ── Step 1: Image Preprocessing ─────────────────────────────────────────
    t0 = time.time()
    image_array, img_w, img_h = preprocess_image(image_bytes)
    logger.debug(f"Preprocessing: {(time.time()-t0)*1000:.1f}ms | {img_w}×{img_h}px")

    # ── Step 2: YOLOv11 Food Detection ──────────────────────────────────────
    t0 = time.time()
    detections = detector.detect(image_array, img_w, img_h)
    logger.debug(f"Detection: {(time.time()-t0)*1000:.1f}ms | {len(detections)} items found")

    if not detections:
        return {
            "detected_foods": [],
            "total_nutrition": {},
            "health_score": 0,
            "health_grade": "No food detected",
            "health_feedback": ["No food items detected. Please try a clearer photo with better lighting."],
            "macro_percentages": {},
            "analysis_time_ms": int((time.time() - pipeline_start) * 1000),
            "is_demo": detector.demo_mode,
        }

    # ── Step 3: ConvNeXt Classification + SAM2 Segmentation ─────────────────
    processed_foods = []
    for detection in detections:
        food_name = detection["food_name"]
        bbox = detection["bbox"]

        # 3a. Classify (refine label)
        t0 = time.time()
        crop = image_array[
            max(0, bbox[1]):min(img_h, bbox[3]),
            max(0, bbox[0]):min(img_w, bbox[2])
        ]
        classification = classifier.classify(crop, food_name)
        final_food_name = classification["final_label"]
        logger.debug(f"  Classify '{food_name}' → '{final_food_name}': {(time.time()-t0)*1000:.1f}ms")

        # 3b. Segment (get mask area for portion estimation)
        t0 = time.time()
        segmentation = segmentor.segment(image_array, bbox, final_food_name)
        mask_area = segmentation.get("mask_area_pixels")
        logger.debug(f"  Segment: {(time.time()-t0)*1000:.1f}ms | mask_area={mask_area}")

        # 3c. Estimate portion weight
        t0 = time.time()
        portion = estimator.estimate_weight(
            food_name=final_food_name,
            bbox=bbox,
            image_width=img_w,
            image_height=img_h,
            mask_area_pixels=mask_area,
        )
        weight_g = portion["weight_g"]
        logger.debug(f"  Portion '{final_food_name}': {weight_g}g | {(time.time()-t0)*1000:.1f}ms")

        processed_foods.append({
            "food_name": final_food_name,
            "original_detection": food_name,
            "detection_confidence": detection["confidence"],
            "classification_confidence": classification["confidence"],
            "portion_confidence": portion["confidence"],
            "weight_g": weight_g,
            "bbox": bbox,
            "segmentation": segmentation,
        })

    # ── Step 4: Nutrition Calculation ────────────────────────────────────────
    t0 = time.time()
    nutrition_inputs = [
        {"food_name": f["food_name"], "weight_g": f["weight_g"]}
        for f in processed_foods
    ]
    meal_nutrition = calculate_meal_nutrition(nutrition_inputs)
    logger.debug(f"Nutrition calc: {(time.time()-t0)*1000:.1f}ms")

    # ── Step 5: Health Score ─────────────────────────────────────────────────
    t0 = time.time()
    health = calculate_health_score(meal_nutrition, processed_foods, user_profile)
    logger.debug(f"Health score: {health['overall_score']}/100 | {(time.time()-t0)*1000:.1f}ms")

    # ── Step 6: Build Response ───────────────────────────────────────────────
    detected_foods_response = []
    for food, nutrition_item in zip(processed_foods, meal_nutrition["items"]):
        n = nutrition_item["total"]
        detected_foods_response.append({
            "food_name": food["food_name"],
            "original_detection": food["original_detection"],
            "confidence": round((food["detection_confidence"] + food["classification_confidence"]) / 2, 3),
            "detection_confidence": food["detection_confidence"],
            "classification_confidence": food["classification_confidence"],
            "estimated_weight_g": food["weight_g"],
            "portion_confidence": food["portion_confidence"],
            "calories": n.get("calories", 0),
            "protein_g": n.get("protein", 0),
            "carbs_g": n.get("carbs", 0),
            "fat_g": n.get("fat", 0),
            "fiber_g": n.get("fiber", 0),
            "sodium_mg": n.get("sodium", 0),
            "calcium_mg": n.get("calcium", 0),
            "iron_mg": n.get("iron", 0),
            "bbox": food["bbox"],
            "category": nutrition_item.get("category", "unknown"),
            "demo": food.get("demo", True),
        })

    total_time_ms = int((time.time() - pipeline_start) * 1000)
    logger.info(f"✅ Pipeline complete: {total_time_ms}ms | {len(processed_foods)} foods | Score: {health['overall_score']}/100")

    return {
        "detected_foods": detected_foods_response,
        "total_nutrition": meal_nutrition["totals"],
        "macro_percentages": meal_nutrition["macro_percentages"],
        "daily_value_percent": meal_nutrition.get("daily_value_percent", {}),
        "health_score": health["overall_score"],
        "health_grade": health["grade"],
        "health_grade_emoji": health["grade_emoji"],
        "health_grade_color": health["grade_color"],
        "health_feedback": health["feedback"],
        "health_positives": health["positives"],
        "health_factor_scores": health["factor_scores"],
        "analysis_time_ms": total_time_ms,
        "item_count": len(processed_foods),
        "total_weight_g": meal_nutrition["total_weight_g"],
        "not_found_foods": meal_nutrition.get("not_found_foods", []),
        "is_demo": detector.demo_mode,
        "image_dimensions": {"width": img_w, "height": img_h},
    }
