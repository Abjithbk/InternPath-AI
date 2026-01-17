import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# --- DEBUG: Print Environment Variables (Safe Mode) ---
print("🔍 [DEBUG] Checking Environment Variables...")
found_url = os.getenv("DATABASE_URL")
if found_url:
    print(f"   ✅ DATABASE_URL found: {found_url[:10]}... (Hidden)")
else:
    print("   ❌ DATABASE_URL is MISSING from Environment!")

# 1. GET CREDENTIALS
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# 2. STRICT VALIDATION
if not SQLALCHEMY_DATABASE_URL:
    # This stops the app from running in "fake mode"
    raise ValueError("❌ FATAL ERROR: 'DATABASE_URL' env variable is missing! Check Render Dashboard -> Environment.")

# 3. FIX PROTOCOL (Render/Supabase uses postgres://, Python needs postgresql://)
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

print("✅ [DATABASE] Connection string configured.")

# 4. CREATE ENGINE
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()