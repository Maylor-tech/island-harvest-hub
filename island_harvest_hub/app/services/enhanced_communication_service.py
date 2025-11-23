"""
Enhanced communication service for Island Harvest Hub.
Integrates WhatsApp, email, and task management.
"""

from typing import Dict, List, Optional
from datetime import datetime
import json

from .whatsapp_service import WhatsAppService
from .email_service import EmailService

class EnhancedCommunicationService:
    """Enhanced service for managing all communication channels."""
    
    def __init__(self):
        """Initialize enhanced communication service."""
        self.whatsapp = WhatsAppService()
        self.email = EmailService()
    
    def send_customer_notification(self, customer_id: int, notification_type: str, 
                                 data: Dict) -> Dict:
        """
        Send notification to customer via preferred channel.
        
        Args:
            customer_id: Customer ID
            notification_type: Type of notification
            data: Notification data
            
        Returns:
            Response dictionary
        """
        # In a real implementation, you would:
        # 1. Get customer preferences from database
        # 2. Choose appropriate channel (WhatsApp, email, SMS)
        # 3. Send via preferred channel
        
        # Mock implementation
        return {
            "success": True,
            "customer_id": customer_id,
            "notification_type": notification_type,
            "channel": "whatsapp",
            "timestamp": datetime.now().isoformat()
        }
    
    def send_supplier_notification(self, farmer_id: int, notification_type: str, 
                                 data: Dict) -> Dict:
        """
        Send notification to supplier/farmer.
        
        Args:
            farmer_id: Farmer ID
            notification_type: Type of notification
            data: Notification data
            
        Returns:
            Response dictionary
        """
        # Mock implementation
        return {
            "success": True,
            "farmer_id": farmer_id,
            "notification_type": notification_type,
            "channel": "whatsapp",
            "timestamp": datetime.now().isoformat()
        }
    
    def schedule_reminder(self, recipient_type: str, recipient_id: int, 
                         reminder_type: str, schedule_time: datetime, 
                         data: Dict) -> Dict:
        """
        Schedule a reminder notification.
        
        Args:
            recipient_type: 'customer' or 'farmer'
            recipient_id: ID of recipient
            reminder_type: Type of reminder
            schedule_time: When to send reminder
            data: Reminder data
            
        Returns:
            Response dictionary
        """
        # In production, this would integrate with a job scheduler
        return {
            "success": True,
            "reminder_id": f"reminder_{datetime.now().timestamp()}",
            "recipient_type": recipient_type,
            "recipient_id": recipient_id,
            "reminder_type": reminder_type,
            "scheduled_for": schedule_time.isoformat(),
            "status": "scheduled"
        }
    
    def get_communication_history(self, recipient_type: str, 
                                recipient_id: int) -> List[Dict]:
        """
        Get communication history for a recipient.
        
        Args:
            recipient_type: 'customer' or 'farmer'
            recipient_id: ID of recipient
            
        Returns:
            List of communication records
        """
        # Mock data for demonstration
        return [
            {
                "id": 1,
                "type": "whatsapp",
                "template": "order_confirmation",
                "status": "delivered",
                "sent_at": "2024-01-15T10:30:00",
                "content": "Order confirmation message"
            },
            {
                "id": 2,
                "type": "email",
                "template": "welcome_customer",
                "status": "opened",
                "sent_at": "2024-01-10T09:15:00",
                "content": "Welcome email"
            }
        ]
    
    def get_message_templates(self, channel: str = "all") -> List[Dict]:
        """
        Get available message templates.
        
        Args:
            channel: 'whatsapp', 'email', or 'all'
            
        Returns:
            List of templates
        """
        templates = []
        
        if channel in ["whatsapp", "all"]:
            whatsapp_templates = self.whatsapp.get_message_templates()
            for template in whatsapp_templates:
                template["channel"] = "whatsapp"
                templates.append(template)
        
        if channel in ["email", "all"]:
            email_templates = self.email.get_email_templates()
            for template in email_templates:
                template["channel"] = "email"
                templates.append(template)
        
        return templates
    
    def send_bulk_message(self, recipient_type: str, recipient_ids: List[int], 
                         template_name: str, parameters: Dict, 
                         channel: str = "whatsapp") -> Dict:
        """
        Send bulk message to multiple recipients.
        
        Args:
            recipient_type: 'customer' or 'farmer'
            recipient_ids: List of recipient IDs
            template_name: Name of template to use
            parameters: Template parameters
            channel: Communication channel
            
        Returns:
            Response dictionary
        """
        results = []
        
        for recipient_id in recipient_ids:
            if channel == "whatsapp":
                result = self.send_customer_notification(
                    recipient_id, template_name, parameters
                ) if recipient_type == "customer" else self.send_supplier_notification(
                    recipient_id, template_name, parameters
                )
            elif channel == "email":
                # Similar implementation for email
                result = {"success": True, "recipient_id": recipient_id}
            
            results.append(result)
        
        return {
            "success": True,
            "total_sent": len(recipient_ids),
            "successful": len([r for r in results if r.get("success")]),
            "failed": len([r for r in results if not r.get("success")]),
            "results": results
        }
    
    def create_follow_up_task(self, task_type: str, description: str, 
                            due_date: datetime, assigned_to: str = "Brian Miller") -> Dict:
        """
        Create a follow-up task.
        
        Args:
            task_type: Type of task
            description: Task description
            due_date: When task is due
            assigned_to: Who task is assigned to
            
        Returns:
            Task dictionary
        """
        return {
            "id": f"task_{datetime.now().timestamp()}",
            "type": task_type,
            "description": description,
            "due_date": due_date.isoformat(),
            "assigned_to": assigned_to,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
    
    def get_pending_tasks(self, assigned_to: str = None) -> List[Dict]:
        """
        Get pending follow-up tasks.
        
        Args:
            assigned_to: Filter by assignee
            
        Returns:
            List of pending tasks
        """
        # Mock data for demonstration
        return [
            {
                "id": "task_1",
                "type": "customer_follow_up",
                "description": "Follow up with Blue Mountain Resort about order feedback",
                "due_date": "2024-01-20T10:00:00",
                "assigned_to": "Brian Miller",
                "status": "pending",
                "priority": "high"
            },
            {
                "id": "task_2",
                "type": "supplier_check",
                "description": "Check quality standards with Green Valley Farm",
                "due_date": "2024-01-18T14:00:00",
                "assigned_to": "Brian Miller",
                "status": "pending",
                "priority": "medium"
            }
        ]
    
    def mark_task_complete(self, task_id: str, notes: str = "") -> Dict:
        """
        Mark a task as complete.
        
        Args:
            task_id: Task ID
            notes: Completion notes
            
        Returns:
            Response dictionary
        """
        return {
            "success": True,
            "task_id": task_id,
            "status": "completed",
            "completed_at": datetime.now().isoformat(),
            "notes": notes
        }

