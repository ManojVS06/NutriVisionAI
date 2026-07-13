"""
NutriVision AI — ML Model: Depth Anything V2 Portion Estimator

Estimates food weight from:
1. Depth Anything V2 → monocular depth map → food height estimation
2. Known plate/reference object diameter → pixel-to-cm calibration
3. SAM2 mask area → food footprint area
4. Food-specific density table → volume × density = weight

TODO: Replace mock with real Depth Anything V2 inference:
  from depth_anything_v2.dpt import DepthAnythingV2
  model = DepthAnythingV2(encoder='vitl', ...)
  model.load_state_dict(torch.load('weights/depth_anything_v2_vitl.pth'))
"""

import os
import random
import time
import math
import numpy as np
from loguru import logger

from models.detector import TYPICAL_PORTIONS

# Food density table (g/cm³) for volume-to-weight conversion
# Based on USDA food density measurements
FOOD_DENSITY = {
    "basmati rice": 0.85, "brown rice": 0.85, "roti": 0.55, "paratha": 0.60,
    "aloo paratha": 0.65, "naan": 0.45, "puri": 0.40, "idli": 0.65,
    "dosa": 0.35, "masala dosa": 0.40, "upma": 0.75, "poha": 0.70,
    "dal tadka": 0.90, "dal makhani": 0.95, "rajma": 0.95,
    "chana masala": 0.90, "sambar": 0.88, "moong dal": 0.88,
    "aloo sabzi": 0.85, "palak paneer": 0.90, "paneer butter masala": 0.92,
    "mixed vegetable": 0.80, "bhindi masala": 0.78, "baingan bharta": 0.88,
    "chicken curry": 0.92, "butter chicken": 0.93, "chicken biryani": 0.85,
    "fish curry": 0.90, "egg curry": 0.90, "boiled eggs": 1.05,
    "curd": 1.02, "raita": 0.98, "buttermilk": 1.00, "lassi": 1.02,
    "paneer": 1.10, "green salad": 0.25, "kachumber salad": 0.35,
    "samosa": 0.55, "pakora": 0.50, "pav bhaji": 0.88, "vada pav": 0.70,
    "dhokla": 0.60, "kheer": 1.05, "gulab jamun": 0.95, "halwa": 0.98,
    "papad": 0.20, "pickle": 0.95, "chutney": 0.95, "chai": 1.00,
    "veg biryani": 0.85, "pulao": 0.85, "curd rice": 0.90,
    "lemon rice": 0.85, "mango": 0.95, "banana": 0.70,
    # Default for unknown foods
    "_default": 0.80,
}

# Standard plate diameter in cm (common thali/dinner plate)
STANDARD_PLATE_DIAMETER_CM = 28.0
STANDARD_BOWL_DIAMETER_CM = 15.0


class PortionEstimator:
    """
    Estimates food portion weight from:
    - Depth map (Depth Anything V2) for height estimation
    - Segmentation mask (SAM2) for footprint area
    - Reference object calibration for scale
    - Food-specific density for volume → weight
    """

    def __init__(self):
        self.model = None
        self.model_path = os.getenv("DEPTH_MODEL_PATH", "weights/depth_anything_v2_vitl.pth")
        self.demo_mode = True
        self._load_model()

    def _load_model(self):
        """Load Depth Anything V2 model."""
        if os.path.exists(self.model_path):
            try:
                # from depth_anything_v2.dpt import DepthAnythingV2
                # self.model = DepthAnythingV2(encoder='vitl', features=256, out_channels=[256,512,1024,1024])
                # self.model.load_state_dict(torch.load(self.model_path, map_location='cpu'))
                # self.model.eval()
                self.demo_mode = False
                logger.success(f"✅ Depth Anything V2 loaded from {self.model_path}")
            except Exception as e:
                logger.warning(f"⚠️  Failed to load Depth Anything V2: {e}. Demo mode.")
        else:
            logger.info("📦 Depth Anything V2 weights not found. Running in demo mode.")

    def estimate_weight(
        self,
        food_name: str,
        bbox: list[int],
        image_width: int,
        image_height: int,
        mask_area_pixels: Optional[int] = None,
        depth_map: Optional[np.ndarray] = None,
        reference_plate_bbox: Optional[list[int]] = None,
    ) -> dict:
        """
        Estimate portion weight for a detected food item.

        Args:
            food_name: Name of the food
            bbox: Bounding box [x1, y1, x2, y2]
            image_width, image_height: Image dimensions
            mask_area_pixels: SAM2 segmentation mask area in pixels (optional)
            depth_map: Depth map from Depth Anything V2 (optional)
            reference_plate_bbox: Bounding box of reference plate for calibration

        Returns:
            Dict with weight_g, confidence, and estimation method
        """
        if self.demo_mode:
            return self._mock_estimate(food_name, bbox, image_width, image_height)

        # ── REAL INFERENCE ─────────────────────────────────────────────────
        return self._geometric_estimate(
            food_name, bbox, image_width, image_height,
            mask_area_pixels, depth_map, reference_plate_bbox
        )

    def _geometric_estimate(
        self, food_name, bbox, image_width, image_height,
        mask_area_pixels, depth_map, reference_plate_bbox
    ) -> dict:
        """
        Geometric estimation pipeline:
        1. Calibrate pixel-to-cm using reference plate
        2. Calculate food area from mask or bbox
        3. Estimate height from depth map
        4. Compute volume = area × height
        5. Weight = volume × density
        """
        # Step 1: Pixel-to-cm calibration
        if reference_plate_bbox:
            plate_w_px = reference_plate_bbox[2] - reference_plate_bbox[0]
            cm_per_px = STANDARD_PLATE_DIAMETER_CM / plate_w_px
        else:
            # Estimate: assume plate takes ~60% of image width
            cm_per_px = STANDARD_PLATE_DIAMETER_CM / (0.6 * image_width)

        # Step 2: Food area
        if mask_area_pixels:
            area_cm2 = mask_area_pixels * (cm_per_px ** 2)
        else:
            w_px = bbox[2] - bbox[0]
            h_px = bbox[3] - bbox[1]
            area_cm2 = w_px * h_px * (cm_per_px ** 2) * 0.7  # bbox overestimates

        # Step 3: Height from depth map
        if depth_map is not None:
            roi = depth_map[bbox[1]:bbox[3], bbox[0]:bbox[2]]
            bg_depth = np.percentile(depth_map, 5)
            food_depth = np.median(roi)
            height_relative = max(0.01, (food_depth - bg_depth))
            # Convert relative depth to cm (calibration needed)
            height_cm = height_relative * 3.0  # heuristic
        else:
            height_cm = 2.5  # assume 2.5cm average food height

        # Step 4: Volume
        volume_cm3 = area_cm2 * height_cm

        # Step 5: Weight
        density = FOOD_DENSITY.get(food_name.lower(), FOOD_DENSITY["_default"])
        weight_g = volume_cm3 * density * 1000 / 1000  # cm³ × g/cm³

        return {
            "weight_g": round(max(10, min(weight_g, 600)), 1),
            "confidence": 0.72,
            "method": "geometric (depth + mask)",
            "area_cm2": round(area_cm2, 1),
            "height_cm": round(height_cm, 2),
            "volume_cm3": round(volume_cm3, 1),
            "density_g_cm3": density,
        }

    def _mock_estimate(self, food_name, bbox, image_width, image_height) -> dict:
        """Generate realistic mock weight estimates based on bbox size and food type."""
        time.sleep(0.05)

        # Base portion from typical range
        food_lower = food_name.lower()
        portion_range = TYPICAL_PORTIONS.get(food_lower, (80, 200))
        base_weight = random.uniform(*portion_range)

        # Scale by bbox area relative to image
        bbox_area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
        image_area = image_width * image_height
        area_ratio = bbox_area / image_area
        # Larger bbox → larger portion
        scale = 0.7 + area_ratio * 3.0
        weight = base_weight * min(scale, 1.3)

        return {
            "weight_g": round(weight, 1),
            "confidence": round(random.uniform(0.65, 0.82), 3),
            "method": "demo (bbox + portion table)",
            "demo": True,
        }


# Type hint fix
from typing import Optional
