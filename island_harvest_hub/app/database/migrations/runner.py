"""
Migration runner for Island Harvest Hub database migrations.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy import text, inspect
from sqlalchemy.engine import Engine

from app.database.config import engine, DATABASE_PATH
from app.database.migrations.base import Migration

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


class MigrationRunner:
    """Manages and runs database migrations."""
    
    def __init__(self, engine: Engine, migrations_dir: Optional[Path] = None):
        """
        Initialize migration runner.
        
        Args:
            engine: SQLAlchemy engine
            migrations_dir: Directory containing migration files (optional)
        """
        self.engine = engine
        self.migrations_dir = migrations_dir or Path(__file__).parent
        self._ensure_migrations_table()
    
    def _ensure_migrations_table(self):
        """Create migrations tracking table if it doesn't exist."""
        with self.engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version VARCHAR(50) PRIMARY KEY,
                    description TEXT,
                    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.commit()
    
    def get_applied_migrations(self) -> List[str]:
        """Get list of applied migration versions."""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT version FROM schema_migrations ORDER BY version"))
                return [row[0] for row in result]
        except Exception:
            return []
    
    def record_migration(self, migration: Migration):
        """Record that a migration has been applied."""
        with self.engine.connect() as conn:
            conn.execute(text("""
                INSERT OR REPLACE INTO schema_migrations (version, description, applied_at)
                VALUES (:version, :description, :applied_at)
            """), {
                'version': migration.version,
                'description': migration.description,
                'applied_at': datetime.now()
            })
            conn.commit()
    
    def is_migration_applied(self, version: str) -> bool:
        """Check if a migration has been applied."""
        return version in self.get_applied_migrations()
    
    def run_migration(self, migration: Migration, dry_run: bool = False) -> bool:
        """
        Run a single migration.
        
        Args:
            migration: Migration instance
            dry_run: If True, don't actually apply the migration
            
        Returns:
            True if successful, False otherwise
        """
        if self.is_migration_applied(migration.version):
            if not os.getenv('IHH_SILENT_INIT'):
                print(f"[MIGRATION] Skipping {migration.version}: {migration.description} (already applied)")
            return True
        
        if not os.getenv('IHH_SILENT_INIT'):
            print(f"[MIGRATION] Applying {migration.version}: {migration.description}")
        
        if dry_run:
            print(f"[DRY RUN] Would apply migration {migration.version}")
            return True
        
        try:
            with self.engine.begin() as conn:
                migration.up(conn)
                self.record_migration(migration)
            
            if not os.getenv('IHH_SILENT_INIT'):
                print(f"[MIGRATION] Successfully applied {migration.version}")
            return True
        except Exception as e:
            print(f"[MIGRATION ERROR] Failed to apply {migration.version}: {str(e)}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return False
    
    def run_all_migrations(self, migrations: List[Migration], dry_run: bool = False) -> Dict[str, bool]:
        """
        Run all pending migrations.
        
        Args:
            migrations: List of Migration instances (should be sorted by version)
            dry_run: If True, don't actually apply migrations
            
        Returns:
            Dictionary mapping migration versions to success status
        """
        results = {}
        
        for migration in migrations:
            results[migration.version] = self.run_migration(migration, dry_run=dry_run)
            if not results[migration.version]:
                break  # Stop on first failure
        
        return results
    
    def get_migration_status(self) -> Dict:
        """Get status of all migrations."""
        applied = self.get_applied_migrations()
        
        return {
            'applied_count': len(applied),
            'applied_versions': applied,
            'database_path': str(DATABASE_PATH),
            'database_exists': DATABASE_PATH.exists()
        }


# Import all migrations
def get_all_migrations() -> List[Migration]:
    """Get all available migrations in order."""
    from .m001_add_business_id import Migration001AddBusinessId
    
    return [
        Migration001AddBusinessId(),
    ]

