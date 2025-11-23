"""
WhatsApp Business integration using Twilio for Island Harvest Hub.
Handles automated messaging for orders, invoices, and customer communications.
"""

import json
import os
import streamlit as st
from typing import Dict, Optional, List, Tuple
from datetime import datetime

# Try to import Twilio, but handle gracefully if not available
try:
    from twilio.rest import Client
    from twilio.base.exceptions import TwilioRestException
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    Client = None
    TwilioRestException = Exception


class WhatsAppAutomationService:
    """Service for WhatsApp Business messaging via Twilio."""
    
    def __init__(self, config_path="whatsapp_config.json"):
        """Initialize WhatsApp automation service with Twilio."""
        # Try to load from Streamlit secrets first (for Streamlit Cloud)
        self.config = self.load_config_from_secrets()
        if not self.config:
            # Fallback to config file
            self.config = self.load_config(config_path)
        self.client = None
        
        if self.config and self.config.get("enable_whatsapp"):
            if not TWILIO_AVAILABLE:
                if st:
                    st.warning("⚠️ Twilio package not installed. Install with: pip install twilio")
                return
            try:
                self.client = Client(
                    self.config.get("account_sid"),
                    self.config.get("auth_token")
                )
            except Exception as e:
                if self.config.get("debug", False):
                    st.warning(f"Twilio client initialization failed: {str(e)}")
    
    def load_config_from_secrets(self) -> Optional[Dict]:
        """Load WhatsApp configuration from Streamlit secrets."""
        if hasattr(st, 'secrets'):
            try:
                # Check if whatsapp section exists in secrets
                if 'whatsapp' in st.secrets:
                    whatsapp_secrets = st.secrets['whatsapp']
                    if isinstance(whatsapp_secrets, dict):
                        return {
                            'account_sid': whatsapp_secrets.get('account_sid', ''),
                            'auth_token': whatsapp_secrets.get('auth_token', ''),
                            'twilio_whatsapp_number': whatsapp_secrets.get('twilio_whatsapp_number', ''),
                            'enable_whatsapp': whatsapp_secrets.get('enable_whatsapp', False),
                            'debug': whatsapp_secrets.get('debug', False)
                        }
            except Exception as e:
                # Silently fail if secrets not available
                pass
        return None
    
    def load_config(self, path: str) -> Optional[Dict]:
        """Load WhatsApp configuration from JSON file."""
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception as e:
            if st:
                st.error(f"Error loading WhatsApp config: {str(e)}")
            return None
    
    def send_message(self, to_number: str, message: str) -> Tuple[bool, str]:
        """
        Send a WhatsApp message via Twilio.
        
        Args:
            to_number: Recipient phone number (E.164 format)
            message: Message content
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.config or not self.config.get("enable_whatsapp"):
            return False, "WhatsApp notifications are disabled."
        
        if not TWILIO_AVAILABLE:
            return False, "Twilio package not installed. Install with: pip install twilio"
        
        if not self.client:
            return False, "Twilio client not initialized. Check your configuration."
        
        try:
            # Format phone number if needed
            formatted_number = self.format_phone_number(to_number)
            
            # Get Twilio WhatsApp number from config
            from_number = f"whatsapp:{self.config.get('twilio_whatsapp_number')}"
            to_number_formatted = f"whatsapp:{formatted_number}"
            
            # Send message
            message_obj = self.client.messages.create(
                body=message,
                from_=from_number,
                to=to_number_formatted
            )
            
            if self.config.get("debug", False):
                self._log_message(f"Message sent successfully. SID: {message_obj.sid}")
            
            return True, f"Message sent successfully. SID: {message_obj.sid}"
            
        except TwilioRestException as e:
            error_msg = f"Twilio error: {str(e)}"
            if self.config.get("debug", False):
                self._log_error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            if self.config.get("debug", False):
                self._log_error(error_msg)
            return False, error_msg
    
    def send_template_message(self, template_name: str, to_number: str, 
                            parameters: Dict[str, str]) -> Tuple[bool, str]:
        """
        Send a WhatsApp message using a predefined template.
        
        Args:
            template_name: Name of the message template
            to_number: Recipient phone number
            parameters: Dictionary of template parameters
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        message_content = self.format_template_message(template_name, parameters)
        if not message_content:
            return False, f"Template '{template_name}' not found."
        
        return self.send_message(to_number, message_content)
    
    def send_order_confirmation(self, customer_name: str, customer_phone: str,
                               order_id: int, order_items: List[Dict],
                               delivery_date: str, total_amount: float,
                               delivery_address: str = None) -> Tuple[bool, str]:
        """
        Send order confirmation message to customer.
        
        Args:
            customer_name: Customer's name
            customer_phone: Customer's phone number
            order_id: Order ID
            order_items: List of order items with 'product_name', 'quantity', 'unit_price'
            delivery_date: Scheduled delivery date
            total_amount: Total order amount
            delivery_address: Delivery address (optional)
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        # Format order items
        items_text = "\n".join([
            f"• {item.get('product_name', 'Item')} - Qty: {item.get('quantity', 0)} @ ${item.get('unit_price', 0):.2f}"
            for item in order_items
        ])
        
        address_text = f"\n📍 Delivery Address: {delivery_address}" if delivery_address else ""
        
        message = f"""✅ *Order Confirmation*

Hello {customer_name}!

Your order #{order_id} has been confirmed.

📦 *Order Details:*
{items_text}

💰 *Total Amount:* ${total_amount:.2f}
📅 *Delivery Date:* {delivery_date}{address_text}

We'll deliver fresh produce to you on the scheduled date. Our driver will contact you 30 minutes before arrival.

Thank you for supporting local farmers! 🌱

_Island Harvest Hub_"""
        
        return self.send_message(customer_phone, message)
    
    def send_delivery_notification(self, customer_name: str, customer_phone: str,
                                  order_id: int, delivery_date: str,
                                  time_window: str = "9 AM - 12 PM",
                                  driver_contact: str = None) -> Tuple[bool, str]:
        """
        Send delivery notification to customer.
        
        Args:
            customer_name: Customer's name
            customer_phone: Customer's phone number
            order_id: Order ID
            delivery_date: Delivery date
            time_window: Expected delivery time window
            driver_contact: Driver contact number (optional)
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        driver_text = f"\n📞 Driver Contact: {driver_contact}" if driver_contact else ""
        
        message = f"""🚚 *Delivery Notification*

Good morning {customer_name}!

Your fresh produce delivery for order #{order_id} is scheduled for today.

📅 *Date:* {delivery_date}
⏰ *Time Window:* {time_window}{driver_text}

Our driver will contact you 30 minutes before arrival. Please ensure someone is available to receive the delivery.

Have a great day! 🥬

_Island Harvest Hub_"""
        
        return self.send_message(customer_phone, message)
    
    def send_payment_reminder(self, customer_name: str, customer_phone: str,
                             invoice_id: int, amount: float, due_date: str,
                             payment_methods: str = "bank transfer or mobile money") -> Tuple[bool, str]:
        """
        Send payment reminder to customer.
        
        Args:
            customer_name: Customer's name
            customer_phone: Customer's phone number
            invoice_id: Invoice ID
            amount: Invoice amount
            due_date: Payment due date
            payment_methods: Available payment methods
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        message = f"""💰 *Payment Reminder*

Hi {customer_name},

This is a friendly reminder that payment for invoice #{invoice_id} is due.

📄 *Invoice #:* {invoice_id}
💵 *Amount:* ${amount:.2f}
📅 *Due Date:* {due_date}

You can pay via {payment_methods}.

Thank you for your prompt payment! 🙏

_Island Harvest Hub_"""
        
        return self.send_message(customer_phone, message)
    
    def send_custom_message(self, customer_phone: str, message: str) -> Tuple[bool, str]:
        """
        Send a custom WhatsApp message.
        
        Args:
            customer_phone: Recipient phone number
            message: Custom message content
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        return self.send_message(customer_phone, message)
    
    def format_template_message(self, template_name: str, parameters: Dict[str, str]) -> Optional[str]:
        """
        Format a template message with parameters.
        
        Args:
            template_name: Name of the template
            parameters: Dictionary of parameter values
            
        Returns:
            Formatted message content or None if template not found
        """
        templates = self.get_message_templates()
        template = next((t for t in templates if t["name"] == template_name), None)
        
        if not template:
            return None
        
        content = template["content"]
        for param, value in parameters.items():
            content = content.replace(f"{{{param}}}", str(value))
        
        return content
    
    def get_message_templates(self) -> List[Dict]:
        """
        Get available WhatsApp message templates.
        
        Returns:
            List of message template dictionaries
        """
        return [
            {
                "name": "order_confirmation",
                "category": "order_updates",
                "title": "Order Confirmation",
                "content": """✅ *Order Confirmation*

Hello {customer_name}!

Your order #{order_id} has been confirmed.

📦 *Order Details:*
{order_items}

💰 *Total Amount:* ${total_amount}
📅 *Delivery Date:* {delivery_date}

Thank you for supporting local farmers! 🌱

_Island Harvest Hub_"""
            },
            {
                "name": "delivery_notification",
                "category": "delivery_updates",
                "title": "Delivery Notification",
                "content": """🚚 *Delivery Notification*

Good morning {customer_name}!

Your fresh produce delivery for order #{order_id} is scheduled for today.

📅 *Date:* {delivery_date}
⏰ *Time Window:* {time_window}

Our driver will contact you 30 minutes before arrival.

Have a great day! 🥬

_Island Harvest Hub_"""
            },
            {
                "name": "payment_reminder",
                "category": "payment_updates",
                "title": "Payment Reminder",
                "content": """💰 *Payment Reminder*

Hi {customer_name},

This is a friendly reminder that payment for invoice #{invoice_id} is due.

💵 *Amount:* ${amount}
📅 *Due Date:* {due_date}

You can pay via {payment_methods}.

Thank you! 🙏

_Island Harvest Hub_"""
            },
            {
                "name": "custom_message",
                "category": "custom",
                "title": "Custom Message",
                "content": "{message}"
            }
        ]
    
    def format_phone_number(self, phone_number: str) -> str:
        """
        Format phone number to E.164 format for Twilio.
        
        Args:
            phone_number: Raw phone number
            
        Returns:
            Formatted phone number in E.164 format
        """
        # Remove all non-digit characters
        digits = ''.join(filter(str.isdigit, phone_number))
        
        # Handle different formats
        if len(digits) == 11 and digits.startswith('1876'):
            return digits
        elif len(digits) == 10 and digits.startswith('876'):
            return f"1{digits}"
        elif len(digits) == 7:  # Local Jamaica format
            return f"1876{digits}"
        
        # If already in E.164 format or other format, return as is
        return digits if digits.startswith('1') else f"1{digits}"
    
    def validate_phone_number(self, phone_number: str) -> bool:
        """
        Validate phone number format.
        
        Args:
            phone_number: Phone number to validate
            
        Returns:
            True if valid, False otherwise
        """
        digits = ''.join(filter(str.isdigit, phone_number))
        
        # Jamaica phone numbers: +1-876-XXX-XXXX or 876-XXX-XXXX
        if len(digits) == 11 and digits.startswith('1876'):
            return True
        elif len(digits) == 10 and digits.startswith('876'):
            return True
        elif len(digits) == 7:  # Local format
            return True
        
        return False
    
    def _log_message(self, message: str):
        """Log a message to debug log file."""
        try:
            log_dir = "database_reports"
            os.makedirs(log_dir, exist_ok=True)
            with open(f"{log_dir}/whatsapp_debug.log", "a", encoding="utf-8") as f:
                f.write(f"[{datetime.now().isoformat()}] {message}\n")
        except Exception:
            pass
    
    def _log_error(self, error_msg: str):
        """Log an error to debug log file."""
        try:
            log_dir = "database_reports"
            os.makedirs(log_dir, exist_ok=True)
            with open(f"{log_dir}/whatsapp_debug.log", "a", encoding="utf-8") as f:
                f.write(f"[{datetime.now().isoformat()}] ERROR: {error_msg}\n")
        except Exception:
            pass
    
    def send_test_message(self, test_number: str) -> Tuple[bool, str]:
        """
        Send a test WhatsApp message.
        
        Args:
            test_number: Test phone number
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        test_message = """🧪 *Test Message*

This is a test message from Island Harvest Hub WhatsApp Automation Service.

If you received this message, your WhatsApp integration is working correctly! ✅

_Island Harvest Hub_"""
        
        return self.send_message(test_number, test_message)

