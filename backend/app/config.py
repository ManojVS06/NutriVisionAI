import os
from dotenv import load_dotenv

# Load env variables from backend/.env if it exists
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(backend_dir, ".env")
load_dotenv(dotenv_path=env_path)

db_url = os.getenv("DATABASE_URL", "sqlite:///./nutrivision.db")
if db_url.startswith("sqlite:///"):
    db_path = db_url.replace("sqlite:///", "")
    if db_path.startswith("./"):
        db_path = db_path[2:]
    if not os.path.isabs(db_path):
        db_path = os.path.abspath(os.path.join(backend_dir, db_path))
    db_url = f"sqlite:///{db_path}"

class Settings:
    DATABASE_URL: str = db_url
    JWT_SECRET: str = os.getenv("JWT_SECRET", "8f9a2e6b1d4c7f0e3a5b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    
    # Static files directories
    STATIC_DIR: str = os.path.abspath(os.path.join(backend_dir, "static"))
    UPLOAD_DIR: str = os.path.join(STATIC_DIR, "uploads")
    
settings = Settings()

# Ensure directories exist
os.makedirs(settings.STATIC_DIR, exist_ok=True)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
