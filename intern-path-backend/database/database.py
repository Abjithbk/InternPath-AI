from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv


load_dotenv()
#env for render guyss
DATABASE_URL = os.getenv("DB_URL")

if not DATABASE_URL:
    raise Exception("DB_URL environment variable not set!")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()