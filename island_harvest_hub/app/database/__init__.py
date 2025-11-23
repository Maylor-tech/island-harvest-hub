"""
Database package for Island Harvest Hub.

Provides:
- Database configuration with absolute paths
- Migration system
- Schema verification
- Database management utilities
"""

from .config import (
    DATABASE_PATH,
    DATABASE_URL,
    SQLALCHEMY_DATABASE_URI,
    engine,
    SessionLocal,
    Base,
    get_db,
    get_database_path,
    init_db
)
from .manager import DatabaseManager
from .migrations import MigrationRunner
from .schema import SchemaVerifier

__all__ = [
    'DATABASE_PATH',
    'DATABASE_URL',
    'SQLALCHEMY_DATABASE_URI',
    'engine',
    'SessionLocal',
    'Base',
    'get_db',
    'get_database_path',
    'init_db',
    'DatabaseManager',
    'MigrationRunner',
    'SchemaVerifier',
]

