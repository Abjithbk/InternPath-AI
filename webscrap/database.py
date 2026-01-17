import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# --- CRITICAL FIX ---
# 1. Get the URL from Render's Environment
# 2. If it's missing, ONLY THEN fallback to local sqlite
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    print("⚠️ WARNING: Using LOCAL SQLite database (Not Supabase!)")
    SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
else:
    print("✅ CONNECTING TO SUPABASE/CLOUD DATABASE")
    # Fix for Postgres URL format if needed (postgres:// -> postgresql://)
    if text := SQLALCHEMY_DATABASE_URL:
        if text.startswith("postgres://"):
            SQLALCHEMY_DATABASE_URL = text.replace("postgres://", "postgresql://", 1)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()