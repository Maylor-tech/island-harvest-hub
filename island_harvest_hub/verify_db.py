"""
Database verification script for Island Harvest Hub.

Prints database schema and row counts for all tables.
"""

import sys
import os
from pathlib import Path

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import inspect, text
from app.database.config import engine, DATABASE_PATH
from app.models import (
    Customer, Order, OrderItem, Farmer, FarmerPayment,
    DailyLog, Transaction, Invoice, MessageTemplate,
    Meeting, FollowUpTask, Document, Goal,
    PerformanceMetric, Partnership
)

def get_table_row_count(engine, table_name):
    """Get row count for a table."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            return result.scalar()
    except Exception as e:
        return f"Error: {str(e)}"

def print_schema():
    """Print database schema information."""
    print("=" * 80)
    print("DATABASE SCHEMA VERIFICATION")
    print("=" * 80)
    print(f"\nDatabase Path: {DATABASE_PATH}")
    print(f"Database Exists: {DATABASE_PATH.exists()}")
    print(f"Database Size: {DATABASE_PATH.stat().st_size / 1024:.2f} KB" if DATABASE_PATH.exists() else "N/A")
    print("\n" + "=" * 80)
    
    # Get inspector
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print(f"\nTotal Tables: {len(tables)}")
    print("\n" + "-" * 80)
    print("TABLE SCHEMA")
    print("-" * 80)
    
    for table_name in sorted(tables):
        print(f"\n[Table] {table_name}")
        print("-" * 40)
        
        # Get columns
        columns = inspector.get_columns(table_name)
        print("Columns:")
        for col in columns:
            col_type = str(col['type'])
            nullable = "NULL" if col['nullable'] else "NOT NULL"
            default = f" DEFAULT {col['default']}" if col.get('default') is not None else ""
            print(f"  - {col['name']}: {col_type} {nullable}{default}")
        
        # Get primary keys
        pk_constraint = inspector.get_pk_constraint(table_name)
        if pk_constraint['constrained_columns']:
            print(f"Primary Key: {', '.join(pk_constraint['constrained_columns'])}")
        
        # Get foreign keys
        fk_constraints = inspector.get_foreign_keys(table_name)
        if fk_constraints:
            print("Foreign Keys:")
            for fk in fk_constraints:
                print(f"  - {', '.join(fk['constrained_columns'])} -> {fk['referred_table']}.{', '.join(fk['referred_columns'])}")
        
        # Get indexes
        indexes = inspector.get_indexes(table_name)
        if indexes:
            print("Indexes:")
            for idx in indexes:
                unique = "UNIQUE " if idx['unique'] else ""
                print(f"  - {unique}{idx['name']}: {', '.join(idx['column_names'])}")

def print_row_counts():
    """Print row counts for all tables."""
    print("\n" + "=" * 80)
    print("ROW COUNTS")
    print("=" * 80)
    
    # Define all tables
    tables = [
        ('customers', Customer),
        ('orders', Order),
        ('order_items', OrderItem),
        ('farmers', Farmer),
        ('farmer_payments', FarmerPayment),
        ('daily_logs', DailyLog),
        ('transactions', Transaction),
        ('invoices', Invoice),
        ('message_templates', MessageTemplate),
        ('meetings', Meeting),
        ('follow_up_tasks', FollowUpTask),
        ('documents', Document),
        ('goals', Goal),
        ('performance_metrics', PerformanceMetric),
        ('partnerships', Partnership),
    ]
    
    print(f"\n{'Table Name':<30} {'Row Count':<15} {'Status'}")
    print("-" * 80)
    
    total_rows = 0
    for table_name, model in tables:
        try:
            count = get_table_row_count(engine, table_name)
            if isinstance(count, int):
                total_rows += count
                status = "[OK]"
            else:
                status = "[ERROR]"
                count = str(count)
            print(f"{table_name:<30} {str(count):<15} {status}")
        except Exception as e:
            print(f"{table_name:<30} {'Error':<15} [ERROR] {str(e)}")
    
    print("-" * 80)
    print(f"{'TOTAL':<30} {str(total_rows):<15} [OK]")
    print("=" * 80)

def check_business_id_column():
    """Check if business_id column exists in customers table."""
    print("\n" + "=" * 80)
    print("BUSINESS_ID COLUMN CHECK")
    print("=" * 80)
    
    inspector = inspect(engine)
    
    # Check customers table
    if 'customers' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('customers')]
        has_business_id = 'business_id' in columns
        
        print(f"\nCustomers table:")
        print(f"  - business_id column exists: {'[YES]' if has_business_id else '[NO]'}")
        
        if has_business_id:
            # Check if any rows are missing business_id
            try:
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT COUNT(*) FROM customers WHERE business_id IS NULL OR business_id = ''"))
                    null_count = result.scalar()
                    if null_count > 0:
                        print(f"  - Rows with missing business_id: {null_count} [WARNING]")
                    else:
                        print(f"  - All rows have business_id: [OK]")
            except Exception as e:
                print(f"  - Error checking data: {str(e)}")
        else:
            print("  [WARNING] Migration needed: customers.business_id column is missing!")
    else:
        print("  [ERROR] Customers table does not exist!")

if __name__ == "__main__":
    try:
        print_schema()
        print_row_counts()
        check_business_id_column()
        print("\n[OK] Database verification complete!")
    except Exception as e:
        print(f"\n[ERROR] Error during verification: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

