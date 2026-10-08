import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
load_dotenv()
URL = os.getenv("DATABASE_URL", "sqlite:///./meditrack.db")
if URL.startswith("postgres://"):
    URL = URL.replace("postgres://", "postgresql://", 1)
engine = create_engine(URL, connect_args={"check_same_thread": False} if URL.startswith("sqlite") else {}, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
