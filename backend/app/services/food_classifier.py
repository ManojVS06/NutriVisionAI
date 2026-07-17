"""
Phase 2: CLIP Zero-Shot Food Classifier

After Grounding DINO detects food regions with broad category labels
(e.g. "curry", "bread", "rice"), CLIP refines the label to the exact
IFCT database entry (e.g. "Butter Chicken", "Roti / Chapati", "Jeera Rice").

Model: ViT-B/32 via open_clip (OpenAI pretrained weights)
VRAM:  ~400 MB
Speed: ~0.2s per crop on RTX 3050

Pipeline:
  1. Crop the food region from the image (with padding)
  2. Encode it with CLIP image encoder
  3. Compute cosine similarity against IFCT food name text embeddings
  4. Return top-1 match with confidence score

Text embeddings for all 155 IFCT foods are pre-computed and cached
at module load time — no per-request text encoding needed.
"""

from __future__ import annotations

import numpy as np
from PIL import Image
from typing import Optional
import math

from app.services.model_registry import get_clip, DEVICE
from app.data.ifct_database import IFCT_DATABASE, ALL_FOOD_NAMES

# ─── CLIP confidence thresholds ───────────────────────────────────────────────
CLIP_HIGH_CONF = 0.80   # Accept without further validation
CLIP_MED_CONF  = 0.50   # Accept with warning
CLIP_LOW_CONF  = 0.50   # Below this → escalate to Gemini

# ─── Text prompt templates ────────────────────────────────────────────────────
# CLIP works best with descriptive prompts rather than bare food names
PROMPT_TEMPLATES = [
    "a photo of {}",
    "a plate of {}",
    "a bowl of {}",
    "Indian food called {}",
    "{} served on a plate",
]

# ─── Pre-computed text embedding cache ───────────────────────────────────────
# Populated lazily on first call to classify_food()
_text_embeddings: Optional[np.ndarray] = None  # shape: (N_foods, D)
_food_names_indexed: list[str] = []


def _ensure_text_embeddings():
    """
    Pre-compute and cache CLIP text embeddings for all 155 IFCT foods.
    Called once and then cached for the session lifetime.
    """
    global _text_embeddings, _food_names_indexed

    if _text_embeddings is not None:
        return  # Already computed

    clip_bundle = get_clip()
    if clip_bundle is None:
        return  # CLIP unavailable

    import torch
    model     = clip_bundle["model"]
    tokenizer = clip_bundle["tokenizer"]

    print(f"[FoodClassifier] Pre-computing CLIP embeddings for {len(ALL_FOOD_NAMES)} foods...")

    all_embeddings = []
    food_names_ordered = []

    with torch.no_grad():
        for food_name in ALL_FOOD_NAMES:
            # Encode multiple prompt templates and average them
            prompts = [tmpl.format(food_name) for tmpl in PROMPT_TEMPLATES]
            tokens = tokenizer(prompts).to(DEVICE)
            text_feats = model.encode_text(tokens)   # (N_templates, D)
            text_feats = text_feats / text_feats.norm(dim=-1, keepdim=True)
            avg_feat = text_feats.mean(dim=0)        # (D,)
            avg_feat = avg_feat / avg_feat.norm()
            all_embeddings.append(avg_feat.cpu().numpy())
            food_names_ordered.append(food_name)

    _text_embeddings = np.stack(all_embeddings, axis=0)  # (N, D)
    _food_names_indexed = food_names_ordered
    print(f"[FoodClassifier] CLIP text embeddings cached: {_text_embeddings.shape}")


def classify_food_crop(
    crop_bgr: np.ndarray,
    top_k: int = 3,
    hint: Optional[str] = None
) -> list[dict]:
    """
    Classify a single food crop using CLIP zero-shot matching against
    all 155 IFCT food names.

    Args:
        crop_bgr:  Cropped food region as BGR numpy array (from OpenCV).
        top_k:     Number of top candidates to return.
        hint:      Optional Grounding DINO label to boost candidates
                   matching the same category (e.g. "curry" boosts
                   all curry-type foods).

    Returns:
        List of top_k dicts, each with:
          {
            name: str,              # IFCT canonical food name
            score: float,           # CLIP cosine similarity (0-1)
            category: str,          # IFCT food group
            needs_gemini: bool      # True if confidence too low
          }
        Returns empty list if CLIP unavailable.
    """
    clip_bundle = get_clip()
    if clip_bundle is None:
        print("[FoodClassifier] CLIP unavailable — skipping classification")
        return []

    # Ensure text embeddings are cached
    _ensure_text_embeddings()

    if _text_embeddings is None:
        return []

    try:
        import torch

        model     = clip_bundle["model"]
        preprocess = clip_bundle["preprocess"]

        # Convert BGR → RGB PIL image
        crop_rgb = crop_bgr[:, :, ::-1]
        pil_crop = Image.fromarray(crop_rgb)

        # Preprocess and encode image
        img_tensor = preprocess(pil_crop).unsqueeze(0).to(DEVICE)

        with torch.no_grad():
            img_feat = model.encode_image(img_tensor)  # (1, D)
            img_feat = img_feat / img_feat.norm(dim=-1, keepdim=True)

        img_np = img_feat.cpu().numpy()  # (1, D)

        # Cosine similarity against all food name embeddings
        similarities = (_text_embeddings @ img_np.T).squeeze(1)  # (N,)

        # Apply category hint boost (+0.05 to foods in same category)
        if hint:
            hint_lower = hint.lower()
            for i, food_name in enumerate(_food_names_indexed):
                food_info = IFCT_DATABASE.get(food_name, {})
                cat = food_info.get("category", "").lower()
                if any(h in food_name.lower() or h in cat
                       for h in hint_lower.split()):
                    similarities[i] = min(1.0, similarities[i] + 0.05)

        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            name = _food_names_indexed[idx]
            score = float(similarities[idx])
            food_info = IFCT_DATABASE.get(name, {})
            results.append({
                "name":         name,
                "score":        round(score, 4),
                "category":     food_info.get("category", "Unknown"),
                "needs_gemini": score < CLIP_LOW_CONF
            })

        print(f"[FoodClassifier] CLIP top-3 predictions:")
        for r in results:
            flag = " [needs Gemini]" if r["needs_gemini"] else ""
            print(f"  '{r['name']}' score={r['score']:.4f} [{r['category']}]{flag}")

        return results

    except Exception as e:
        print(f"[FoodClassifier] CLIP inference error: {e}")
        return []


def classify_food_crops_batch(
    crops_bgr: list[np.ndarray],
    hints: Optional[list[str]] = None
) -> list[list[dict]]:
    """
    Batch CLIP classification for multiple food crops.
    More efficient than calling classify_food_crop() in a loop
    because image encoding is batched.

    Args:
        crops_bgr: List of BGR numpy arrays.
        hints:     Optional list of Grounding DINO labels (same length).

    Returns:
        List of top-3 prediction lists, one per crop.
    """
    clip_bundle = get_clip()
    if clip_bundle is None:
        return [[] for _ in crops_bgr]

    _ensure_text_embeddings()

    if _text_embeddings is None or not crops_bgr:
        return [[] for _ in crops_bgr]

    try:
        import torch

        model      = clip_bundle["model"]
        preprocess = clip_bundle["preprocess"]

        # Encode all crops as a batch
        tensors = []
        for crop in crops_bgr:
            crop_rgb = crop[:, :, ::-1]
            pil_crop = Image.fromarray(crop_rgb)
            tensors.append(preprocess(pil_crop))

        batch = torch.stack(tensors).to(DEVICE)   # (B, C, H, W)

        with torch.no_grad():
            img_feats = model.encode_image(batch)   # (B, D)
            img_feats = img_feats / img_feats.norm(dim=-1, keepdim=True)

        img_np = img_feats.cpu().numpy()           # (B, D)
        # similarities: (B, N_foods)
        similarities = img_np @ _text_embeddings.T

        all_results = []
        for b_idx, sims in enumerate(similarities):
            hint = hints[b_idx] if hints and b_idx < len(hints) else None

            # Apply hint boost
            if hint:
                hint_lower = hint.lower()
                for i, food_name in enumerate(_food_names_indexed):
                    food_info = IFCT_DATABASE.get(food_name, {})
                    cat = food_info.get("category", "").lower()
                    if any(h in food_name.lower() or h in cat
                           for h in hint_lower.split()):
                        sims[i] = min(1.0, sims[i] + 0.05)

            top_indices = np.argsort(sims)[::-1][:3]
            results = []
            for idx in top_indices:
                name = _food_names_indexed[idx]
                score = float(sims[idx])
                food_info = IFCT_DATABASE.get(name, {})
                results.append({
                    "name":         name,
                    "score":        round(score, 4),
                    "category":     food_info.get("category", "Unknown"),
                    "needs_gemini": score < CLIP_LOW_CONF
                })
            all_results.append(results)

        return all_results

    except Exception as e:
        print(f"[FoodClassifier] Batch CLIP inference error: {e}")
        return [[] for _ in crops_bgr]
