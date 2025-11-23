"""
Database configuration and setup for Island Harvest Hub AI Assistant.
"""

import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database configuration
# Get the project root directory (parent of island_harvest_hub folder)
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATABASE_PATH = PROJECT_ROOT / "island_harvest_hub.db"

# Create SQLAlchemy database URL with absolute path
# Check if DATABASE_URL is set in environment, otherwise use absolute path
DATABASE_URL = os.getenv('DATABASE_URL', f"sqlite:///{DATABASE_PATH}")

print(f"Database path: {DATABASE_PATH}")  # Debug output

# Create engine
engine = create_engine(DATABASE_URL, echo=False)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

def get_db():
    """
    Get database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Initialize the database by creating all tables.
    """
    from app.models import (
        Customer, Order, OrderItem, Farmer, FarmerPayment,
        DailyLog, Transaction, Invoice, MessageTemplate,
        Meeting, FollowUpTask, Document, Goal,
        PerformanceMetric, Partnership
    )
    
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()

