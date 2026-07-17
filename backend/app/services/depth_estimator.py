"""
Phase 3: Depth Anything V2 — Monocular Depth Estimation for Portion Sizing

Replaces the simplistic OpenCV-based depth approximation with a real
neural depth estimator that produces metric-scale depth maps.

Model: depth-anything/Depth-Anything-V2-Small-hf (ViT-S backbone)
VRAM:  ~300 MB
Speed: ~0.5s per image on RTX 3050
Output: Relative depth map (0=nearest, 1=farthest) or metric depth

Pipeline role:
  Grounding DINO → CLIP → [Depth Anything V2] → Portion Estimation

Depth → Volume → Weight:
  1. Get depth map from Depth Anything V2
  2. For each detected bbox, compute:
       - Apparent area in pixels
       - Mean depth relative to plate rim (reference plane)
       - Estimate volumetric height above the plate
  3. volume_cm3 = apparent_area_cm2 × height_cm
  4. weight_g   = volume_cm3 × food_density (from IFCT)
"""

from __future__ import annotations

import cv2
import numpy as np
from PIL import Image
from typing import Optional

from app.services.model_registry import get_depth_anything, DEVICE

# ─── Physical constants ───────────────────────────────────────────────────────
# Standard plate reference: typical Indian dinner plate = 27 cm diameter
PLATE_DIAMETER_CM  = 27.0

# Approximate camera-to-plate distance (used for depth calibration)
# For top-down meal photos, typically ~40-60cm
TYPICAL_CAMERA_DISTANCE_CM = 50.0

# Maximum sensible food height (a tall samosa ≈ 5 cm)
MAX_FOOD_HEIGHT_CM = 6.0
MIN_FOOD_HEIGHT_CM = 0.3


def estimate_depth_map(image_path: str) -> Optional[np.ndarray]:
    """
    Runs Depth Anything V2 on the full image and returns a normalized
    depth map as a float32 numpy array in range [0.0, 1.0].
    0.0 = closest (near), 1.0 = farthest (background).

    Args:
        image_path: Path to the uploaded image.

    Returns:
        Depth map (H, W) float32, or None if model unavailable.
    """
    depth_bundle = get_depth_anything()

    if depth_bundle is None:
        print("[DepthEstimator] Depth Anything V2 unavailable — using fallback")
        return None

    try:
        import torch

        model     = depth_bundle["model"]
        processor = depth_bundle["processor"]

        pil_image = Image.open(image_path).convert("RGB")
        orig_w, orig_h = pil_image.size

        # Preprocess
        inputs = processor(images=pil_image, return_tensors="pt").to(DEVICE)

        # Inference
        with torch.no_grad():
            outputs = model(**inputs)
            depth_raw = outputs.predicted_depth  # (1, H', W')

        # Resize back to original image dimensions
        depth_np = depth_raw.squeeze(0).cpu().numpy()  # (H', W')
        depth_resized = cv2.resize(
            depth_np, (orig_w, orig_h), interpolation=cv2.INTER_LINEAR
        )

        # Normalize to [0, 1] — closer objects = smaller depth value
        d_min, d_max = depth_resized.min(), depth_resized.max()
        if d_max - d_min < 1e-6:
            return np.zeros_like(depth_resized, dtype=np.float32)

        depth_norm = (depth_resized - d_min) / (d_max - d_min)
        depth_norm = depth_norm.astype(np.float32)

        print(f"[DepthEstimator] Depth map: {orig_w}x{orig_h} | "
              f"min={d_min:.2f} max={d_max:.2f}")
        return depth_norm

    except Exception as e:
        print(f"[DepthEstimator] Depth Anything V2 error: {e}")
        return None


def estimate_volume_from_depth(
    depth_map: np.ndarray,
    bbox_px: list[int],
    image_shape: tuple[int, int],
    plate_diameter_pixels: Optional[float] = None
) -> float:
    """
    Estimates the volume of a food item in cm³ using depth map analysis.

    Strategy:
    1. Use plate rim pixels as the "zero height" reference plane
       (background depth ≈ depth of the plate rim)
    2. Food pixels that are CLOSER than the plate = height above plate
    3. Compute: height_cm = depth_delta × scale_factor
    4. volume = apparent_area_cm2 × mean_height_cm × fill_factor

    Args:
        depth_map:             Normalized depth map (H, W) float32.
        bbox_px:               [x1, y1, x2, y2] food region in pixels.
        image_shape:           (height, width) of the original image.
        plate_diameter_pixels: Detected plate diameter in pixels.
                               Used to calibrate cm/pixel scale.
    Returns:
        Estimated volume in cm³.
    """
    img_h, img_w = image_shape[:2]
    x1, y1, x2, y2 = bbox_px
    x1 = max(0, x1); y1 = max(0, y1)
    x2 = min(img_w, x2); y2 = min(img_h, y2)

    if x2 <= x1 or y2 <= y1:
        return 0.0

    # ── cm/pixel scale factor ──────────────────────────────────────────────
    if plate_diameter_pixels and plate_diameter_pixels > 0:
        cm_per_pixel = PLATE_DIAMETER_CM / plate_diameter_pixels
    else:
        # Fallback: assume plate takes ~60% of image width
        assumed_plate_px = img_w * 0.60
        cm_per_pixel = PLATE_DIAMETER_CM / assumed_plate_px

    # ── Reference depth: median of image border pixels (outside food zone) ─
    border = np.concatenate([
        depth_map[0, :],           # top row
        depth_map[-1, :],          # bottom row
        depth_map[:, 0],           # left col
        depth_map[:, -1],          # right col
    ])
    ref_depth = float(np.median(border))  # ≈ plate/background depth

    # ── Food region depth ──────────────────────────────────────────────────
    food_region = depth_map[y1:y2, x1:x2]  # (h_box, w_box)
    food_median_depth = float(np.median(food_region))

    # Depth CLOSER to camera = smaller normalized value
    # delta > 0 means food is closer (higher) than reference
    depth_delta = ref_depth - food_median_depth  # in [0, 1] normalized units

    # ── Convert depth delta to cm ──────────────────────────────────────────
    # Normalized depth range maps to TYPICAL_CAMERA_DISTANCE_CM depth range
    depth_range_cm = TYPICAL_CAMERA_DISTANCE_CM * 0.30  # ~15 cm depth range
    height_cm = depth_delta * depth_range_cm
    height_cm = max(MIN_FOOD_HEIGHT_CM, min(height_cm, MAX_FOOD_HEIGHT_CM))

    # ── Compute apparent area in cm² ────────────────────────────────────────
    box_w_cm = (x2 - x1) * cm_per_pixel
    box_h_cm = (y2 - y1) * cm_per_pixel
    apparent_area_cm2 = box_w_cm * box_h_cm

    # Fill factor: food doesn't fill the entire bounding box
    # Approximate as circular/elliptical filling (π/4 ≈ 0.785)
    fill_factor = 0.75
    volume_cm3 = apparent_area_cm2 * height_cm * fill_factor

    print(f"[DepthEstimator] bbox={bbox_px} | height={height_cm:.2f}cm | "
          f"area={apparent_area_cm2:.1f}cm² | volume={volume_cm3:.1f}cm³")

    return round(volume_cm3, 2)


def generate_depth_colormap(depth_map: np.ndarray) -> np.ndarray:
    """
    Converts a normalized depth map to a colorized BGR image
    using the INFERNO colormap (dark=close, bright=far).

    Args:
        depth_map: (H, W) float32 normalized [0, 1].

    Returns:
        Colorized BGR depth image (H, W, 3) uint8.
    """
    depth_uint8 = (depth_map * 255).astype(np.uint8)
    return cv2.applyColorMap(depth_uint8, cv2.COLORMAP_INFERNO)


def fallback_depth_estimate(
    bbox_px: list[int],
    image_shape: tuple[int, int],
    plate_diameter_pixels: Optional[float] = None
) -> float:
    """
    Geometry-based volume estimate when Depth Anything V2 is unavailable.
    Uses bounding box area + empirical height lookup.

    Returns estimated volume in cm³.
    """
    img_h, img_w = image_shape[:2]
    x1, y1, x2, y2 = bbox_px

    if plate_diameter_pixels and plate_diameter_pixels > 0:
        cm_per_pixel = PLATE_DIAMETER_CM / plate_diameter_pixels
    else:
        cm_per_pixel = PLATE_DIAMETER_CM / (img_w * 0.60)

    box_w_cm = (x2 - x1) * cm_per_pixel
    box_h_cm = (y2 - y1) * cm_per_pixel
    apparent_area_cm2 = box_w_cm * box_h_cm

    # Empirical average food height for Indian dishes: ~2.5 cm
    avg_height_cm = 2.5
    fill_factor   = 0.75
    volume_cm3 = apparent_area_cm2 * avg_height_cm * fill_factor

    return round(volume_cm3, 2)
