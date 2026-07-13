"""
NutriVision AI — Database Models (SQLAlchemy ORM)

Tables: Users, MealLogs, FoodItems, Goals, NutritionHistory
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, Float, String, Boolean,
    DateTime, ForeignKey, Text, JSON
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    """User profile and athlete settings."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Physical profile
    weight_kg = Column(Float, nullable=True)
    height_cm = Column(Float, nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)  # male, female, other

    # Athlete profile
    sport = Column(String(100), default="general fitness")
    training_phase = Column(String(50), default="base_training")
    goal = Column(String(50), default="maintain")  # muscle_gain, fat_loss, maintain, performance
    activity_level = Column(String(50), default="moderate")

    # Preferences
    is_vegetarian = Column(Boolean, default=False)
    is_vegan = Column(Boolean, default=False)
    dietary_restrictions = Column(JSON, default=list)
    allergies = Column(JSON, default=list)

    # Relationships
    meal_logs = relationship("MealLog", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")


class MealLog(Base):
    """A single meal scan event."""
    __tablename__ = "meal_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    logged_at = Column(DateTime, default=datetime.utcnow, index=True)
    meal_type = Column(String(20), default="lunch")  # breakfast, lunch, dinner, snack

    # Image
    image_path = Column(String(500), nullable=True)
    image_url = Column(String(500), nullable=True)

    # Analysis results
    detected_foods = Column(JSON, default=list)       # List of food detection objects
    total_nutrition = Column(JSON, default=dict)       # Aggregated nutrients
    health_score = Column(Integer, nullable=True)      # 0-100
    health_grade = Column(String(20), nullable=True)   # Excellent, Good, etc.

    # AI outputs
    ai_recommendation = Column(Text, nullable=True)
    analysis_time_ms = Column(Integer, nullable=True)

    # Status
    is_demo = Column(Boolean, default=False)  # True if mock inference was used

    # Relationships
    user = relationship("User", back_populates="meal_logs")
    food_items = relationship("FoodItem", back_populates="meal_log", cascade="all, delete-orphan")


class FoodItem(Base):
    """Individual food item detected within a meal."""
    __tablename__ = "food_items"

    id = Column(Integer, primary_key=True, index=True)
    meal_log_id = Column(Integer, ForeignKey("meal_logs.id"), nullable=False)

    # Detection
    food_name = Column(String(150), nullable=False)
    detection_confidence = Column(Float, nullable=True)
    classification_confidence = Column(Float, nullable=True)
    bbox_x1 = Column(Integer, nullable=True)
    bbox_y1 = Column(Integer, nullable=True)
    bbox_x2 = Column(Integer, nullable=True)
    bbox_y2 = Column(Integer, nullable=True)

    # Portion
    estimated_weight_g = Column(Float, nullable=True)
    portion_confidence = Column(Float, nullable=True)

    # Nutrition (per this item's portion)
    calories = Column(Float, nullable=True)
    protein_g = Column(Float, nullable=True)
    carbs_g = Column(Float, nullable=True)
    fat_g = Column(Float, nullable=True)
    fiber_g = Column(Float, nullable=True)
    sodium_mg = Column(Float, nullable=True)
    calcium_mg = Column(Float, nullable=True)
    iron_mg = Column(Float, nullable=True)

    # DB info
    ifct_matched_name = Column(String(150), nullable=True)
    ifct_category = Column(String(50), nullable=True)

    # Relationship
    meal_log = relationship("MealLog", back_populates="food_items")


class Goal(Base):
    """User nutrition and fitness goals."""
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Daily targets
    daily_calories = Column(Integer, nullable=True)
    daily_protein_g = Column(Float, nullable=True)
    daily_carbs_g = Column(Float, nullable=True)
    daily_fat_g = Column(Float, nullable=True)
    daily_fiber_g = Column(Float, nullable=True)

    # Timeline
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    goal_type = Column(String(50), nullable=True)  # muscle_gain, fat_loss, performance
    is_active = Column(Boolean, default=True)

    # Relationship
    user = relationship("User", back_populates="goals")


# ─────────────────────────────────────────────────────────────────────────────
# Pydantic Schemas (for API request/response validation)
# ─────────────────────────────────────────────────────────────────────────────

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List


class UserCreate(BaseModel):
    email: EmailStr
    name: str
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    sport: str = "general fitness"
    training_phase: str = "base_training"
    goal: str = "maintain"
    is_vegetarian: bool = False
    is_vegan: bool = False


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    sport: str
    goal: str
    training_phase: str

    class Config:
        from_attributes = True


class FoodDetectionResult(BaseModel):
    food_name: str
    confidence: float
    estimated_weight_g: float
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float
    sodium_mg: float
    bbox: Optional[List[int]] = None
    category: Optional[str] = None
    demo: bool = False


class MealAnalysisResponse(BaseModel):
    meal_id: Optional[int] = None
    detected_foods: List[FoodDetectionResult]
    total_nutrition: dict
    health_score: int
    health_grade: str
    health_feedback: List[str]
    macro_percentages: dict
    analysis_time_ms: int
    is_demo: bool = True


class RecommendationRequest(BaseModel):
    meal_id: Optional[int] = None
    detected_foods: List[str]
    total_nutrition: dict
    user_id: Optional[int] = None
    user_profile: Optional[dict] = None


class ProfileUpdateRequest(BaseModel):
    user_id: int
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    age: Optional[int] = None
    sport: Optional[str] = None
    training_phase: Optional[str] = None
    goal: Optional[str] = None
    is_vegetarian: Optional[bool] = None
