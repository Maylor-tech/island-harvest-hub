"""
WhatsApp Business API integration for Island Harvest Hub.
"""

import json
from typing import Dict, List, Optional
from datetime import datetime

class WhatsAppService:
    """Service for WhatsApp Business API integration."""
    
    def __init__(self):
        """Initialize WhatsApp service."""
        # In production, these would come from environment variables
        self.api_token = "YOUR_WHATSAPP_API_TOKEN"
        self.phone_number_id = "YOUR_PHONE_NUMBER_ID"
        self.base_url = "https://graph.facebook.com/v17.0"
        
    def send_message(self, to_number: str, message: str) -> Dict:
        """
        Send a WhatsApp message.
        
        Args:
            to_number: Recipient phone number
            message: Message content
            
        Returns:
            Response from WhatsApp API
        """
        # This is a mock implementation for demonstration
        # In production, you would make actual API calls
        return {
            "success": True,
            "message_id": f"msg_{datetime.now().timestamp()}",
            "status": "sent",
            "timestamp": datetime.now().isoformat()
        }
    
    def send_template_message(self, to_number: str, template_name: str, 
                            parameters: List[str] = None) -> Dict:
        """
        Send a WhatsApp template message.
        
        Args:
            to_number: Recipient phone number
            template_name: Name of the approved template
            parameters: Template parameters
            
        Returns:
            Response from WhatsApp API
        """
        # Mock implementation
        return {
            "success": True,
            "message_id": f"tmpl_{datetime.now().timestamp()}",
            "template": template_name,
            "status": "sent",
            "timestamp": datetime.now().isoformat()
        }
    
    def get_message_templates(self) -> List[Dict]:
        """
        Get available WhatsApp message templates for Jamaica farm-to-table business.
        
        Returns:
            List of message templates
        """
        return [
            {
                "name": "order_confirmation",
                "category": "order_updates",
                "title": "Order Confirmation",
                "content": "Hello {customer_name}! Your order #{order_id} has been confirmed. We'll deliver fresh {products} to {address} on {delivery_date}. Total: ${amount}. Thanks for supporting local farmers! 🌱",
                "parameters": ["customer_name", "order_id", "products", "address", "delivery_date", "amount"]
            },
            {
                "name": "delivery_reminder",
                "category": "delivery_updates",
                "title": "Delivery Reminder",
                "content": "Good morning {customer_name}! Your fresh produce delivery is scheduled for today between {time_window}. Our driver will contact you 30 minutes before arrival. Have a great day! 🚚🥬",
                "parameters": ["customer_name", "time_window"]
            },
            {
                "name": "payment_reminder",
                "category": "payment_updates",
                "title": "Payment Reminder",
                "content": "Hi {customer_name}, this is a friendly reminder that payment for invoice #{invoice_id} (${amount}) is due on {due_date}. You can pay via bank transfer or mobile money. Thanks! 💰",
                "parameters": ["customer_name", "invoice_id", "amount", "due_date"]
            },
            {
                "name": "new_product_alert",
                "category": "marketing",
                "title": "New Product Alert",
                "content": "🌟 Exciting news {customer_name}! We now have fresh {product_name} from {farm_name} available. Perfect for {season} cooking! Order now for next delivery. Limited quantity! 🥭🥥",
                "parameters": ["customer_name", "product_name", "farm_name", "season"]
            },
            {
                "name": "farmer_pickup_reminder",
                "category": "supplier_updates",
                "title": "Pickup Reminder",
                "content": "Good morning {farmer_name}! Reminder: We'll be picking up {products} from your farm today at {pickup_time}. Please have everything ready. Thanks for your quality produce! 🚜",
                "parameters": ["farmer_name", "products", "pickup_time"]
            },
            {
                "name": "quality_feedback",
                "category": "supplier_updates",
                "title": "Quality Feedback",
                "content": "Hi {farmer_name}, great news! Your {products} received excellent quality ratings from our customers. Keep up the fantastic work! Your dedication to quality makes Island Harvest Hub proud. 🌟⭐",
                "parameters": ["farmer_name", "products"]
            },
            {
                "name": "seasonal_greeting",
                "category": "relationship",
                "title": "Seasonal Greeting",
                "content": "Happy {season} {name}! 🌴 As we celebrate this beautiful time in Jamaica, we're grateful for your partnership with Island Harvest Hub. Wishing you and your family health and prosperity! 🙏",
                "parameters": ["season", "name"]
            },
            {
                "name": "weather_alert",
                "category": "alerts",
                "title": "Weather Alert",
                "content": "⚠️ Weather Alert: {weather_condition} expected in Portland Parish. Please secure your crops and adjust pickup schedules if needed. Stay safe! We'll update delivery schedules as necessary. 🌧️",
                "parameters": ["weather_condition"]
            }
        ]
    
    def format_template_message(self, template_name: str, parameters: Dict[str, str]) -> str:
        """
        Format a template message with parameters.
        
        Args:
            template_name: Name of the template
            parameters: Dictionary of parameter values
            
        Returns:
            Formatted message content
        """
        templates = self.get_message_templates()
        template = next((t for t in templates if t["name"] == template_name), None)
        
        if not template:
            return f"Template '{template_name}' not found"
        
        content = template["content"]
        for param, value in parameters.items():
            content = content.replace(f"{{{param}}}", str(value))
        
        return content
    
    def validate_phone_number(self, phone_number: str) -> bool:
        """
        Validate Jamaica phone number format.
        
        Args:
            phone_number: Phone number to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Remove all non-digit characters
        digits = ''.join(filter(str.isdigit, phone_number))
        
        # Jamaica phone numbers: +1-876-XXX-XXXX or 876-XXX-XXXX
        if len(digits) == 11 and digits.startswith('1876'):
            return True
        elif len(digits) == 10 and digits.startswith('876'):
            return True
        elif len(digits) == 7:  # Local format
            return True
        
        return False
    
    def format_phone_number(self, phone_number: str) -> str:
        """
        Format phone number for WhatsApp API.
        
        Args:
            phone_number: Raw phone number
            
        Returns:
            Formatted phone number
        """
        digits = ''.join(filter(str.isdigit, phone_number))
        
        if len(digits) == 7:
            return f"1876{digits}"
        elif len(digits) == 10 and digits.startswith('876'):
            return f"1{digits}"
        elif len(digits) == 11 and digits.startswith('1876'):
            return digits
        
        return digits

