"""
Phase 2: Grounding DINO Open-Vocabulary Food Detector

Replaces the Gemini-first detection strategy with a LOCAL first approach:
  1. Grounding DINO detects food regions using a rich text prompt
  2. Results are filtered by confidence threshold
  3. Low-confidence or failed detections fall back to Gemini/OpenRouter

Model: IDEA-Research/grounding-dino-tiny (Swin-T backbone)
VRAM:  ~1.5 GB
Speed: ~1.5s per image on RTX 3050

Grounding DINO text prompt format:
  - Phrases separated by " . " (period + space)
  - Each phrase becomes an independent detection class
  - No training needed — zero-shot open-vocabulary detection
"""

from __future__ import annotations

import cv2
import numpy as np
from PIL import Image
from typing import Optional

from app.services.model_registry import get_grounding_dino, DEVICE

# ─── Detection prompt ─────────────────────────────────────────────────────────
# Each period-separated phrase = one detection category
# Broad categories first (for recall), specific names for precision
FOOD_DETECTION_PROMPT = (
    "rice . dal . curry . roti . bread . naan . paratha . puri . "
    "biryani . idli . dosa . upma . poha . sambar . rasam . "
    "paneer . cottage cheese . "
    "chicken . mutton . fish . prawn . egg . omelette . kebab . "
    "salad . vegetable . sabzi . chutney . pickle . papad . "
    "sweet . dessert . halwa . ladoo . kheer . gulab jamun . "
    "samosa . pakora . vada . snack . "
    "fruit . mango . banana . apple . "
    "nuts . seeds . almonds . cashew . "
    "soup . gravy . stew . "
    "tea . coffee . lassi . yogurt . curd"
)

# ─── Confidence thresholds ────────────────────────────────────────────────────
BOX_THRESHOLD  = 0.30   # Min bbox score to keep detection
TEXT_THRESHOLD = 0.25   # Min text-match score to keep detection
HIGH_CONF      = 0.60   # Above this → accept without Gemini validation
LOW_CONF       = 0.35   # Below this → send to Gemini for verification

# ─── Physical constraints ─────────────────────────────────────────────────────
MIN_BBOX_AREA_RATIO = 0.005   # Must be at least 0.5% of image
MAX_BBOX_AREA_RATIO = 0.95    # Must be less than 95% of image
MAX_DETECTIONS      = 10


def detect_foods(image_path: str) -> tuple[list[dict], str]:
    """
    Detect food items in an image using Grounding DINO.

    Args:
        image_path: Absolute path to the uploaded image.

    Returns:
        (detections, method) where:
          detections: List of detection dicts:
            {
              name: str,              # matched phrase from prompt
              confidence: float,      # bbox confidence score
              bbox_pct: [x1%, y1%, x2%, y2%],   # percentage coords
              bbox_px: [x1, y1, x2, y2],         # pixel coords
              needs_gemini: bool      # True if low confidence
            }
          method: "grounding_dino" | "grounding_dino_unavailable"
    """
    gdino = get_grounding_dino()

    if gdino is None:
        print("[Detector] Grounding DINO unavailable — skipping to API fallback")
        return [], "grounding_dino_unavailable"

    try:
        import torch
        model     = gdino["model"]
        processor = gdino["processor"]

        # Load image
        pil_image = Image.open(image_path).convert("RGB")
        img_w, img_h = pil_image.size

        # Prepare inputs
        inputs = processor(
            images=pil_image,
            text=FOOD_DETECTION_PROMPT,
            return_tensors="pt"
        ).to(DEVICE)

        # Run inference
        with torch.no_grad():
            outputs = model(**inputs)

        # Post-process: convert logits → boxes + labels
        results = processor.post_process_grounded_object_detection(
            outputs,
            inputs.input_ids,
            box_threshold=BOX_THRESHOLD,
            text_threshold=TEXT_THRESHOLD,
            target_sizes=[(img_h, img_w)]
        )

        detections = []
        if results and len(results) > 0:
            result = results[0]
            boxes  = result.get("boxes", [])
            scores = result.get("scores", [])
            labels = result.get("labels", [])

            img_area = img_w * img_h

            for box, score, label in zip(boxes, scores, labels):
                score_val = float(score)
                x1, y1, x2, y2 = [int(v) for v in box.tolist()]

                # Clamp to image bounds
                x1 = max(0, min(x1, img_w - 1))
                y1 = max(0, min(y1, img_h - 1))
                x2 = max(x1 + 5, min(x2, img_w))
                y2 = max(y1 + 5, min(y2, img_h))

                # Filter by area
                box_area = (x2 - x1) * (y2 - y1)
                area_ratio = box_area / img_area
                if area_ratio < MIN_BBOX_AREA_RATIO or area_ratio > MAX_BBOX_AREA_RATIO:
                    continue

                detections.append({
                    "name":         str(label).strip(),
                    "confidence":   round(score_val, 3),
                    "bbox_pct":     [
                        round(x1 / img_w * 100, 1),
                        round(y1 / img_h * 100, 1),
                        round(x2 / img_w * 100, 1),
                        round(y2 / img_h * 100, 1),
                    ],
                    "bbox_px":      [x1, y1, x2, y2],
                    "needs_gemini": score_val < LOW_CONF
                })

        # Sort by confidence descending, cap at MAX_DETECTIONS
        detections = sorted(detections, key=lambda d: d["confidence"], reverse=True)
        detections = detections[:MAX_DETECTIONS]

        # Deduplicate overlapping boxes (NMS-style IoU filter)
        detections = _nms_filter(detections, iou_threshold=0.45)

        print(f"[Detector] Grounding DINO found {len(detections)} food regions")
        for d in detections:
            flag = " [needs Gemini]" if d["needs_gemini"] else ""
            print(f"  '{d['name']}' conf={d['confidence']:.3f}{flag}")

        return detections, "grounding_dino"

    except Exception as e:
        print(f"[Detector] Grounding DINO inference error: {e}")
        return [], "grounding_dino_error"


def _iou(a: list[int], b: list[int]) -> float:
    """Compute IoU between two [x1,y1,x2,y2] boxes."""
    xi1 = max(a[0], b[0])
    yi1 = max(a[1], b[1])
    xi2 = min(a[2], b[2])
    yi2 = min(a[3], b[3])
    inter = max(0, xi2 - xi1) * max(0, yi2 - yi1)
    area_a = (a[2] - a[0]) * (a[3] - a[1])
    area_b = (b[2] - b[0]) * (b[3] - b[1])
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0.0


def _nms_filter(detections: list[dict], iou_threshold: float = 0.45) -> list[dict]:
    """
    Simple greedy NMS — removes duplicate overlapping boxes.
    Detections must be sorted by confidence descending before calling.
    """
    kept = []
    suppressed = set()
    for i, det in enumerate(detections):
        if i in suppressed:
            continue
        kept.append(det)
        for j, other in enumerate(detections):
            if j <= i or j in suppressed:
                continue
            if _iou(det["bbox_px"], other["bbox_px"]) > iou_threshold:
                suppressed.add(j)
    return kept


def crop_food_region(image_bgr: np.ndarray, bbox_px: list[int],
                     padding_ratio: float = 0.05) -> np.ndarray:
    """
    Crops a food region from the image with optional padding.

    Args:
        image_bgr: Full image as BGR numpy array.
        bbox_px:   [x1, y1, x2, y2] pixel coordinates.
        padding_ratio: Fractional padding to add around the crop.

    Returns:
        Cropped BGR numpy array.
    """
    h, w = image_bgr.shape[:2]
    x1, y1, x2, y2 = bbox_px
    pad_x = int((x2 - x1) * padding_ratio)
    pad_y = int((y2 - y1) * padding_ratio)
    x1 = max(0, x1 - pad_x)
    y1 = max(0, y1 - pad_y)
    x2 = min(w, x2 + pad_x)
    y2 = min(h, y2 + pad_y)
    return image_bgr[y1:y2, x1:x2]
