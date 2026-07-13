from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
import hashlib
import os
from app.database import get_db
from app.config import settings
from app import models, schemas

router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login-form")

# Helper functions for secure password hashing using PBKDF2-HMAC-SHA256
def hash_password(password: str) -> str:
    salt = os.urandom(16)
    pw_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt.hex() + ":" + pw_hash.hex()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        salt_hex, hash_hex = hashed_password.split(":")
        salt = bytes.fromhex(salt_hex)
        pw_hash = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), salt, 100000)
        return pw_hash.hex() == hash_hex
    except Exception:
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user

# Routes
@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(models.User).filter(
        (models.User.username == user_in.username) | (models.User.email == user_in.email)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
        
    # Create user
    new_user = models.User(
        username=user_in.username,
        email=user_in.email,
        password_hash=hash_password(user_in.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Initialize a default AthleteProfile for the user
    # 70 kg, 175 cm, 25 years old, General Fitness, Rest Day
    from app.api.athlete import calculate_athlete_targets
    targets = calculate_athlete_targets(70.0, 175.0, 25, "Male", "General Fitness", "Rest Day")
    
    profile = models.AthleteProfile(
        user_id=new_user.id,
        weight=70.0,
        height=175.0,
        age=25,
        gender="Male",
        sport="General Fitness",
        training_phase="Rest Day",
        calorie_target=targets["calorie_target"],
        protein_target=targets["protein_target"],
        carbs_target=targets["carbs_target"],
        fat_target=targets["fat_target"]
    )
    db.add(profile)
    db.commit()
    
    return new_user

@router.post("/login", response_model=schemas.Token)
def login(login_in: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        (models.User.username == login_in.username_or_email) | (models.User.email == login_in.username_or_email)
    ).first()
    
    if not user or not verify_password(login_in.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username/email or password"
        )
        
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

from fastapi.security import OAuth2PasswordRequestForm
@router.post("/login-form", response_model=schemas.Token, include_in_schema=False)
def login_form(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """OAuth2 password login form helper for Swagger UI Docs"""
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password"
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=schemas.UserResponse)
def read_current_user(current_user: models.User = Depends(get_current_user)):
    return current_user

from pydantic import BaseModel
class KeySyncRequest(BaseModel):
    key: str

@router.post("/sync-key")
def sync_key(payload: KeySyncRequest):
    if not payload.key.strip():
        raise HTTPException(status_code=400, detail="Invalid API Key")
    
    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    env_path = os.path.join(backend_dir, ".env")
    
    lines = []
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            lines = f.readlines()
            
    updated = False
    for i, line in enumerate(lines):
        if line.startswith("GEMINI_API_KEY="):
            lines[i] = f"GEMINI_API_KEY={payload.key.strip()}\n"
            updated = True
            break
            
    if not updated:
        lines.append(f"\nGEMINI_API_KEY={payload.key.strip()}\n")
        
    with open(env_path, "w") as f:
        f.writelines(lines)
        
    settings.GEMINI_API_KEY = payload.key.strip()
    print("[Sync Key] Saved Gemini API key to backend/.env and updated runtime configuration.")
    return {"status": "success", "message": "API key secured to backend successfully"}
