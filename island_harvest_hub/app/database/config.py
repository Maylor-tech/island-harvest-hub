"""
Database configuration and setup for Island Harvest Hub AI Assistant.

Database path resolution priority:
1. IHH_DB_PATH environment variable (absolute path)
2. project-root/island_harvest_hub.db (absolute path)
3. /mnt/data/island_harvest_hub.db (fallback for Streamlit Cloud)

This module ensures exactly one database file is used across all environments.
"""

import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Optional

# Global variable to track database path (ensures single DB)
_DATABASE_PATH: Optional[Path] = None
_DATABASE_INITIALIZED = False

def get_database_path() -> Path:
    """
    Get database path using priority order.
    Ensures exactly one database file is used across all environments.
    
    Priority:
    1. IHH_DB_PATH environment variable (absolute path)
    2. project-root/island_harvest_hub.db (absolute path)
    3. /mnt/data/island_harvest_hub.db (fallback for Streamlit Cloud)
    
    Returns:
        Path: Absolute path to database file
    """
    global _DATABASE_PATH
    
    # Return cached path if already determined
    if _DATABASE_PATH is not None:
        return _DATABASE_PATH
    
    # Priority 1: Environment variable IHH_DB_PATH
    env_path = os.getenv('IHH_DB_PATH')
    if env_path:
        db_path = Path(env_path).resolve()
        _DATABASE_PATH = db_path
        if not os.getenv('IHH_SILENT_INIT'):
            print(f"[DB] Using database path from IHH_DB_PATH: {db_path}")
        return db_path
    
    # Priority 2: project-root/island_harvest_hub.db
    # Get the project root directory (parent of island_harvest_hub folder)
    project_root = Path(__file__).parent.parent.parent
    default_path = project_root / "island_harvest_hub.db"
    db_path = default_path.resolve()
    
    # Check if file exists or if we can create it
    if db_path.exists() or db_path.parent.exists():
        _DATABASE_PATH = db_path
        if not os.getenv('IHH_SILENT_INIT'):
            print(f"[DB] Using database path (project root): {db_path}")
        return db_path
    
    # Priority 3: Fallback to /mnt/data/island_harvest_hub.db
    fallback_path = Path("/mnt/data/island_harvest_hub.db")
    _DATABASE_PATH = fallback_path
    if not os.getenv('IHH_SILENT_INIT'):
        print(f"[DB] Using database path (fallback): {fallback_path}")
    return fallback_path

# Get absolute database path (singleton pattern)
DATABASE_PATH = get_database_path()

# Ensure parent directory exists
try:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
except Exception as e:
    print(f"[DB ERROR] Failed to create database directory: {e}", file=sys.stderr)
    raise

# Validate we have exactly one database path
if not DATABASE_PATH.is_absolute():
    raise ValueError(f"Database path must be absolute: {DATABASE_PATH}")

# Create SQLAlchemy database URL with absolute path
# Always use absolute path for SQLite
SQLALCHEMY_DATABASE_URI = f"sqlite:///{DATABASE_PATH.absolute()}"

# Legacy support: DATABASE_URL can override if set (but must be absolute)
env_db_url = os.getenv('DATABASE_URL')
if env_db_url:
    if not env_db_url.startswith('sqlite:///'):
        raise ValueError("DATABASE_URL must be a SQLite absolute path (sqlite:///absolute/path)")
    DATABASE_URL = env_db_url
    if not os.getenv('IHH_SILENT_INIT'):
        print(f"[DB] Using DATABASE_URL override: {DATABASE_URL}")
else:
    DATABASE_URL = SQLALCHEMY_DATABASE_URI

if not os.getenv('IHH_SILENT_INIT'):
    print(f"[DB] Final database URI: {DATABASE_URL}")
    print(f"[DB] Database file: {DATABASE_PATH}")

# Create engine with connection pooling and error handling
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,  # Verify connections before using
    connect_args={
        "check_same_thread": False,  # Allow multi-threaded access
        "timeout": 20,  # Connection timeout
    }
)

# Add connection event listeners for better error handling
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Set SQLite pragmas for better performance and reliability."""
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA cache_size=10000")
    cursor.execute("PRAGMA temp_store=MEMORY")
    cursor.close()

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
    Initialize the database by creating all tables and running migrations.
    
    This function ensures:
    1. Database file exists
    2. All tables are created
    3. All migrations are applied
    4. Schema is verified
    
    Returns:
        bool: True if successful, False otherwise
    """
    from app.database.manager import DatabaseManager
    
    manager = DatabaseManager()
    return manager.initialize(run_migrations=True, verify_schema=True)

if __name__ == "__main__":
    success = init_db()
    sys.exit(0 if success else 1)

