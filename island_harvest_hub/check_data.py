"""Check database data and schema."""
import sqlite3
from pathlib import Path

# Get database path (project root)
db_path = Path(__file__).parent.parent / "island_harvest_hub.db"
print(f"Checking database at: {db_path}")
print(f"Database exists: {db_path.exists()}")

if not db_path.exists():
    print("ERROR: Database file not found!")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check customers
print("\n" + "=" * 60)
print("CUSTOMERS")
print("=" * 60)
try:
    cursor.execute("SELECT COUNT(*), business_id FROM customers GROUP BY business_id")
    print("\nCustomers by business:")
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            print(f"  Count: {row[0]}, Business: {row[1]}")
    else:
        print("  No customers found")
    
    cursor.execute("SELECT COUNT(*) FROM customers")
    total = cursor.fetchone()[0]
    print(f"\nTotal customers: {total}")
except Exception as e:
    print(f"Error checking customers: {e}")

# Check transactions
print("\n" + "=" * 60)
print("TRANSACTIONS")
print("=" * 60)

# First check if transactions table exists and has business_id column
try:
    cursor.execute("PRAGMA table_info(transactions)")
    columns = cursor.fetchall()
    print("\nTransactions table columns:")
    column_names = []
    for col in columns:
        column_names.append(col[1])
        print(f"  {col[1]} ({col[2]})")
    
    has_business_id = 'business_id' in column_names
    print(f"\nHas business_id column: {has_business_id}")
    
    if has_business_id:
        cursor.execute("SELECT COUNT(*), type, business_id FROM transactions GROUP BY type, business_id")
        print("\nTransactions by business:")
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                print(f"  Count: {row[0]}, Type: {row[1]}, Business: {row[2]}")
        else:
            print("  No transactions found")
        
        cursor.execute("SELECT COUNT(*) FROM transactions")
        total = cursor.fetchone()[0]
        print(f"\nTotal transactions: {total}")
        
        # Check revenue transactions
        cursor.execute("SELECT COUNT(*), SUM(amount) FROM transactions WHERE type = 'revenue'")
        rev_row = cursor.fetchone()
        print(f"\nRevenue transactions: {rev_row[0]}, Total: ${rev_row[1] or 0:.2f}")
    else:
        print("\nWARNING: transactions table does not have business_id column!")
        cursor.execute("SELECT COUNT(*) FROM transactions")
        total = cursor.fetchone()[0]
        print(f"Total transactions (without business_id): {total}")
        
except Exception as e:
    print(f"\nTransactions table issue: {e}")

# Check other key tables
print("\n" + "=" * 60)
print("OTHER TABLES")
print("=" * 60)

tables_to_check = ['orders', 'invoices', 'farmers', 'daily_logs']
for table in tables_to_check:
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{table}: {count} records")
    except Exception as e:
        print(f"{table}: Error - {e}")

conn.close()
print("\n" + "=" * 60)
print("Check complete!")
print("=" * 60)

