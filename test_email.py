"""
Test script for EmailService
Run this to test your email configuration
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock streamlit to avoid errors when running outside Streamlit
class MockStreamlit:
    def error(self, msg):
        print(f"ERROR: {msg}")

sys.modules['streamlit'] = MockStreamlit()

# Now import the email service
from island_harvest_hub.app.services.email_service import EmailService

if __name__ == "__main__":
    print("Testing Email Service...")
    print("-" * 50)
    
    try:
        email_service = EmailService()
        status, msg = email_service.send_test_email()
        
        print(f"Status: {status}")
        print(f"Message: {msg}")
        
        if status:
            print("\n[SUCCESS] Email sent successfully!")
        else:
            print("\n[FAILED] Email failed. Check your email_config.json settings.")
            
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()

