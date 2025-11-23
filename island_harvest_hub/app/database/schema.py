"""
Schema verification utilities for Island Harvest Hub database.
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional
from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


class SchemaVerifier:
    """Verify database schema and provide diagnostic information."""
    
    def __init__(self, engine: Engine, database_path: Path):
        """
        Initialize schema verifier.
        
        Args:
            engine: SQLAlchemy engine
            database_path: Path to database file
        """
        self.engine = engine
        self.database_path = database_path
        self.inspector = inspect(engine)
    
    def verify_database_exists(self) -> bool:
        """Check if database file exists."""
        return self.database_path.exists()
    
    def get_database_info(self) -> Dict:
        """Get basic database information."""
        info = {
            'path': str(self.database_path),
            'exists': self.database_path.exists(),
            'size_kb': 0,
            'tables': []
        }
        
        if self.database_path.exists():
            info['size_kb'] = self.database_path.stat().st_size / 1024
        
        try:
            info['tables'] = self.inspector.get_table_names()
        except Exception:
            pass
        
        return info
    
    def get_table_schema(self, table_name: str) -> Dict:
        """Get schema information for a specific table."""
        if table_name not in self.inspector.get_table_names():
            return {'error': f'Table {table_name} does not exist'}
        
        schema = {
            'name': table_name,
            'columns': [],
            'primary_key': None,
            'foreign_keys': [],
            'indexes': []
        }
        
        # Get columns
        columns = self.inspector.get_columns(table_name)
        for col in columns:
            schema['columns'].append({
                'name': col['name'],
                'type': str(col['type']),
                'nullable': col['nullable'],
                'default': col.get('default')
            })
        
        # Get primary key
        pk_constraint = self.inspector.get_pk_constraint(table_name)
        if pk_constraint['constrained_columns']:
            schema['primary_key'] = pk_constraint['constrained_columns']
        
        # Get foreign keys
        fk_constraints = self.inspector.get_foreign_keys(table_name)
        for fk in fk_constraints:
            schema['foreign_keys'].append({
                'columns': fk['constrained_columns'],
                'referred_table': fk['referred_table'],
                'referred_columns': fk['referred_columns']
            })
        
        # Get indexes
        indexes = self.inspector.get_indexes(table_name)
        for idx in indexes:
            schema['indexes'].append({
                'name': idx['name'],
                'columns': idx['column_names'],
                'unique': idx['unique']
            })
        
        return schema
    
    def get_table_row_count(self, table_name: str) -> int:
        """Get row count for a table."""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                return result.scalar()
        except Exception:
            return -1
    
    def get_all_table_row_counts(self) -> Dict[str, int]:
        """Get row counts for all tables."""
        counts = {}
        tables = self.inspector.get_table_names()
        
        for table_name in tables:
            counts[table_name] = self.get_table_row_count(table_name)
        
        return counts
    
    def check_column_exists(self, table_name: str, column_name: str) -> bool:
        """Check if a column exists in a table."""
        if table_name not in self.inspector.get_table_names():
            return False
        
        columns = [col['name'] for col in self.inspector.get_columns(table_name)]
        return column_name in columns
    
    def verify_schema(self, expected_tables: List[str]) -> Dict:
        """
        Verify database schema against expected tables.
        
        Args:
            expected_tables: List of expected table names
            
        Returns:
            Dictionary with verification results
        """
        actual_tables = set(self.inspector.get_table_names())
        expected_tables_set = set(expected_tables)
        
        missing_tables = expected_tables_set - actual_tables
        extra_tables = actual_tables - expected_tables_set
        
        return {
            'valid': len(missing_tables) == 0,
            'missing_tables': list(missing_tables),
            'extra_tables': list(extra_tables),
            'expected_count': len(expected_tables),
            'actual_count': len(actual_tables)
        }
    
    def print_schema_report(self) -> None:
        """Print a comprehensive schema report."""
        info = self.get_database_info()
        
        print("=" * 80)
        print("DATABASE SCHEMA VERIFICATION")
        print("=" * 80)
        print(f"\nDatabase Path: {info['path']}")
        print(f"Database Exists: {info['exists']}")
        if info['exists']:
            print(f"Database Size: {info['size_kb']:.2f} KB")
        print(f"Total Tables: {len(info['tables'])}")
        print("\n" + "-" * 80)
        
        # Print schema for each table
        for table_name in sorted(info['tables']):
            schema = self.get_table_schema(table_name)
            if 'error' in schema:
                print(f"\n[ERROR] {table_name}: {schema['error']}")
                continue
            
            print(f"\n[Table] {table_name}")
            print("-" * 40)
            print("Columns:")
            for col in schema['columns']:
                nullable = "NULL" if col['nullable'] else "NOT NULL"
                default = f" DEFAULT {col['default']}" if col.get('default') is not None else ""
                print(f"  - {col['name']}: {col['type']} {nullable}{default}")
            
            if schema['primary_key']:
                print(f"Primary Key: {', '.join(schema['primary_key'])}")
            
            if schema['foreign_keys']:
                print("Foreign Keys:")
                for fk in schema['foreign_keys']:
                    print(f"  - {', '.join(fk['columns'])} -> {fk['referred_table']}.{', '.join(fk['referred_columns'])}")
            
            if schema['indexes']:
                print("Indexes:")
                for idx in schema['indexes']:
                    unique = "UNIQUE " if idx['unique'] else ""
                    print(f"  - {unique}{idx['name']}: {', '.join(idx['columns'])}")
        
        # Print row counts
        print("\n" + "=" * 80)
        print("ROW COUNTS")
        print("=" * 80)
        print(f"\n{'Table Name':<30} {'Row Count':<15} {'Status'}")
        print("-" * 80)
        
        row_counts = self.get_all_table_row_counts()
        total_rows = 0
        
        for table_name in sorted(row_counts.keys()):
            count = row_counts[table_name]
            if count >= 0:
                total_rows += count
                status = "[OK]"
            else:
                count = "Error"
                status = "[ERROR]"
            print(f"{table_name:<30} {str(count):<15} {status}")
        
        print("-" * 80)
        print(f"{'TOTAL':<30} {str(total_rows):<15} [OK]")
        print("=" * 80)

