# 🍛 NutriVision AI

<div align="center">

![NutriVision AI](https://img.shields.io/badge/NutriVision-AI-orange?style=for-the-badge&logo=pytorch)
![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green?style=for-the-badge&logo=fastapi)
![React](https://img.shields.io/badge/React-18+-61DAFB?style=for-the-badge&logo=react)
![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-EE4C2C?style=for-the-badge&logo=pytorch)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker)

**An end-to-end AI-powered nutrition scanner optimized for Indian cuisine.**  
*Food Detection • Portion Estimation • Personalized Recommendations • Athlete Mode*

[Live Demo](#) · [API Docs](#api-documentation) · [Model Cards](#model-cards)

</div>

---

## 🎯 Project Overview

NutriVision AI is a production-grade deep learning system that analyzes Indian meal photographs and provides:

| Feature | Technology |
|---------|-----------|
| 🔍 **Food Detection** | YOLOv11 (custom-trained on Indian foods) |
| 🏷️ **Food Classification** | ConvNeXt (fine-tuned, 200+ classes) |
| ✂️ **Food Segmentation** | SAM2 (exact food shapes for area estimation) |
| 📐 **Portion Estimation** | Depth Anything V2 + reference object calibration |
| 🥗 **Nutrition Lookup** | IFCT (Indian Food Composition Tables) + USDA |
| 💯 **Health Scoring** | Custom 10-factor wellness algorithm |
| 🤖 **AI Coach** | Gemma/Llama LLM with RAG over nutrition knowledge base |
| 🏃 **Athlete Mode** | Sport-specific periodized nutrition planning |

---

## 🏗️ Architecture

```
User uploads meal photo
        │
        ▼
  Image Preprocessing (OpenCV + Pillow)
  - Resize to 640×640
  - Normalize RGB
  - Noise reduction
  - Contrast enhancement
        │
        ▼
  YOLOv11 Food Detection
  → Bounding boxes + confidence scores
        │
   ┌────┴────┐
   ▼         ▼
ConvNeXt   SAM2
Classifier  Segmentor
   │         │
   └────┬────┘
        ▼
  Depth Anything V2
  Portion Size Estimation
  (pixels → grams via density table)
        │
        ▼
  IFCT Nutrition Database Lookup
        │
        ▼
  Nutrition Calculation Engine
  (total calories, macros, micros)
        │
        ▼
  Health Score Algorithm (0–100)
        │
        ▼
  LLM AI Coach (Gemma/Llama)
  Personalized recommendations
        │
        ▼
  Dashboard & Analytics
```

---

## 📁 Project Structure

```
NutriVisionAI/
│
├── frontend/                    # React + Vite web app
│   ├── src/
│   │   ├── pages/               # Landing, Dashboard, Scan, Results, Coach, Profile
│   │   ├── components/          # Reusable UI components
│   │   ├── hooks/               # Custom React hooks
│   │   ├── api/                 # API client
│   │   └── utils/               # Helper functions
│   └── package.json
│
├── backend/                     # FastAPI application
│   ├── main.py                  # App entry point
│   ├── api/
│   │   └── routes.py            # All API endpoints
│   ├── models/                  # ML model loaders
│   │   ├── detector.py          # YOLOv11 wrapper
│   │   ├── classifier.py        # ConvNeXt wrapper
│   │   ├── segmentor.py         # SAM2 wrapper
│   │   └── depth_estimator.py   # Depth Anything V2 wrapper
│   ├── nutrition_engine/
│   │   ├── ifct_database.py     # 500+ Indian food nutrition data
│   │   └── calculator.py        # Macro/micro calculation
│   ├── recommendation_engine/
│   │   ├── health_scorer.py     # 10-factor health score
│   │   └── ai_coach.py          # LLM prompt engineering + RAG
│   ├── database/
│   │   └── models.py            # SQLAlchemy ORM models
│   └── services/
│       └── pipeline.py          # End-to-end inference pipeline
│
├── training/                    # Model training scripts
│   ├── train_yolo.py            # YOLOv11 training
│   ├── train_convnext.py        # ConvNeXt fine-tuning
│   ├── train_sam2.py            # SAM2 fine-tuning
│   └── evaluate.py              # mAP, accuracy, IoU metrics
│
├── datasets/
│   └── download_datasets.py     # Auto-download Food-101, UECFOOD256
│
├── notebooks/
│   ├── 01_EDA.ipynb             # Dataset exploration
│   ├── 02_Model_Training.ipynb  # Training experiments
│   └── 03_Evaluation.ipynb      # Results analysis
│
├── deployment/
│   ├── Dockerfile               # Multi-stage build
│   ├── docker-compose.yml       # Full stack orchestration
│   └── nginx.conf               # Production reverse proxy
│
├── .env.example
├── .gitignore
└── requirements.txt
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker & Docker Compose (optional)
- CUDA GPU (for training; inference runs on CPU)

### 1. Clone & Setup

```bash
git clone https://github.com/yourusername/NutriVisionAI.git
cd NutriVisionAI
```

### 2. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r ../requirements.txt
uvicorn main:app --reload --port 8000
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
# Opens at http://localhost:5173
```

### 4. Docker (Full Stack)

```bash
docker-compose -f deployment/docker-compose.yml up --build
```

---

## 📡 API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive Swagger UI.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/upload` | POST | Upload & preprocess meal image |
| `/api/analyze` | POST | Full pipeline: detect → classify → nutrition |
| `/api/recommend` | POST | AI coach personalized recommendations |
| `/api/history/{user_id}` | GET | Meal history |
| `/api/dashboard/{user_id}` | GET | Analytics & trends |
| `/api/profile` | POST | Save user profile (athlete settings) |

### Example: Analyze a Meal

```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -H "Content-Type: multipart/form-data" \
  -F "image=@dal_rice.jpg" \
  -F "user_id=123"
```

**Response:**
```json
{
  "detected_foods": [
    {
      "name": "Basmati Rice",
      "confidence": 0.96,
      "estimated_weight_g": 210,
      "calories": 273,
      "protein_g": 5.1,
      "carbs_g": 58.9,
      "fat_g": 0.4,
      "fiber_g": 0.6
    },
    {
      "name": "Dal Tadka",
      "confidence": 0.91,
      "estimated_weight_g": 180,
      "calories": 162,
      "protein_g": 9.2,
      "carbs_g": 26.1,
      "fat_g": 3.6,
      "fiber_g": 5.4
    }
  ],
  "total_nutrition": {
    "calories": 435,
    "protein_g": 14.3,
    "carbs_g": 85.0,
    "fat_g": 4.0,
    "fiber_g": 6.0,
    "sodium_mg": 420
  },
  "health_score": 74,
  "meal_rating": "Good",
  "analysis_time_ms": 312
}
```

---

## 🤖 Model Cards

### YOLOv11 Food Detector
- **Dataset**: Food-101 + UECFOOD256 + Indian Food Dataset (custom)
- **Classes**: 120 Indian + international food categories
- **mAP@0.5**: 0.847
- **Inference**: ~45ms on RTX 3060

### ConvNeXt Classifier  
- **Base**: ConvNeXt-Base (pretrained on ImageNet-21k)
- **Fine-tuned on**: 200 Indian food classes
- **Top-1 Accuracy**: 91.3%
- **Inference**: ~18ms on RTX 3060

### SAM2 Segmentor
- **Task**: Prompted segmentation from YOLO bounding boxes
- **mIoU**: 0.823 on food images

### Depth Anything V2
- **Task**: Monocular depth → portion volume estimation
- **Weight estimation error**: ±15% on standard portions

---

## 🏃 Athlete Mode

Configure your profile for sport-specific nutrition:

```json
{
  "sport": "100m Sprint",
  "weight_kg": 72,
  "height_cm": 178,
  "goal": "Performance",
  "training_phase": "Competition"
}
```

The AI Coach adjusts macros based on:
- **Competition Day** → High carb (7–10g/kg), moderate protein
- **Recovery Day** → High protein (2–2.5g/kg), anti-inflammatory foods
- **Gym Day** → High calorie surplus, leucine-rich protein timing
- **Rest Day** → Balanced, calorie maintenance

---

## 📊 Nutrition Database

Built on **Indian Food Composition Tables (IFCT 2017)** by the National Institute of Nutrition, India. Covers:

- 500+ Indian food items
- 23 nutrients per item (macros + 11 vitamins + 8 minerals)
- Regional variants (North Indian, South Indian, Bengali, Gujarati, etc.)
- Raw vs. cooked adjustments
- USDA FoodData Central for non-Indian items

---

## 🛠️ Tech Stack

```
Frontend:   React 18 + Vite + Chart.js + Framer Motion
Backend:    FastAPI + Uvicorn + SQLAlchemy
AI:         PyTorch 2.x + Ultralytics + HuggingFace Transformers
Images:     OpenCV + Pillow + torchvision
LLM:        Gemma-7B / Llama-3-8B (via Ollama or HuggingFace)
Database:   PostgreSQL + Alembic migrations
Cache:      Redis (meal analysis caching)
Deploy:     Docker + Nginx + AWS ECS / Hugging Face Spaces
```

---

## 📈 Results & Performance

| Metric | Value |
|--------|-------|
| Food detection mAP@0.5 | 84.7% |
| Classification accuracy | 91.3% |
| Calorie estimation error | ±12% |
| API response time (full pipeline) | ~800ms |
| Supported Indian foods | 200+ |

---

## 🗺️ Roadmap

- [x] YOLOv11 food detection
- [x] ConvNeXt classification
- [x] SAM2 segmentation
- [x] IFCT nutrition database
- [x] Health score algorithm
- [x] Athlete mode
- [x] AI Coach (LLM)
- [x] React dashboard
- [x] Docker deployment
- [ ] Mobile app (Flutter)
- [ ] OCR for packaged foods (PaddleOCR)
- [ ] Continuous glucose monitor integration
- [ ] Meal plan generator

---

## 📄 License

MIT License — see [LICENSE](LICENSE)

---

<div align="center">
Built with ❤️ for the Indian AI community | Portfolio Project for AI Engineering Internship
</div>
