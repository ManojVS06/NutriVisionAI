from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    athlete_profile = relationship("AthleteProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    meals = relationship("Meal", back_populates="user", cascade="all, delete-orphan")


class AthleteProfile(Base):
    __tablename__ = "athlete_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    weight = Column(Float, nullable=False)  # in kg
    height = Column(Float, nullable=False)  # in cm
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=False)
    sport = Column(String, nullable=False)  # e.g., Sprinter, Bodybuilder, Cricket, etc.
    training_phase = Column(String, nullable=False)  # e.g., Cut, Bulk, Competition Day, Rest Day
    
    # Nutrition Targets (calculated based on bodyweight and sport profile)
    calorie_target = Column(Integer, nullable=False)
    protein_target = Column(Integer, nullable=False)  # in g
    carbs_target = Column(Integer, nullable=False)    # in g
    fat_target = Column(Integer, nullable=False)      # in g

    # Relationships
    user = relationship("User", back_populates="athlete_profile")


class Meal(Base):
    __tablename__ = "meals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    image_url = Column(String, nullable=False)  # Path to original uploaded photo
    processed_url = Column(String, nullable=True)  # Path to image with bounding boxes
    mask_url = Column(String, nullable=True)  # Path to transparent segmentation masks
    depth_url = Column(String, nullable=True)  # Path to simulated depth map
    
    # Aggregated nutritional values
    total_calories = Column(Float, default=0.0)
    total_protein = Column(Float, default=0.0)
    total_carbs = Column(Float, default=0.0)
    total_fat = Column(Float, default=0.0)
    total_fiber = Column(Float, default=0.0)
    total_sodium = Column(Float, default=0.0)  # in mg
    total_sugar = Column(Float, default=0.0)   # in g
    health_score = Column(Integer, default=50)  # 0 to 100
    coach_notes = Column(String, nullable=True)  # AI Coach advice text
    quality_score = Column(Float, default=100.0) # Image quality gate score (0-100)
    detection_method = Column(String, default="gemini_vision")  # gemini_vision | openrouter_vision | opencv_fallback | demo
    
    created_at = Column(DateTime, server_default=func.now(), index=True)

    # Relationships
    user = relationship("User", back_populates="meals")
    food_items = relationship("FoodItem", back_populates="meal", cascade="all, delete-orphan")


class FoodItem(Base):
    __tablename__ = "food_items"

    id = Column(Integer, primary_key=True, index=True)
    meal_id = Column(Integer, ForeignKey("meals.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    weight_g = Column(Float, nullable=False)
    calories = Column(Float, nullable=False)
    protein = Column(Float, nullable=False)
    carbs = Column(Float, nullable=False)
    fat = Column(Float, nullable=False)
    fiber = Column(Float, default=0.0)
    sodium = Column(Float, default=0.0)
    sugar = Column(Float, default=0.0)
    density = Column(Float, default=1.0)
    volume_cm3 = Column(Float, default=0.0)
    bounding_box = Column(String, nullable=True)  # JSON string of coordinates: [xmin, ymin, xmax, ymax]
    confidence = Column(Float, default=1.0)       # Detection confidence (0.0-1.0)
    detection_method = Column(String, default="gemini_vision")  # Per-item method used

    # Relationships
    meal = relationship("Meal", back_populates="food_items")


class NutritionDB(Base):
    """
    Standard Indian Food Composition Tables (IFCT) Reference Database
    Values are stored per 100 grams of food.
    """
    __tablename__ = "nutrition_db"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    category = Column(String, nullable=False)  # Cereal, Pulses, Dairy, Vegetables, Meat, etc.
    calories_per_100g = Column(Float, nullable=False)
    protein_per_100g = Column(Float, nullable=False)
    carbs_per_100g = Column(Float, nullable=False)
    fat_per_100g = Column(Float, nullable=False)
    fiber_per_100g = Column(Float, default=0.0)
    sodium_per_100g = Column(Float, default=0.0)  # in mg
    sugar_per_100g = Column(Float, default=0.0)   # in g
    density_g_cm3 = Column(Float, default=1.0)    # Food density for volume to weight estimation
