from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

DatabaseURL = os.getenv("DATABASE_URL", "mysql+pymysql://root:passw0rd@77.37.45.138/ai_analyser")

# If using SQLite, we need connect_args to allow multithreading
if DatabaseURL.startswith("sqlite"):
    engine = create_engine(DatabaseURL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DatabaseURL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()