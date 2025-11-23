"""
Database manager for Island Harvest Hub.

Handles database initialization, verification, and migrations.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, List
from sqlalchemy.engine import Engine

from app.database.config import (
    engine as _engine,
    Base,
    DATABASE_PATH,
    get_database_path
)
from app.database.schema import SchemaVerifier
from app.database.migrations.runner import MigrationRunner, get_all_migrations

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


class DatabaseManager:
    """Manages database initialization, verification, and migrations."""
    
    def __init__(self, engine: Optional[Engine] = None):
        """
        Initialize database manager.
        
        Args:
            engine: SQLAlchemy engine (uses default if not provided)
        """
        self.engine = engine or _engine
        self.database_path = DATABASE_PATH
        self.verifier = SchemaVerifier(self.engine, self.database_path)
        self.migration_runner = MigrationRunner(self.engine)
    
    def ensure_database_exists(self) -> bool:
        """Ensure database file exists (create if needed)."""
        try:
            self.database_path.parent.mkdir(parents=True, exist_ok=True)
            if not self.database_path.exists():
                # Touch the file to create it
                self.database_path.touch()
            return True
        except Exception as e:
            print(f"[DB ERROR] Failed to ensure database exists: {e}", file=sys.stderr)
            return False
    
    def initialize_schema(self) -> bool:
        """
        Initialize database schema by creating all tables.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            from app.models import (
                Customer, Order, OrderItem, Farmer, FarmerPayment,
                DailyLog, Transaction, Invoice, MessageTemplate,
                Meeting, FollowUpTask, Document, Goal,
                PerformanceMetric, Partnership
            )
            
            Base.metadata.create_all(bind=self.engine)
            
            if not os.getenv('IHH_SILENT_INIT'):
                print(f"[DB] Schema initialized successfully")
            return True
        except Exception as e:
            print(f"[DB ERROR] Failed to initialize schema: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return False
    
    def run_migrations(self, dry_run: bool = False) -> Dict[str, bool]:
        """
        Run all pending migrations.
        
        Args:
            dry_run: If True, don't actually apply migrations
            
        Returns:
            Dictionary mapping migration versions to success status
        """
        migrations = get_all_migrations()
        return self.migration_runner.run_all_migrations(migrations, dry_run=dry_run)
    
    def verify_schema(self, expected_tables: Optional[List[str]] = None) -> Dict:
        """
        Verify database schema.
        
        Args:
            expected_tables: List of expected table names (optional)
            
        Returns:
            Dictionary with verification results
        """
        if expected_tables is None:
            expected_tables = [
                'customers', 'orders', 'order_items', 'farmers', 'farmer_payments',
                'daily_logs', 'transactions', 'invoices', 'message_templates',
                'meetings', 'follow_up_tasks', 'documents', 'goals',
                'performance_metrics', 'partnerships', 'schema_migrations'
            ]
        
        return self.verifier.verify_schema(expected_tables)
    
    def initialize(self, run_migrations: bool = True, verify_schema: bool = True) -> bool:
        """
        Complete database initialization.
        
        Args:
            run_migrations: Whether to run migrations
            verify_schema: Whether to verify schema after initialization
            
        Returns:
            True if successful, False otherwise
        """
        # Step 1: Ensure database exists
        if not self.ensure_database_exists():
            return False
        
        # Step 2: Initialize schema
        if not self.initialize_schema():
            return False
        
        # Step 3: Run migrations
        if run_migrations:
            migration_results = self.run_migrations()
            if not all(migration_results.values()):
                print("[DB WARNING] Some migrations failed", file=sys.stderr)
        
        # Step 4: Verify schema
        if verify_schema:
            verification = self.verify_schema()
            if not verification['valid']:
                print(f"[DB WARNING] Schema verification failed: {verification}", file=sys.stderr)
        
        if not os.getenv('IHH_SILENT_INIT'):
            print(f"[DB] Database initialization complete: {self.database_path}")
        
        return True
    
    def get_status(self) -> Dict:
        """Get comprehensive database status."""
        info = self.verifier.get_database_info()
        migration_status = self.migration_runner.get_migration_status()
        schema_verification = self.verify_schema()
        
        return {
            'database': info,
            'migrations': migration_status,
            'schema': schema_verification,
            'path': str(self.database_path),
            'absolute_path': str(self.database_path.absolute())
        }
    
    def print_status_report(self):
        """Print a comprehensive status report."""
        status = self.get_status()
        
        print("=" * 80)
        print("DATABASE STATUS REPORT")
        print("=" * 80)
        print(f"\nDatabase Path: {status['path']}")
        print(f"Absolute Path: {status['absolute_path']}")
        print(f"Database Exists: {status['database']['exists']}")
        if status['database']['exists']:
            print(f"Database Size: {status['database']['size_kb']:.2f} KB")
        print(f"Total Tables: {len(status['database']['tables'])}")
        
        print(f"\nMigrations Applied: {status['migrations']['applied_count']}")
        if status['migrations']['applied_versions']:
            print("Applied Versions:")
            for version in status['migrations']['applied_versions']:
                print(f"  - {version}")
        
        print(f"\nSchema Valid: {status['schema']['valid']}")
        if not status['schema']['valid']:
            if status['schema']['missing_tables']:
                print(f"Missing Tables: {status['schema']['missing_tables']}")
            if status['schema']['extra_tables']:
                print(f"Extra Tables: {status['schema']['extra_tables']}")
        
        print("=" * 80)


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None

def get_database_manager() -> DatabaseManager:
    """Get or create global database manager instance."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager

