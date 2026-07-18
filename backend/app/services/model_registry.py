"""
Phase 2: Model Registry — Singleton Loader for All Deep Learning Models

Handles:
  - Lazy loading (models loaded only on first use)
  - Persistent in-memory caching between requests (no per-request reload)
  - Device management (CUDA if available, CPU fallback)
  - VRAM budget tracking
  - Graceful degradation if a model fails to load

VRAM budget on RTX 3050 6GB:
  Grounding DINO (Swin-T)  ~1.5 GB
  CLIP (ViT-B/32)          ~0.4 GB
  SAM2 (Tiny)              ~0.5 GB
  Depth Anything V2 (ViT-S)~0.3 GB
  Total                    ~2.7 GB  (safe within 6GB)
"""

from __future__ import annotations

import os
import threading
import time
from typing import Optional, Any

# ─── Device selection ─────────────────────────────────────────────────────────
def _get_device():
    try:
        import torch
        if torch.cuda.is_available():
            dev = "cuda"
            gpu = torch.cuda.get_device_name(0)
            vram = torch.cuda.get_device_properties(0).total_memory / 1e9
            print(f"[ModelRegistry] GPU: {gpu} | VRAM: {vram:.1f} GB")
        else:
            dev = "cpu"
            print("[ModelRegistry] No GPU detected — using CPU (slower inference)")
        return dev
    except ImportError:
        print("[ModelRegistry] PyTorch not installed — all models will be unavailable")
        return "cpu"

DEVICE = _get_device()

# ─── Singleton registry ───────────────────────────────────────────────────────
_registry: dict[str, Any] = {}
_lock = threading.Lock()
_load_times: dict[str, float] = {}


class _RegistryView:
    """Thin wrapper so /health can iterate loaded models."""
    @property
    def loaded_models(self) -> dict:
        return {k: v for k, v in _registry.items() if v is not None}


_registry_view = _RegistryView()


def get_registry() -> _RegistryView:
    """Return a view of the model registry for status endpoints."""
    return _registry_view


def _register(name: str, loader_fn) -> Optional[Any]:
    """
    Thread-safe singleton loader. Calls loader_fn() once, caches result.

    Uses a non-blocking acquire: if the model is already being loaded by
    the warmup thread, returns None immediately so the request pipeline
    can fall through to its OpenCV/API fallback without blocking.
    """
    # Fast path: already loaded (or cached as failed)
    if name in _registry:
        return _registry[name]

    # Try to acquire without blocking — if loading is in progress, skip
    acquired = _lock.acquire(blocking=False)
    if not acquired:
        print(f"[ModelRegistry] {name} is being loaded by another thread — skipping for now")
        return None

    try:
        # Double-check after lock acquired
        if name in _registry:
            return _registry[name]

        print(f"[ModelRegistry] Loading {name}...")
        t0 = time.time()
        try:
            model = loader_fn()
            elapsed = time.time() - t0
            _registry[name] = model
            _load_times[name] = elapsed
            print(f"[ModelRegistry] {name} ready in {elapsed:.1f}s")
            return model
        except Exception as e:
            print(f"[ModelRegistry] FAILED to load {name}: {e}")
            _registry[name] = None      # Cache the failure too
            return None
    finally:
        _lock.release()



# ─── Grounding DINO ───────────────────────────────────────────────────────────
GDINO_MODEL_ID = "IDEA-Research/grounding-dino-tiny"

def _load_grounding_dino():
    from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection
    import torch
    # Try offline (cached) first; fall back to online download if cache miss
    try:
        processor = AutoProcessor.from_pretrained(GDINO_MODEL_ID, local_files_only=True)
        model = AutoModelForZeroShotObjectDetection.from_pretrained(GDINO_MODEL_ID, local_files_only=True)
    except Exception:
        print(f"[ModelRegistry] Grounding DINO not cached — downloading from HuggingFace...")
        processor = AutoProcessor.from_pretrained(GDINO_MODEL_ID)
        model = AutoModelForZeroShotObjectDetection.from_pretrained(GDINO_MODEL_ID)
    model = model.to(DEVICE)
    model.eval()
    return {"model": model, "processor": processor}


def get_grounding_dino() -> Optional[dict]:
    """Returns {'model': ..., 'processor': ...} or None if unavailable."""
    return _register("grounding_dino", _load_grounding_dino)


# ─── CLIP (open_clip ViT-B/32) ────────────────────────────────────────────────
CLIP_MODEL_NAME = "ViT-B-32"
CLIP_PRETRAINED  = "openai"

def _load_clip():
    import open_clip
    import torch
    model, _, preprocess = open_clip.create_model_and_transforms(
        CLIP_MODEL_NAME, pretrained=CLIP_PRETRAINED
    )
    tokenizer = open_clip.get_tokenizer(CLIP_MODEL_NAME)
    model = model.to(DEVICE)
    model.eval()
    return {"model": model, "preprocess": preprocess, "tokenizer": tokenizer}


def get_clip() -> Optional[dict]:
    """Returns {'model': ..., 'preprocess': ..., 'tokenizer': ...} or None."""
    return _register("clip", _load_clip)


# ─── SAM2 (Tiny) ─────────────────────────────────────────────────────────────
SAM2_MODEL_ID = "facebook/sam2-hiera-tiny"

def _load_sam2():
    from transformers import Sam2Processor, Sam2Model
    import torch
    try:
        processor = Sam2Processor.from_pretrained(SAM2_MODEL_ID, local_files_only=True)
        model = Sam2Model.from_pretrained(SAM2_MODEL_ID, local_files_only=True)
    except Exception:
        print(f"[ModelRegistry] SAM2 not cached — downloading from HuggingFace...")
        processor = Sam2Processor.from_pretrained(SAM2_MODEL_ID)
        model = Sam2Model.from_pretrained(SAM2_MODEL_ID)
    model = model.to(DEVICE)
    model.eval()
    return {"model": model, "processor": processor}


def get_sam2() -> Optional[dict]:
    """Returns {'model': ..., 'processor': ...} or None if unavailable."""
    return _register("sam2", _load_sam2)


# ─── Depth Anything V2 (ViT-S) ───────────────────────────────────────────────
DEPTH_MODEL_ID = "depth-anything/Depth-Anything-V2-Small-hf"

def _load_depth_anything():
    from transformers import AutoImageProcessor, AutoModelForDepthEstimation
    import torch
    try:
        processor = AutoImageProcessor.from_pretrained(DEPTH_MODEL_ID, local_files_only=True)
        model = AutoModelForDepthEstimation.from_pretrained(DEPTH_MODEL_ID, local_files_only=True)
    except Exception:
        print(f"[ModelRegistry] Depth Anything not cached — downloading from HuggingFace...")
        processor = AutoImageProcessor.from_pretrained(DEPTH_MODEL_ID)
        model = AutoModelForDepthEstimation.from_pretrained(DEPTH_MODEL_ID)
    model = model.to(DEVICE)
    model.eval()
    return {"model": model, "processor": processor}


def get_depth_anything() -> Optional[dict]:
    """Returns {'model': ..., 'processor': ...} or None if unavailable."""
    return _register("depth_anything", _load_depth_anything)


# ─── Status helpers ───────────────────────────────────────────────────────────
def get_model_status() -> dict:
    """
    Returns current load status of all models.
    Useful for /api/system/models health endpoint.
    """
    models = ["grounding_dino", "clip", "sam2", "depth_anything"]
    status = {}
    for name in models:
        if name not in _registry:
            status[name] = "not_loaded"
        elif _registry[name] is None:
            status[name] = "failed"
        else:
            status[name] = f"loaded ({_load_times.get(name, 0):.1f}s)"
    status["device"] = DEVICE
    return status


def preload_all():
    """
    Eagerly load all models at startup.
    Call from app startup to warm up models before first request.
    """
    print("[ModelRegistry] Preloading all models...")
    get_grounding_dino()
    get_clip()
    get_sam2()
    get_depth_anything()
    print(f"[ModelRegistry] Status: {get_model_status()}")
