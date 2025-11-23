"""
Database management script for Island Harvest Hub AI Assistant.
Handles backups, monitoring, and maintenance tasks.
"""

import os
import shutil
import sqlite3
from datetime import datetime, timedelta
import json
import logging
from pathlib import Path
import sys
import hashlib
from email_notifier import EmailNotifier

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('db_manager.log'),
        logging.StreamHandler()
    ]
)

class DatabaseManager:
    def __init__(self, db_path='island_harvest_hub.db'):
        self.db_path = db_path
        self.backup_dir = 'database_backups'
        self.stats_dir = 'database_stats'
        self.reports_dir = 'database_reports'
        self.notifier = EmailNotifier()
        
        # Create necessary directories
        Path(self.backup_dir).mkdir(exist_ok=True)
        Path(self.stats_dir).mkdir(exist_ok=True)
        Path(self.reports_dir).mkdir(exist_ok=True)
    
    def get_database_size(self):
        """Get current database size in MB."""
        try:
            size_bytes = os.path.getsize(self.db_path)
            size_mb = size_bytes / (1024 * 1024)
            return round(size_mb, 2)
        except Exception as e:
            logging.error(f"Error getting database size: {str(e)}")
            self.notifier.send_error_notification("Database Size Error", str(e))
            return None
    
    def get_table_sizes(self):
        """Get size of each table in the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get list of tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            table_sizes = {}
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                row_count = cursor.fetchone()[0]
                table_sizes[table_name] = row_count
            
            conn.close()
            return table_sizes
        except Exception as e:
            logging.error(f"Error getting table sizes: {str(e)}")
            self.notifier.send_error_notification("Table Size Error", str(e))
            return None
    
    def get_table_statistics(self):
        """Get detailed statistics for each table."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            stats = {}
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            for table in tables:
                table_name = table[0]
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                row_count = cursor.fetchone()[0]
                
                stats[table_name] = {
                    'columns': len(columns),
                    'rows': row_count,
                    'column_names': [col[1] for col in columns]
                }
            
            conn.close()
            return stats
        except Exception as e:
            logging.error(f"Error getting table statistics: {str(e)}")
            self.notifier.send_error_notification("Table Statistics Error", str(e))
            return None
    
    def verify_backup(self, backup_path):
        """Verify backup integrity."""
        try:
            # Check if backup file exists
            if not os.path.exists(backup_path):
                raise FileNotFoundError(f"Backup file not found: {backup_path}")
            
            # Try to open and verify the backup database
            conn = sqlite3.connect(backup_path)
            cursor = conn.cursor()
            
            # Check if we can read tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            if not tables:
                raise ValueError("Backup database contains no tables")
            
            # Calculate backup checksum
            with open(backup_path, 'rb') as f:
                backup_checksum = hashlib.sha256(f.read()).hexdigest()
            
            conn.close()
            
            # Save checksum for future verification
            checksum_file = f"{backup_path}.checksum"
            with open(checksum_file, 'w') as f:
                f.write(backup_checksum)
            
            return True
        except Exception as e:
            logging.error(f"Error verifying backup: {str(e)}")
            self.notifier.send_error_notification("Backup Verification Error", str(e))
            return False
    
    def create_backup(self, backup_type='daily'):
        """Create a database backup."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"backup_{backup_type}_{timestamp}.db"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # Create backup
            shutil.copy2(self.db_path, backup_path)
            
            # Verify backup
            if not self.verify_backup(backup_path):
                raise Exception("Backup verification failed")
            
            # Get backup size
            backup_size = os.path.getsize(backup_path) / (1024 * 1024)  # Convert to MB
            
            # Log backup creation
            logging.info(f"Created {backup_type} backup: {backup_filename}")
            
            # Send backup notification
            self.notifier.send_backup_notification(backup_path, backup_size, backup_type)
            
            # Clean up old backups
            self.cleanup_old_backups()
            
            return backup_path
        except Exception as e:
            logging.error(f"Error creating backup: {str(e)}")
            self.notifier.send_error_notification("Backup Creation Error", str(e))
            return None
    
    def cleanup_old_backups(self, keep_daily=7, keep_weekly=4, keep_monthly=12):
        """Clean up old backup files."""
        try:
            backups = os.listdir(self.backup_dir)
            now = datetime.now()
            
            for backup in backups:
                if not backup.startswith('backup_'):
                    continue
                
                backup_path = os.path.join(self.backup_dir, backup)
                backup_time = datetime.fromtimestamp(os.path.getctime(backup_path))
                age = now - backup_time
                
                # Delete old backups based on type
                if backup.startswith('backup_daily_') and age.days > keep_daily:
                    os.remove(backup_path)
                    if os.path.exists(f"{backup_path}.checksum"):
                        os.remove(f"{backup_path}.checksum")
                    logging.info(f"Deleted old daily backup: {backup}")
                elif backup.startswith('backup_weekly_') and age.days > (keep_weekly * 7):
                    os.remove(backup_path)
                    if os.path.exists(f"{backup_path}.checksum"):
                        os.remove(f"{backup_path}.checksum")
                    logging.info(f"Deleted old weekly backup: {backup}")
                elif backup.startswith('backup_monthly_') and age.days > (keep_monthly * 30):
                    os.remove(backup_path)
                    if os.path.exists(f"{backup_path}.checksum"):
                        os.remove(f"{backup_path}.checksum")
                    logging.info(f"Deleted old monthly backup: {backup}")
        except Exception as e:
            logging.error(f"Error cleaning up old backups: {str(e)}")
            self.notifier.send_error_notification("Backup Cleanup Error", str(e))
    
    def optimize_database(self):
        """Optimize database performance."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Run VACUUM to optimize database
            cursor.execute("VACUUM;")
            
            # Analyze tables for better query planning
            cursor.execute("ANALYZE;")
            
            # Update statistics
            cursor.execute("PRAGMA optimize;")
            
            conn.close()
            logging.info("Database optimization completed")
            return True
        except Exception as e:
            logging.error(f"Error optimizing database: {str(e)}")
            self.notifier.send_error_notification("Database Optimization Error", str(e))
            return False
    
    def generate_stats_report(self):
        """Generate database statistics report."""
        try:
            stats = {
                'timestamp': datetime.now().isoformat(),
                'database_size_mb': self.get_database_size(),
                'table_sizes': self.get_table_sizes(),
                'table_statistics': self.get_table_statistics(),
                'backup_count': len(os.listdir(self.backup_dir))
            }
            
            # Save stats to file
            stats_file = os.path.join(self.stats_dir, f"stats_{datetime.now().strftime('%Y%m%d')}.json")
            with open(stats_file, 'w') as f:
                json.dump(stats, f, indent=4)
            
            logging.info(f"Generated stats report: {stats_file}")
            return stats
        except Exception as e:
            logging.error(f"Error generating stats report: {str(e)}")
            self.notifier.send_error_notification("Stats Report Error", str(e))
            return None
    
    def generate_monthly_report(self):
        """Generate a detailed monthly report."""
        try:
            # Get all stats
            stats = self.generate_stats_report()
            
            # Generate HTML report
            report_date = datetime.now().strftime('%B %Y')
            report_file = os.path.join(self.reports_dir, f"monthly_report_{datetime.now().strftime('%Y%m')}.html")
            
            html_content = f"""
            <html>
            <head>
                <title>Island Harvest Hub Database Report - {report_date}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    h1, h2 {{ color: #2c3e50; }}
                    .section {{ margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 5px; }}
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                </style>
            </head>
            <body>
                <h1>Island Harvest Hub Database Report</h1>
                <h2>{report_date}</h2>
                
                <div class="section">
                    <h3>Database Overview</h3>
                    <p>Total Size: {stats['database_size_mb']} MB</p>
                    <p>Total Tables: {len(stats['table_sizes'])}</p>
                    <p>Total Backups: {stats['backup_count']}</p>
                </div>
                
                <div class="section">
                    <h3>Table Statistics</h3>
                    <table>
                        <tr>
                            <th>Table Name</th>
                            <th>Rows</th>
                            <th>Columns</th>
                        </tr>
            """
            
            for table_name, table_stats in stats['table_statistics'].items():
                html_content += f"""
                        <tr>
                            <td>{table_name}</td>
                            <td>{table_stats['rows']}</td>
                            <td>{table_stats['columns']}</td>
                        </tr>
                """
            
            html_content += """
                    </table>
                </div>
                
                <div class="section">
                    <h3>Column Details</h3>
            """
            
            for table_name, table_stats in stats['table_statistics'].items():
                html_content += f"""
                    <h4>{table_name}</h4>
                    <ul>
                """
                for column in table_stats['column_names']:
                    html_content += f"<li>{column}</li>"
                html_content += "</ul>"
            
            html_content += """
                </div>
            </body>
            </html>
            """
            
            with open(report_file, 'w') as f:
                f.write(html_content)
            
            logging.info(f"Generated monthly report: {report_file}")
            
            # Send monthly report notification
            self.notifier.send_monthly_report(report_file, stats)
            
            return report_file
        except Exception as e:
            logging.error(f"Error generating monthly report: {str(e)}")
            self.notifier.send_error_notification("Monthly Report Error", str(e))
            return None

def main():
    """Main function to run database management tasks."""
    db_manager = DatabaseManager()
    
    # Check command line arguments for task type
    task_type = sys.argv[1] if len(sys.argv) > 1 else 'daily'
    
    if task_type == 'daily':
        # Daily backup and basic stats
        size = db_manager.get_database_size()
        logging.info(f"Current database size: {size} MB")
        
        backup_path = db_manager.create_backup('daily')
        if backup_path:
            logging.info(f"Created backup at: {backup_path}")
    
    elif task_type == 'weekly':
        # Weekly optimization and detailed stats
        if db_manager.optimize_database():
            logging.info("Database optimization completed")
        
        stats = db_manager.generate_stats_report()
        if stats:
            logging.info("Generated detailed statistics report")
    
    elif task_type == 'monthly':
        # Monthly report and cleanup
        report_file = db_manager.generate_monthly_report()
        if report_file:
            logging.info(f"Generated monthly report: {report_file}")
        
        # Clean up old backups
        db_manager.cleanup_old_backups()
    
    else:
        logging.error(f"Unknown task type: {task_type}")

if __name__ == "__main__":
    main() 