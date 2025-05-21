import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@db:5432/zuno_db"
)

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_pre_ping=True,
    connect_args={} if "postgresql" in DATABASE_URL else {"check_same_thread": False}
)

# SessionLocal class for database sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Encryption settings
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    import base64
    import secrets
    ENCRYPTION_KEY = base64.b64encode(secrets.token_bytes(32)).decode()
    print(f"Warning: Generated new encryption key: {ENCRYPTION_KEY}")

# API Settings
API_V1_PREFIX = "/api/v1"
PROJECT_NAME = "Zuno Marketplace"

# Security settings
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Tor settings
TOR_HOSTNAME_PATH = "/var/lib/tor/zuno_service/hostname"

# AI Model settings
AI_MODEL_PATH = os.getenv("AI_MODEL_PATH", "distilbert-base-uncased-finetuned-sst-2-english")
AI_MODEL_CACHE_DIR = os.getenv("AI_MODEL_CACHE_DIR", "/app/data/models")

# File upload settings
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/app/data/uploads")
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB

# Create necessary directories
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(AI_MODEL_CACHE_DIR, exist_ok=True)
