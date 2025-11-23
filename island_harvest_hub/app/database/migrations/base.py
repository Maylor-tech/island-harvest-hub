"""
Base migration class for Island Harvest Hub.
"""

from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime


class Migration(ABC):
    """Base class for database migrations."""
    
    def __init__(self, version: str, description: str):
        """
        Initialize migration.
        
        Args:
            version: Migration version (e.g., "001", "002")
            description: Human-readable description
        """
        self.version = version
        self.description = description
        self.applied_at: Optional[datetime] = None
    
    @abstractmethod
    def up(self, connection):
        """
        Apply the migration.
        
        Args:
            connection: SQLAlchemy connection object
        """
        pass
    
    @abstractmethod
    def down(self, connection):
        """
        Rollback the migration (optional).
        
        Args:
            connection: SQLAlchemy connection object
        """
        pass
    
    def __repr__(self):
        return f"Migration(version={self.version}, description={self.description})"

