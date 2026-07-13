"""
NutriVision AI — ML Model: YOLOv11 Food Detector

Detects all food items in a meal image with bounding boxes.
- Real model: Ultralytics YOLOv11 fine-tuned on Indian Food Dataset
- Demo mode: Realistic mock inference for portfolio demonstration

To use real model: download weights from HuggingFace and set YOLO_MODEL_PATH in .env
"""

import os
import random
import time
from typing import Optional
import numpy as np
from loguru import logger


# Indian foods that YOLOv11 can detect
DETECTABLE_FOODS = [
    "basmati rice", "roti", "dal tadka", "dal makhani", "chicken curry",
    "butter chicken", "paneer butter masala", "palak paneer", "chana masala",
    "rajma", "curd", "raita", "green salad", "kachumber salad", "samosa",
    "pakora", "idli", "dosa", "masala dosa", "upma", "poha", "pav bhaji",
    "vada pav", "chicken biryani", "veg biryani", "pulao", "papad", "pickle",
    "chai", "lassi", "paratha", "aloo paratha", "naan", "puri", "fish curry",
    "egg curry", "boiled eggs", "kheer", "gulab jamun", "bhindi masala",
    "baingan bharta", "aloo sabzi", "mixed vegetable", "moong dal", "sambar",
    "curd rice", "lemon rice", "dhokla", "chutney",
]

# Typical portion weights per food (grams) — used in mock estimation
TYPICAL_PORTIONS = {
    "basmati rice": (150, 280), "roti": (30, 50), "dal tadka": (120, 200),
    "dal makhani": (120, 200), "chicken curry": (150, 250), "butter chicken": (150, 250),
    "paneer butter masala": (120, 200), "palak paneer": (120, 200),
    "chana masala": (130, 220), "rajma": (130, 220), "curd": (80, 150),
    "raita": (80, 120), "green salad": (60, 120), "kachumber salad": (60, 120),
    "samosa": (50, 80), "pakora": (80, 140), "idli": (60, 100),
    "dosa": (80, 150), "masala dosa": (100, 180), "upma": (120, 200),
    "poha": (120, 200), "pav bhaji": (200, 320), "vada pav": (150, 220),
    "chicken biryani": (200, 350), "veg biryani": (200, 350),
    "pulao": (180, 300), "papad": (10, 20), "pickle": (10, 25),
    "chai": (150, 200), "lassi": (200, 300), "paratha": (60, 100),
    "aloo paratha": (80, 120), "naan": (80, 130), "puri": (40, 70),
    "fish curry": (150, 250), "egg curry": (120, 200), "boiled eggs": (50, 100),
    "kheer": (120, 200), "gulab jamun": (60, 100), "bhindi masala": (100, 180),
    "baingan bharta": (100, 180), "aloo sabzi": (100, 180),
    "mixed vegetable": (100, 180), "moong dal": (120, 200),
    "sambar": (100, 180), "curd rice": (150, 250), "lemon rice": (150, 250),
    "dhokla": (100, 180), "chutney": (20, 50),
}

CONFIDENCE_RANGE = (0.78, 0.98)


class FoodDetector:
    """
    YOLOv11-based food detector for Indian cuisine.

    In production, this loads a real .pt model file.
    In demo mode, it returns realistic mock detections.
    """

    def __init__(self):
        self.model = None
        self.model_path = os.getenv("YOLO_MODEL_PATH", "weights/nutrivision_yolov11.pt")
        self.confidence_threshold = float(os.getenv("YOLO_CONFIDENCE_THRESHOLD", "0.5"))
        self.demo_mode = True
        self._load_model()

    def _load_model(self):
        """Load YOLOv11 model from weights file."""
        if os.path.exists(self.model_path):
            try:
                from ultralytics import YOLO
                self.model = YOLO(self.model_path)
                self.demo_mode = False
                logger.success(f"✅ YOLOv11 model loaded from {self.model_path}")
            except Exception as e:
                logger.warning(f"⚠️  Failed to load YOLOv11: {e}. Running in demo mode.")
                self.demo_mode = True
        else:
            logger.info(
                f"📦 YOLOv11 weights not found at {self.model_path}. "
                f"Running in demo mode. Download from HuggingFace to enable real inference."
            )

    def detect(self, image_array: np.ndarray, image_width: int, image_height: int) -> list[dict]:
        """
        Detect food items in an image.

        Args:
            image_array: numpy array (H, W, C) in RGB format
            image_width: original image width in pixels
            image_height: original image height in pixels

        Returns:
            List of detections, each with:
              - food_name: str
              - confidence: float
              - bbox: [x1, y1, x2, y2] in pixel coordinates
              - bbox_normalized: [x1, y1, x2, y2] in 0-1 range
        """
        if self.demo_mode:
            return self._mock_detect(image_width, image_height)

        # ── REAL INFERENCE (when model is loaded) ──────────────────────────
        results = self.model(image_array, conf=self.confidence_threshold)
        detections = []
        for result in results:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                food_name = result.names[cls_id]
                confidence = float(box.conf[0])
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                detections.append({
                    "food_name": food_name,
                    "confidence": round(confidence, 3),
                    "bbox": [int(x1), int(y1), int(x2), int(y2)],
                    "bbox_normalized": [
                        round(x1 / image_width, 3), round(y1 / image_height, 3),
                        round(x2 / image_width, 3), round(y2 / image_height, 3)
                    ],
                })
        return detections

    def _mock_detect(self, image_width: int, image_height: int) -> list[dict]:
        """
        Generate realistic mock detections for demo/portfolio mode.

        Returns 2-5 plausible Indian food items with non-overlapping bounding boxes.
        """
        # Simulate processing time
        time.sleep(0.15)

        # Pick 2-5 random foods (weighted toward common meal combos)
        meal_combos = [
            ["basmati rice", "dal tadka", "mixed vegetable", "papad", "pickle"],
            ["basmati rice", "dal makhani", "paneer butter masala", "raita"],
            ["chicken biryani", "raita", "green salad"],
            ["roti", "butter chicken", "dal makhani", "curd"],
            ["idli", "sambar", "chutney", "filter coffee"],
            ["dosa", "sambar", "chutney"],
            ["roti", "chana masala", "curd", "green salad"],
            ["veg biryani", "raita", "papad"],
            ["basmati rice", "sambar", "rasam", "papad", "pickle"],
            ["roti", "aloo sabzi", "dal tadka", "curd"],
        ]
        chosen_combo = random.choice(meal_combos)

        # Divide image into grid cells for non-overlapping bboxes
        cols = min(len(chosen_combo), 3)
        rows = (len(chosen_combo) + cols - 1) // cols
        cell_w = image_width // cols
        cell_h = image_height // rows

        detections = []
        for i, food_name in enumerate(chosen_combo):
            if food_name not in DETECTABLE_FOODS:
                continue
            row = i // cols
            col = i % cols

            # Add some jitter within cell
            padding = 0.1
            x1 = int((col + padding) * cell_w + random.uniform(-5, 5))
            y1 = int((row + padding) * cell_h + random.uniform(-5, 5))
            x2 = int((col + 1 - padding) * cell_w + random.uniform(-5, 5))
            y2 = int((row + 1 - padding) * cell_h + random.uniform(-5, 5))

            # Clamp to image bounds
            x1 = max(0, min(x1, image_width - 1))
            y1 = max(0, min(y1, image_height - 1))
            x2 = max(x1 + 10, min(x2, image_width))
            y2 = max(y1 + 10, min(y2, image_height))

            confidence = round(random.uniform(*CONFIDENCE_RANGE), 3)

            detections.append({
                "food_name": food_name,
                "confidence": confidence,
                "bbox": [x1, y1, x2, y2],
                "bbox_normalized": [
                    round(x1 / image_width, 3), round(y1 / image_height, 3),
                    round(x2 / image_width, 3), round(y2 / image_height, 3)
                ],
                "demo": True,  # flag for transparency
            })

        return detections
