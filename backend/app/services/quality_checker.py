"""
Phase 1: Image Quality Assessment
Validates image quality before any expensive model inference.
Rejects blurry, dark, overexposed, or plate-absent images.
"""

import cv2
import numpy as np
from dataclasses import dataclass, field
from typing import List


@dataclass
class QualityReport:
    is_acceptable: bool
    quality_score: float           # 0-100
    blur_variance: float
    avg_brightness: float
    plate_detected: bool
    issues: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "is_acceptable": self.is_acceptable,
            "quality_score": round(self.quality_score, 1),
            "blur_variance": round(self.blur_variance, 2),
            "avg_brightness": round(self.avg_brightness, 1),
            "plate_detected": self.plate_detected,
            "issues": self.issues
        }


# ─── Tuneable thresholds ────────────────────────────────────────────────────
BLUR_THRESHOLD        = 80.0   # Laplacian variance below this → blurry
DARK_THRESHOLD        = 40.0   # Mean luminance below this → too dark
BRIGHT_THRESHOLD      = 220.0  # Mean luminance above this → overexposed
MIN_QUALITY_SCORE     = 30.0   # Any score below this → hard reject
# ────────────────────────────────────────────────────────────────────────────


def _check_blur(gray: np.ndarray) -> tuple[float, bool, str | None]:
    """
    Laplacian variance method. High variance = sharp image.
    Returns (variance, is_ok, issue_message_or_None).
    """
    variance = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    is_ok = variance >= BLUR_THRESHOLD
    msg = None if is_ok else f"Image is too blurry (sharpness score: {variance:.1f}, need ≥ {BLUR_THRESHOLD})"
    return variance, is_ok, msg


def _check_brightness(gray: np.ndarray) -> tuple[float, bool, str | None]:
    """
    Mean pixel intensity in grayscale.
    Returns (mean_brightness, is_ok, issue_message_or_None).
    """
    mean_val = float(np.mean(gray))
    if mean_val < DARK_THRESHOLD:
        return mean_val, False, f"Image is too dark (brightness: {mean_val:.1f}, need ≥ {DARK_THRESHOLD})"
    if mean_val > BRIGHT_THRESHOLD:
        return mean_val, False, f"Image is overexposed (brightness: {mean_val:.1f}, need ≤ {BRIGHT_THRESHOLD})"
    return mean_val, True, None


def _check_plate(image: np.ndarray) -> tuple[bool, str | None]:
    """
    Attempts to detect a circular plate or large rectangular tray using:
    1. Hough Circle Transform (for round plates)
    2. Large contour detection (for rectangular trays / flat plates)
    Returns (plate_found, issue_message_or_None).
    """
    h, w = image.shape[:2]
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (9, 9), 2)

    # 1. Hough Circles — look for a circle taking up ≥ 25% of the image
    circles = cv2.HoughCircles(
        blurred, cv2.HOUGH_GRADIENT,
        dp=1.2, minDist=min(h, w) // 2,
        param1=80, param2=35,
        minRadius=min(h, w) // 5,
        maxRadius=int(min(h, w) * 0.65)
    )
    if circles is not None:
        return True, None

    # 2. Large contour fallback — look for any contour covering ≥ 20% of image
    edges = cv2.Canny(blurred, 30, 100)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    dilated = cv2.dilate(edges, kernel, iterations=2)
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > (h * w * 0.20):   # ≥ 20% of image
            return True, None

    return False, "No plate or food tray detected. Please ensure the plate is visible and centred."


def _check_occlusion(gray: np.ndarray) -> tuple[bool, str | None]:
    """
    Simple occlusion heuristic: check whether the central 30% × 30% 
    region is extremely dark (hand/object blocking the view).
    """
    h, w = gray.shape
    cy, cx = h // 2, w // 2
    r = min(h, w) // 6
    center_patch = gray[cy - r: cy + r, cx - r: cx + r]
    mean_center = float(np.mean(center_patch))
    if mean_center < 25:
        return False, "Central area appears occluded. Please remove obstructions."
    return True, None


def _score(blur_ok: bool, bright_ok: bool, plate_ok: bool, occlusion_ok: bool,
           blur_var: float, brightness: float) -> float:
    """
    Combine checks into a 0-100 score.
    Base 40 pts for fundamentals, 60 pts from continuous metrics.
    """
    score = 0.0

    # Binary contributions (each 10 pts)
    if plate_ok:    score += 15
    if occlusion_ok: score += 10

    # Continuous blur contribution (0-35 pts)
    # Maps variance 0→800 → 0→35 pts, clamped
    blur_score = min(35.0, (blur_var / 800.0) * 35.0)
    score += blur_score

    # Continuous brightness contribution (0-40 pts)
    # Ideal brightness: 100-180. Score peaks at 140.
    ideal = 140.0
    deviation = abs(brightness - ideal)
    bright_score = max(0.0, 40.0 - (deviation / ideal) * 40.0)
    score += bright_score

    return min(100.0, score)


def assess_image_quality(image_path: str) -> QualityReport:
    """
    Main entry point. Loads the image from disk and runs all quality checks.

    Args:
        image_path: Absolute path to the uploaded image.

    Returns:
        QualityReport dataclass with all check results.
    """
    image = cv2.imread(image_path)
    if image is None:
        return QualityReport(
            is_acceptable=False,
            quality_score=0.0,
            blur_variance=0.0,
            avg_brightness=0.0,
            plate_detected=False,
            issues=["Could not load image file. It may be corrupted or unsupported."]
        )

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    blur_var,   blur_ok,       blur_msg  = _check_blur(gray)
    brightness, bright_ok,     bright_msg = _check_brightness(gray)
    plate_ok,   plate_msg                = _check_plate(image)
    occlusion_ok, occlusion_msg          = _check_occlusion(gray)

    issues = [m for m in [blur_msg, bright_msg, plate_msg, occlusion_msg] if m]

    quality_score = _score(blur_ok, bright_ok, plate_ok, occlusion_ok, blur_var, brightness)

    # A result is acceptable if score ≥ threshold AND no hard failures
    # We treat blur and brightness as hard failures; plate + occlusion as warnings
    is_acceptable = (
        blur_ok and bright_ok and quality_score >= MIN_QUALITY_SCORE
    )

    report = QualityReport(
        is_acceptable=is_acceptable,
        quality_score=quality_score,
        blur_variance=blur_var,
        avg_brightness=brightness,
        plate_detected=plate_ok,
        issues=issues
    )

    print(f"[QualityChecker] Score={quality_score:.1f} | Blur={blur_var:.1f} | "
          f"Brightness={brightness:.1f} | Plate={plate_ok} | "
          f"Acceptable={is_acceptable}")
    if issues:
        for issue in issues:
            print(f"[QualityChecker] ⚠ {issue}")

    return report
