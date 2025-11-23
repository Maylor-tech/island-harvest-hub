"""
Database initialization script for Island Harvest Hub AI Assistant.
"""

import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.config import init_db

if __name__ == "__main__":
    print("Initializing Island Harvest Hub database...")
    init_db()
    print("Database initialization complete!")

