"""
Migration 001: Add business_id column to customers table if missing.

This migration ensures the customers table has a business_id column.
"""

from sqlalchemy import text, inspect
from app.database.migrations.base import Migration


class Migration001AddBusinessId(Migration):
    """Add business_id column to customers table."""
    
    def __init__(self):
        super().__init__(
            version="001",
            description="Add business_id column to customers table"
        )
    
    def up(self, connection):
        """Apply migration: Add business_id column."""
        inspector = inspect(connection.engine)
        
        # Check if customers table exists
        if 'customers' not in inspector.get_table_names():
            # Table doesn't exist, will be created by init_db
            return
        
        # Check if column already exists
        columns = [col['name'] for col in inspector.get_columns('customers')]
        if 'business_id' in columns:
            # Column already exists, check for NULL values
            result = connection.execute(text("""
                SELECT COUNT(*) FROM customers 
                WHERE business_id IS NULL OR business_id = ''
            """))
            null_count = result.scalar()
            
            if null_count > 0:
                # Update NULL values
                connection.execute(text("""
                    UPDATE customers 
                    SET business_id = 'island_harvest' 
                    WHERE business_id IS NULL OR business_id = ''
                """))
            return
        
        # Column doesn't exist, add it
        connection.execute(text("""
            ALTER TABLE customers 
            ADD COLUMN business_id VARCHAR(50) DEFAULT 'island_harvest'
        """))
        
        # Update any NULL values
        connection.execute(text("""
            UPDATE customers 
            SET business_id = 'island_harvest' 
            WHERE business_id IS NULL OR business_id = ''
        """))
    
    def down(self, connection):
        """Rollback migration: Remove business_id column."""
        # SQLite doesn't support DROP COLUMN directly
        # This would require recreating the table, which is complex
        # For now, we'll just log that rollback is not fully supported
        raise NotImplementedError(
            "Rollback of business_id column requires table recreation. "
            "This is not implemented for safety reasons."
        )

