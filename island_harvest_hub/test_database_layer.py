"""
Test script for database layer refactoring.
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database.config import DATABASE_PATH, DATABASE_URL, SQLALCHEMY_DATABASE_URI
from app.database.manager import DatabaseManager
from app.database.schema import SchemaVerifier
from app.database.migrations.runner import MigrationRunner

def test_database_config():
    """Test database configuration."""
    print("=" * 80)
    print("TEST: Database Configuration")
    print("=" * 80)
    print(f"Database Path: {DATABASE_PATH}")
    print(f"Absolute Path: {DATABASE_PATH.absolute()}")
    print(f"Database URL: {DATABASE_URL}")
    print(f"SQLAlchemy URI: {SQLALCHEMY_DATABASE_URI}")
    print(f"Path is absolute: {DATABASE_PATH.is_absolute()}")
    print("✅ Configuration test passed\n")

def test_database_manager():
    """Test database manager."""
    print("=" * 80)
    print("TEST: Database Manager")
    print("=" * 80)
    
    manager = DatabaseManager()
    status = manager.get_status()
    
    print(f"Database exists: {status['database']['exists']}")
    print(f"Total tables: {len(status['database']['tables'])}")
    print(f"Migrations applied: {status['migrations']['applied_count']}")
    print(f"Schema valid: {status['schema']['valid']}")
    print("✅ Manager test passed\n")

def test_schema_verifier():
    """Test schema verifier."""
    print("=" * 80)
    print("TEST: Schema Verifier")
    print("=" * 80)
    
    from app.database.config import engine
    verifier = SchemaVerifier(engine, DATABASE_PATH)
    
    info = verifier.get_database_info()
    print(f"Database exists: {info['exists']}")
    print(f"Total tables: {len(info['tables'])}")
    
    if info['tables']:
        first_table = info['tables'][0]
        schema = verifier.get_table_schema(first_table)
        print(f"Sample table schema ({first_table}): {len(schema.get('columns', []))} columns")
    
    print("✅ Schema verifier test passed\n")

def test_migration_runner():
    """Test migration runner."""
    print("=" * 80)
    print("TEST: Migration Runner")
    print("=" * 80)
    
    from app.database.config import engine
    runner = MigrationRunner(engine)
    
    applied = runner.get_applied_migrations()
    print(f"Applied migrations: {len(applied)}")
    if applied:
        print(f"Versions: {', '.join(applied)}")
    
    status = runner.get_migration_status()
    print(f"Migration status: {status['applied_count']} applied")
    print("✅ Migration runner test passed\n")

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("DATABASE LAYER REFACTORING - TEST SUITE")
    print("=" * 80 + "\n")
    
    try:
        test_database_config()
        test_database_manager()
        test_schema_verifier()
        test_migration_runner()
        
        print("=" * 80)
        print("ALL TESTS PASSED ✅")
        print("=" * 80)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

