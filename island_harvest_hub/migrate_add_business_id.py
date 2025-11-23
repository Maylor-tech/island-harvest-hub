"""
Database Migration Script: Add business_id to existing records

This script adds the business_id field to all existing records in the database.
All existing records will be assigned to 'island_harvest' by default.

Run this script once after updating the models to include business_id fields.

Usage:
    python migrate_add_business_id.py
"""

import sqlite3
import os
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def migrate_database():
    """Add business_id column to all relevant tables."""
    
    # Database path - use root database (parent of island_harvest_hub folder)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)  # Go up from island_harvest_hub to project root
    db_path = os.path.join(project_root, 'island_harvest_hub.db')
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        print("Database will be created with business_id fields when you start the application.")
        return
    
    print(f"Migrating database at {db_path}...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Tables that need business_id column
    tables = [
        'customers',
        'farmers',
        'orders',
        'transactions',
        'invoices',
        'daily_logs',
        'goals'
    ]
    
    try:
        for table in tables:
            # Check if table exists
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if not cursor.fetchone():
                print(f"  [SKIP] Table '{table}' does not exist, skipping...")
                continue
            
            # Check if business_id column already exists
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'business_id' in columns:
                print(f"  [OK] Table '{table}' already has business_id column")
            else:
                # Add business_id column with default value
                print(f"  -> Adding business_id to '{table}'...")
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN business_id TEXT DEFAULT 'island_harvest'")
                
                # Update existing records to have business_id
                cursor.execute(f"UPDATE {table} SET business_id = 'island_harvest' WHERE business_id IS NULL")
                print(f"  [OK] Updated existing records in '{table}'")
        
        # Remove unique constraint from customers.name and farmers.name if they exist
        # SQLite doesn't support DROP CONSTRAINT directly, so we'll note it
        print("\n  [NOTE] If you see 'UNIQUE constraint failed' errors when adding customers/suppliers,")
        print("         you may need to recreate the database. The unique constraint on 'name' has been")
        print("         removed in the new model (names are now unique per business_id).")
        
        conn.commit()
        print("\n[SUCCESS] Migration completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"\n[ERROR] Error during migration: {str(e)}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Database Migration: Adding business_id to existing records")
    print("=" * 60)
    print()
    
    try:
        migrate_database()
        print("\n" + "=" * 60)
        print("Next steps:")
        print("1. Restart your Streamlit application")
        print("2. Test adding customers/suppliers")
        print("3. Verify business switching works correctly")
        print("=" * 60)
    except Exception as e:
        print(f"\n[ERROR] Migration failed: {str(e)}")
        sys.exit(1)

