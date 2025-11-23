"""
Database Management Interface for Island Harvest Hub.
"""

import streamlit as st
import os
import json
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sqlite3
import time
import threading
from queue import Queue

# Add parent directory to path to import db_manager
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_manager import DatabaseManager

# Global variables for real-time monitoring
performance_metrics = Queue()
monitoring_active = False

def format_size(size_bytes):
    """Format size in bytes to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} GB"

def load_stats_report():
    """Load the latest stats report."""
    reports_dir = Path("database_reports")
    if not reports_dir.exists():
        return None
    
    stats_files = list(reports_dir.glob("stats_*.json"))
    if not stats_files:
        return None
    
    latest_stats = max(stats_files, key=lambda x: x.stat().st_mtime)
    with open(latest_stats, 'r') as f:
        return json.load(f)

def get_detailed_performance_metrics():
    """Get detailed performance metrics from SQLite."""
    metrics = {}
    try:
        # Try multiple possible database locations
        db_paths = [
            'island_harvest_hub.db',
            'island_harvest_hub/island_harvest_hub.db',
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'island_harvest_hub.db')
        ]
        
        conn = None
        for db_path in db_paths:
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                break
        
        if not conn:
            return {}
        cursor = conn.cursor()
        
        # Get database size
        cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
        result = cursor.fetchone()
        metrics['size'] = result[0] if result else 0
        
        # Get table statistics
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        table_stats = {}
        for table in tables:
            if table and len(table) > 0:
                table_name = table[0]
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    row_result = cursor.fetchone()
                    row_count = row_result[0] if row_result else 0
                    
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = cursor.fetchall()
                    column_count = len(columns) if columns else 0
                    
                    table_stats[table_name] = {
                        'rows': row_count,
                        'columns': column_count
                    }
                except Exception:
                    # Skip tables that can't be accessed
                    continue
        
        metrics['tables'] = table_stats
        
        # Get index statistics
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = cursor.fetchall()
        metrics['index_count'] = len(indexes) if indexes else 0
        
        # Get cache statistics
        cursor.execute("PRAGMA cache_size")
        cache_result = cursor.fetchone()
        metrics['cache_size'] = cache_result[0] if cache_result else 0
        
        # Get memory usage
        cursor.execute("PRAGMA memory_usage")
        memory_result = cursor.fetchone()
        metrics['memory_usage'] = memory_result[0] if memory_result else 0
        
        conn.close()
        return metrics
    except Exception as e:
        # Return empty dict instead of None to avoid subscriptable errors
        return {}

def monitor_performance():
    """Background thread for real-time performance monitoring."""
    global monitoring_active
    while monitoring_active:
        metrics = get_detailed_performance_metrics()
        if metrics:
            performance_metrics.put({
                'timestamp': datetime.now(),
                'metrics': metrics
            })
        time.sleep(5)  # Update every 5 seconds

def start_monitoring():
    """Start performance monitoring in background thread."""
    global monitoring_active
    if not monitoring_active:
        monitoring_active = True
        thread = threading.Thread(target=monitor_performance)
        thread.daemon = True
        thread.start()

def stop_monitoring():
    """Stop performance monitoring."""
    global monitoring_active
    monitoring_active = False

def main():
    # Only set page config if running as standalone (not imported)
    # When imported from main.py, page config is already set
    try:
        st.set_page_config(
            page_title="Database Management - Island Harvest Hub",
            page_icon="🗄️",
            layout="wide"
        )
    except Exception:
        # Page config already set by main.py, ignore
        pass
    
    st.title("🗄️ Database Management")
    
    # Initialize database manager
    db_manager = DatabaseManager()
    
    # Sidebar for actions
    st.sidebar.title("Actions")
    
    if st.sidebar.button("🔄 Refresh Stats"):
        st.rerun()
    
    if st.sidebar.button("💾 Create Backup"):
        with st.spinner("Creating backup..."):
            backup_path = db_manager.create_backup("manual")
            if backup_path:
                st.sidebar.success(f"Backup created: {os.path.basename(backup_path)}")
            else:
                st.sidebar.error("Failed to create backup")
    
    if st.sidebar.button("⚡ Optimize Database"):
        with st.spinner("Optimizing database..."):
            if db_manager.optimize_database():
                st.sidebar.success("Database optimized successfully")
            else:
                st.sidebar.error("Failed to optimize database")
    
    # Real-time monitoring toggle
    monitoring_enabled = st.sidebar.checkbox("Enable Real-time Monitoring", value=False)
    if monitoring_enabled:
        start_monitoring()
    else:
        stop_monitoring()
    
    # Main content
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Database Statistics")
        
        # Load and display stats
        stats = load_stats_report()
        if stats and isinstance(stats, dict):
            st.success("Database statistics loaded successfully!")
            st.metric("Database Size", stats.get('size', 'N/A'))
            st.metric("Total Tables", stats.get('tables', 'N/A'))
            st.metric("Total Records", stats.get('records', 'N/A'))
            
            # Table sizes chart (if available)
            if stats.get('table_sizes'):
                table_sizes = pd.DataFrame(stats['table_sizes'].items(), 
                                         columns=['Table', 'Rows'])
                fig = px.bar(table_sizes, x='Table', y='Rows',
                            title='Table Sizes')
                st.plotly_chart(fig)
        else:
            st.info("Click 'Refresh Stats' to see performance metrics")
    
    with col2:
        st.subheader("📦 Backup Management")
        
        # List backups
        backups_dir = Path("database_backups")
        if backups_dir.exists():
            backups = list(backups_dir.glob("backup_*.db"))
            if backups:
                for backup in sorted(backups, key=lambda x: x.stat().st_mtime, reverse=True):
                    with st.expander(f"📦 {backup.name}"):
                        st.write(f"Size: {format_size(backup.stat().st_size)}")
                        st.write(f"Created: {datetime.fromtimestamp(backup.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("🔍 Verify", key=f"verify_{backup.name}"):
                                with st.spinner("Verifying backup..."):
                                    if db_manager.verify_backup(str(backup)):
                                        st.success("Backup verified successfully")
                                    else:
                                        st.error("Backup verification failed")
                        
                        with col2:
                            if st.button("🗑️ Delete", key=f"delete_{backup.name}"):
                                try:
                                    backup.unlink()
                                    st.success("Backup deleted")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Failed to delete backup: {str(e)}")
            else:
                st.info("No backups found")
        else:
            st.info("Backup directory not found")
    
    # Performance Metrics Section
    st.subheader("📈 Performance Metrics")
    
    # Get detailed metrics
    try:
        metrics = get_detailed_performance_metrics()
        if metrics and isinstance(metrics, dict) and metrics.get('tables'):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Memory Usage", format_size(metrics.get('memory_usage', 0)))
                # Get cache_size and ensure it's not negative
                cache_size = metrics.get('cache_size', 0)
                if cache_size < 0:
                    cache_size = 0
                st.metric("Cache Size", format_size(cache_size * 1024))  # Convert pages to bytes
                st.metric("Index Count", metrics.get('index_count', 0))
            
            with col2:
                # Table statistics
                st.write("Table Statistics")
                table_data = []
                for table, stats in metrics.get('tables', {}).items():
                    table_data.append({
                        'Table': table,
                        'Rows': stats.get('rows', 0),
                        'Columns': stats.get('columns', 0)
                    })
                
                if table_data:
                    df = pd.DataFrame(table_data)
                    st.dataframe(df)
            
            with col3:
                # Real-time monitoring chart
                if monitoring_enabled:
                    st.write("Real-time Memory Usage")
                    
                    # Get recent metrics from queue
                    recent_metrics = []
                    while not performance_metrics.empty():
                        recent_metrics.append(performance_metrics.get())
                    
                    if recent_metrics:
                        df = pd.DataFrame([
                            {
                                'timestamp': m['timestamp'],
                                'memory_usage': m['metrics'].get('memory_usage', 0)
                            }
                            for m in recent_metrics
                        ])
                        
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=df['timestamp'],
                            y=df['memory_usage'],
                            mode='lines+markers',
                            name='Memory Usage'
                        ))
                        
                        fig.update_layout(
                            title='Memory Usage Over Time',
                            xaxis_title='Time',
                            yaxis_title='Memory Usage (bytes)'
                        )
                        
                        st.plotly_chart(fig)
        else:
            st.info("Click 'Refresh Stats' to see performance metrics")
    except Exception as e:
        st.warning(f"Unable to load performance metrics: {str(e)}")
        st.info("Click 'Refresh Stats' to try again")
    
    # Email notifications section
    st.subheader("📧 Email Notifications")
    
    # Load email config
    config_path = Path("email_config.json")
    if config_path.exists():
        with open(config_path, 'r') as f:
            email_config = json.load(f)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("Current Settings:")
            # Safely display email config
            st.write(f"SMTP Server: {email_config.get('smtp_server', 'Not configured')}")
            st.write(f"SMTP Port: {email_config.get('smtp_port', 'Not configured')}")
            st.write(f"Sender Email: {email_config.get('sender_email', 'Not configured')}")
            st.write(f"Recipient Email: {email_config.get('recipient_email', 'Not configured')}")
            st.write(f"Notifications Enabled: {email_config.get('enable_notifications', False)}")
        
        with col2:
            st.write("Update Settings:")
            with st.form("email_settings"):
                new_smtp = st.text_input("SMTP Server", value=email_config.get('smtp_server', ''))
                new_sender = st.text_input("Sender Email", value=email_config.get('sender_email', ''))
                new_recipient = st.text_input("Recipient Email", value=email_config.get('recipient_email', ''))
                new_enabled = st.checkbox("Enable Notifications", value=email_config.get('enable_notifications', False))
                
                if st.form_submit_button("Update Settings"):
                    email_config.update({
                        'smtp_server': new_smtp,
                        'sender_email': new_sender,
                        'recipient_email': new_recipient,
                        'enable_notifications': new_enabled
                    })
                    
                    with open(config_path, 'w') as f:
                        json.dump(email_config, f, indent=4)
                    
                    st.success("Email settings updated")
    else:
        st.warning("Email configuration file not found")

if __name__ == "__main__":
    main() 