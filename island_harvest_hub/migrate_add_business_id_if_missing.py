"""
Migration script to add business_id column to customers table if it's missing.

This script:
1. Checks if customers.business_id column exists
2. Adds the column if missing
3. Sets default value 'island_harvest' for existing rows
4. Makes the column NOT NULL with default value
"""

import sys
import os
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import inspect, text, Column, String
from app.database.config import engine, DATABASE_PATH

def check_column_exists(table_name, column_name):
    """Check if a column exists in a table."""
    inspector = inspect(engine)
    if table_name not in inspector.get_table_names():
        return False
    
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def migrate_add_business_id():
    """Add business_id column to customers table if missing."""
    print("=" * 80)
    print("MIGRATION: Add business_id to customers table")
    print("=" * 80)
    print(f"\nDatabase Path: {DATABASE_PATH}")
    print(f"Database Exists: {DATABASE_PATH.exists()}\n")
    
    if not DATABASE_PATH.exists():
        print("[ERROR] Database file does not exist!")
        print("   Please run init_db.py first to create the database.")
        return False
    
    # Check if column already exists
    if check_column_exists('customers', 'business_id'):
        print("[OK] business_id column already exists in customers table.")
        print("   No migration needed.")
        
        # Check if any rows have NULL business_id
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(*) FROM customers WHERE business_id IS NULL OR business_id = ''"))
                null_count = result.scalar()
                
                if null_count > 0:
                    print(f"\n[WARNING] Found {null_count} rows with missing business_id.")
                    print("   Updating NULL values to 'island_harvest'...")
                    
                    conn.execute(text("UPDATE customers SET business_id = 'island_harvest' WHERE business_id IS NULL OR business_id = ''"))
                    conn.commit()
                    
                    print(f"[OK] Updated {null_count} rows with default business_id.")
                else:
                    print("[OK] All rows have business_id set.")
        except Exception as e:
            print(f"[ERROR] Error checking/updating data: {str(e)}")
            return False
        
        return True
    
    # Column doesn't exist, add it
    print("[WARNING] business_id column is missing in customers table.")
    print("   Adding column...")
    
    try:
        with engine.connect() as conn:
            # Step 1: Add column with default value
            print("   Step 1: Adding business_id column...")
            conn.execute(text("""
                ALTER TABLE customers 
                ADD COLUMN business_id VARCHAR(50) DEFAULT 'island_harvest'
            """))
            conn.commit()
            print("   [OK] Column added with default value.")
            
            # Step 2: Update any NULL values (shouldn't be any, but just in case)
            print("   Step 2: Ensuring all rows have business_id...")
            conn.execute(text("""
                UPDATE customers 
                SET business_id = 'island_harvest' 
                WHERE business_id IS NULL OR business_id = ''
            """))
            conn.commit()
            print("   [OK] All rows updated.")
            
            # Step 3: Make column NOT NULL (SQLite doesn't support ALTER COLUMN directly)
            # We'll create a new table, copy data, drop old, rename new
            print("   Step 3: Making business_id NOT NULL...")
            
            # Create new table with NOT NULL constraint
            conn.execute(text("""
                CREATE TABLE customers_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    business_id VARCHAR(50) NOT NULL DEFAULT 'island_harvest',
                    name VARCHAR(255) NOT NULL,
                    contact_person VARCHAR(255),
                    phone VARCHAR(50),
                    email VARCHAR(255),
                    address TEXT,
                    preferences TEXT,
                    satisfaction_score INTEGER,
                    feedback TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME
                )
            """))
            
            # Copy data
            conn.execute(text("""
                INSERT INTO customers_new 
                (id, business_id, name, contact_person, phone, email, address, 
                 preferences, satisfaction_score, feedback, created_at, updated_at)
                SELECT 
                    id, 
                    COALESCE(business_id, 'island_harvest') as business_id,
                    name, contact_person, phone, email, address,
                    preferences, satisfaction_score, feedback, created_at, updated_at
                FROM customers
            """))
            
            # Drop old table
            conn.execute(text("DROP TABLE customers"))
            
            # Rename new table
            conn.execute(text("ALTER TABLE customers_new RENAME TO customers"))
            
            conn.commit()
            print("   [OK] Column is now NOT NULL.")
            
            print("\n[OK] Migration completed successfully!")
            print("   business_id column has been added to customers table.")
            return True
            
    except Exception as e:
        print(f"\n[ERROR] Error during migration: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = migrate_add_business_id()
    sys.exit(0 if success else 1)

