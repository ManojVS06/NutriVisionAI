from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# ==========================================
# AUTH SCHEMAS
# ==========================================
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    username_or_email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# ==========================================
# ATHLETE PROFILE SCHEMAS
# ==========================================
class AthleteProfileCreate(BaseModel):
    weight: float = Field(..., gt=20, lt=250, description="Weight in kg")
    height: float = Field(..., gt=100, lt=250, description="Height in cm")
    age: int = Field(..., gt=10, lt=100)
    gender: str = Field(..., description="Male, Female, or Other")
    sport: str = Field(..., description="e.g. Sprinter, Bodybuilder, Cricket, General Fitness")
    training_phase: str = Field(..., description="e.g. Cut, Bulk, Competition Day, Rest Day")

class AthleteProfileUpdate(BaseModel):
    weight: Optional[float] = None
    height: Optional[float] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    sport: Optional[str] = None
    training_phase: Optional[str] = None

class AthleteProfileResponse(BaseModel):
    id: int
    user_id: int
    weight: float
    height: float
    age: int
    gender: str
    sport: str
    training_phase: str
    calorie_target: int
    protein_target: int
    carbs_target: int
    fat_target: int

    class Config:
        from_attributes = True

# ==========================================
# FOOD ITEM SCHEMAS
# ==========================================
class FoodItemResponse(BaseModel):
    id: int
    name: str
    weight_g: float
    calories: float
    protein: float
    carbs: float
    fat: float
    fiber: float
    sodium: float
    sugar: float
    density: float
    volume_cm3: float
    bounding_box: Optional[str] = None # JSON string
    confidence: float
    detection_method: str

    class Config:
        from_attributes = True

class FoodItemUpdate(BaseModel):
    id: int
    weight_g: float

# ==========================================
# MEAL SCHEMAS
# ==========================================
class MealResponse(BaseModel):
    id: int
    user_id: int
    image_url: str
    processed_url: Optional[str] = None
    mask_url: Optional[str] = None
    depth_url: Optional[str] = None
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    total_fiber: float
    total_sodium: float
    total_sugar: float
    health_score: int
    coach_notes: Optional[str] = None
    quality_score: float
    detection_method: str
    created_at: datetime
    food_items: List[FoodItemResponse] = []

    class Config:
        from_attributes = True

class MealSimpleResponse(BaseModel):
    id: int
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    health_score: int
    quality_score: float
    detection_method: str
    created_at: datetime

    class Config:
        from_attributes = True

class MealUpdateRequest(BaseModel):
    food_items: List[FoodItemUpdate]

# ==========================================
# ANALYTICS & DASHBOARD SCHEMAS
# ==========================================
class DailyMacros(BaseModel):
    calories: float
    protein: float
    carbs: float
    fat: float

class DailyTarget(BaseModel):
    calories: int
    protein: int
    carbs: int
    fat: int

class DashboardSummary(BaseModel):
    consumed: DailyMacros
    target: DailyTarget
    health_score: int
    meals: List[MealResponse] = []
