"""
NutriVision AI — ML Model: ConvNeXt Food Classifier

Disambiguates similar-looking foods (e.g., Veg Biryani vs Chicken Biryani).
Fine-tuned ConvNeXt-Base on 200 Indian food categories.

TODO: Replace mock with: timm.create_model('convnext_base', pretrained=False, num_classes=200)
"""

import os
import random
import time
from typing import Optional
import numpy as np
from loguru import logger

from models.detector import DETECTABLE_FOODS, CONFIDENCE_RANGE


# Similar food pairs that need classification disambiguation
SIMILAR_FOOD_GROUPS = {
    "biryani": ["chicken biryani", "veg biryani", "mutton biryani", "egg biryani"],
    "dal": ["dal tadka", "dal makhani", "moong dal", "masoor dal"],
    "paratha": ["aloo paratha", "paneer paratha", "mooli paratha", "paratha"],
    "dosa": ["dosa", "masala dosa", "rava dosa", "paneer dosa"],
    "curry": ["chicken curry", "mutton curry", "fish curry", "paneer curry"],
    "rice": ["basmati rice", "brown rice", "curd rice", "lemon rice", "pulao"],
}


class FoodClassifier:
    """
    ConvNeXt food classifier for Indian cuisine disambiguation.

    Architecture: ConvNeXt-Base → Global Avg Pool → FC(200) → Softmax
    Trained on: Food-101 + UECFOOD256 + custom Indian food dataset
    """

    def __init__(self):
        self.model = None
        self.model_path = os.getenv("CONVNEXT_MODEL_PATH", "weights/nutrivision_convnext.pt")
        self.class_names = DETECTABLE_FOODS
        self.demo_mode = True
        self._load_model()

    def _load_model(self):
        """Load ConvNeXt model from weights file."""
        if os.path.exists(self.model_path):
            try:
                import timm
                import torch
                self.model = timm.create_model(
                    "convnext_base",
                    pretrained=False,
                    num_classes=len(self.class_names)
                )
                state = torch.load(self.model_path, map_location="cpu")
                self.model.load_state_dict(state)
                self.model.eval()
                self.demo_mode = False
                logger.success(f"✅ ConvNeXt classifier loaded from {self.model_path}")
            except Exception as e:
                logger.warning(f"⚠️  Failed to load ConvNeXt: {e}. Running in demo mode.")
        else:
            logger.info("📦 ConvNeXt weights not found. Running in demo mode.")

    def classify(self, image_crop: np.ndarray, detected_food: str) -> dict:
        """
        Classify a food crop, potentially refining the YOLO detection label.

        Args:
            image_crop: Cropped image region (numpy array)
            detected_food: Initial food label from YOLOv11

        Returns:
            Dict with:
              - final_label: refined food name
              - confidence: float
              - top_5: list of (label, confidence) pairs
        """
        if self.demo_mode:
            return self._mock_classify(detected_food)

        # ── REAL INFERENCE ─────────────────────────────────────────────────
        import torch
        import torchvision.transforms as T

        transform = T.Compose([
            T.ToPILImage(),
            T.Resize((224, 224)),
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

        tensor = transform(image_crop).unsqueeze(0)
        with torch.no_grad():
            logits = self.model(tensor)
            probs = torch.softmax(logits, dim=1)[0]

        top5_idx = probs.argsort(descending=True)[:5].tolist()
        top5 = [(self.class_names[i], round(probs[i].item(), 4)) for i in top5_idx]

        return {
            "final_label": top5[0][0],
            "confidence": top5[0][1],
            "top_5": top5,
        }

    def _mock_classify(self, detected_food: str) -> dict:
        """Generate realistic mock classification results."""
        time.sleep(0.05)

        # Check if this food belongs to a group that needs disambiguation
        food_group = None
        for group_name, group_foods in SIMILAR_FOOD_GROUPS.items():
            if detected_food in group_foods:
                food_group = group_foods
                break

        if food_group:
            # Occasionally refine the label within the group
            final_label = detected_food
            confidence = round(random.uniform(0.75, 0.95), 3)
            alternatives = [f for f in food_group if f != detected_food]
            top5 = [(final_label, confidence)]
            remaining = 1.0 - confidence
            for alt in alternatives[:3]:
                score = round(remaining * random.uniform(0.2, 0.5), 3)
                remaining -= score
                top5.append((alt, score))
        else:
            confidence = round(random.uniform(0.85, 0.98), 3)
            top5 = [(detected_food, confidence)]
            # Add noise alternatives
            others = random.sample([f for f in DETECTABLE_FOODS if f != detected_food], k=4)
            remaining = 1.0 - confidence
            for other in others:
                score = round(remaining * random.uniform(0.1, 0.4), 3)
                remaining = max(0, remaining - score)
                top5.append((other, score))
            final_label = detected_food

        return {
            "final_label": final_label,
            "confidence": confidence,
            "top_5": sorted(top5, key=lambda x: x[1], reverse=True),
        }
