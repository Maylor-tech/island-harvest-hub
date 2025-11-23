"""
Email notification service for Island Harvest Hub database management.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import logging
from pathlib import Path
from datetime import datetime

class EmailNotifier:
    def __init__(self, config_file='email_config.json'):
        self.config_file = config_file
        self.config = self._load_config()
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('email_notifier.log'),
                logging.StreamHandler()
            ]
        )
    
    def _load_config(self):
        """Load email configuration from file."""
        try:
            if Path(self.config_file).exists():
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            else:
                # Create default config
                default_config = {
                    'smtp_server': 'smtp.gmail.com',
                    'smtp_port': 587,
                    'sender_email': 'your-email@gmail.com',
                    'sender_password': 'your-app-password',
                    'recipient_email': 'your-email@gmail.com',
                    'enable_notifications': False
                }
                with open(self.config_file, 'w') as f:
                    json.dump(default_config, f, indent=4)
                return default_config
        except Exception as e:
            logging.error(f"Error loading email config: {str(e)}")
            return None
    
    def send_notification(self, subject, message, is_html=False):
        """Send email notification."""
        if not self.config or not self.config.get('enable_notifications'):
            logging.info("Email notifications are disabled")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config['sender_email']
            msg['To'] = self.config['recipient_email']
            msg['Subject'] = f"Island Harvest Hub - {subject}"
            
            # Attach message
            if is_html:
                msg.attach(MIMEText(message, 'html'))
            else:
                msg.attach(MIMEText(message, 'plain'))
            
            # Connect to SMTP server
            if self.config['smtp_port'] == 465:
                server = smtplib.SMTP_SSL(self.config['smtp_server'], self.config['smtp_port'])
            else:
                server = smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port'])
                server.starttls()
            
            server.login(self.config['sender_email'], self.config['sender_password'])
            
            # Send email
            server.send_message(msg)
            server.quit()
            
            logging.info(f"Email notification sent: {subject}")
            return True
        except Exception as e:
            logging.error(f"Error sending email notification: {str(e)}")
            return False
    
    def send_backup_notification(self, backup_path, backup_size, backup_type):
        """Send backup completion notification."""
        subject = f"Database Backup Completed - {backup_type}"
        
        message = f"""
        Island Harvest Hub Database Backup Notification
        
        Backup Details:
        - Type: {backup_type}
        - Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        - Location: {backup_path}
        - Size: {backup_size:.2f} MB
        
        The backup has been successfully created and verified.
        """
        
        return self.send_notification(subject, message)
    
    def send_error_notification(self, error_type, error_message):
        """Send error notification."""
        subject = f"Database Error Alert - {error_type}"
        
        message = f"""
        Island Harvest Hub Database Error Alert
        
        Error Details:
        - Type: {error_type}
        - Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        - Message: {error_message}
        
        Please check the database management logs for more details.
        """
        
        return self.send_notification(subject, message)
    
    def send_monthly_report(self, report_path, stats):
        """Send monthly report notification."""
        subject = "Monthly Database Report"
        
        # Create HTML message
        html_message = f"""
        <html>
        <head>
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
            <h1>Island Harvest Hub Monthly Database Report</h1>
            <h2>{datetime.now().strftime('%B %Y')}</h2>
            
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
                    </tr>
        """
        
        for table, count in stats['table_sizes'].items():
            html_message += f"""
                    <tr>
                        <td>{table}</td>
                        <td>{count}</td>
                    </tr>
            """
        
        html_message += """
                </table>
            </div>
            
            <p>The full report is available at: {report_path}</p>
        </body>
        </html>
        """
        
        return self.send_notification(subject, html_message, is_html=True)

def main():
    """Test email notification system."""
    notifier = EmailNotifier()
    
    # Test basic notification
    notifier.send_notification(
        "Test Notification",
        "This is a test notification from the Island Harvest Hub database management system."
    )
    
    # Test backup notification
    notifier.send_backup_notification(
        "database_backups/backup_daily_20240115.db",
        1.5,
        "Daily Backup"
    )
    
    # Test error notification
    notifier.send_error_notification(
        "Backup Failed",
        "Failed to create daily backup due to insufficient disk space."
    )

if __name__ == "__main__":
    main() 