"""
Database initialization script for Island Harvest Hub AI Assistant.

This script:
1. Ensures database file exists
2. Creates all tables
3. Runs all pending migrations
4. Verifies schema
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from app.database.config import init_db, DATABASE_PATH
from app.database.manager import DatabaseManager

if __name__ == "__main__":
    print("=" * 80)
    print("Island Harvest Hub - Database Initialization")
    print("=" * 80)
    print(f"\nDatabase will be created at: {DATABASE_PATH}")
    print(f"Absolute path: {DATABASE_PATH.absolute()}\n")
    
    print("Initializing database...")
    success = init_db()
    
    if success:
        print("\n" + "=" * 80)
        print("Database initialization complete!")
        print("=" * 80)
        
        # Print status report
        manager = DatabaseManager()
        manager.print_status_report()
        sys.exit(0)
    else:
        print("\n" + "=" * 80)
        print("Database initialization failed!")
        print("=" * 80)
        sys.exit(1)

