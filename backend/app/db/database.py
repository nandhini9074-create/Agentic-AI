from sqlalchemy import create_engine, Column, Integer, String, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from app.utils.logger import log_execution_time

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ProfileDB(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    profile_data = Column(JSON)
    insights = Column(JSON)
    confidence = Column(JSON)

Base.metadata.create_all(bind=engine)

@log_execution_time
def get_db():
    # Dependency for providing a temporary database session to API endpoints or background tasks
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
