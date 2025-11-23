"""
Communication service for Island Harvest Hub AI Assistant.
"""

import json
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models import MessageTemplate, Meeting, FollowUpTask
from app.database.config import SessionLocal

class CommunicationService:
    """Service class for communication management operations."""
    
    def __init__(self):
        self.db: Session = SessionLocal()
    
    def __del__(self):
        """Close database session when service is destroyed."""
        if hasattr(self, 'db'):
            self.db.close()
    
    # Message Template Management
    def create_message_template(self, name: str, template_type: str, 
                               body: str, subject: str = None) -> MessageTemplate:
        """Create a new message template."""
        try:
            template = MessageTemplate(
                name=name,
                type=template_type,
                subject=subject,
                body=body,
                created_at=datetime.now()
            )
            
            self.db.add(template)
            self.db.commit()
            self.db.refresh(template)
            return template
        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_message_template(self, template_id: int) -> Optional[MessageTemplate]:
        """Get a message template by ID."""
        return self.db.query(MessageTemplate).filter(MessageTemplate.id == template_id).first()
    
    def get_message_template_by_name(self, name: str) -> Optional[MessageTemplate]:
        """Get a message template by name."""
        return self.db.query(MessageTemplate).filter(MessageTemplate.name == name).first()
    
    def get_all_message_templates(self) -> List[MessageTemplate]:
        """Get all message templates."""
        return self.db.query(MessageTemplate).order_by(MessageTemplate.name).all()
    
    def get_templates_by_type(self, template_type: str) -> List[MessageTemplate]:
        """Get message templates by type."""
        return self.db.query(MessageTemplate).filter(
            MessageTemplate.type == template_type
        ).order_by(MessageTemplate.name).all()
    
    def update_message_template(self, template_id: int, **kwargs) -> Optional[MessageTemplate]:
        """Update message template."""
        try:
            template = self.get_message_template(template_id)
            if not template:
                return None
            
            for key, value in kwargs.items():
                if hasattr(template, key):
                    setattr(template, key, value)
            
            template.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(template)
            return template
        except Exception as e:
            self.db.rollback()
            raise e
    
    def delete_message_template(self, template_id: int) -> bool:
        """Delete a message template."""
        try:
            template = self.get_message_template(template_id)
            if not template:
                return False
            
            self.db.delete(template)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e
    
    def personalize_template(self, template_id: int, variables: Dict[str, str]) -> Optional[str]:
        """Personalize a template with variables."""
        template = self.get_message_template(template_id)
        if not template:
            return None
        
        personalized_body = template.body
        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            personalized_body = personalized_body.replace(placeholder, str(value))
        
        return personalized_body
    
    # Meeting Management
    def create_meeting(self, title: str, date_time: datetime, 
                      attendees: List[str] = None, notes: str = None) -> Meeting:
        """Create a new meeting."""
        try:
            meeting = Meeting(
                title=title,
                date_time=date_time,
                attendees=json.dumps(attendees) if attendees else None,
                notes=notes,
                reminders_sent=False,
                created_at=datetime.now()
            )
            
            self.db.add(meeting)
            self.db.commit()
            self.db.refresh(meeting)
            return meeting
        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_meeting(self, meeting_id: int) -> Optional[Meeting]:
        """Get a meeting by ID."""
        return self.db.query(Meeting).filter(Meeting.id == meeting_id).first()
    
    def get_all_meetings(self) -> List[Meeting]:
        """Get all meetings."""
        return self.db.query(Meeting).order_by(Meeting.date_time.desc()).all()
    
    def get_upcoming_meetings(self, days_ahead: int = 7) -> List[Meeting]:
        """Get upcoming meetings within specified days."""
        end_date = datetime.now() + datetime.timedelta(days=days_ahead)
        return self.db.query(Meeting).filter(
            Meeting.date_time >= datetime.now(),
            Meeting.date_time <= end_date
        ).order_by(Meeting.date_time.asc()).all()
    
    def get_meetings_by_date_range(self, start_date: date, end_date: date) -> List[Meeting]:
        """Get meetings within a date range."""
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        return self.db.query(Meeting).filter(
            Meeting.date_time >= start_datetime,
            Meeting.date_time <= end_datetime
        ).order_by(Meeting.date_time.asc()).all()
    
    def update_meeting(self, meeting_id: int, **kwargs) -> Optional[Meeting]:
        """Update meeting information."""
        try:
            meeting = self.get_meeting(meeting_id)
            if not meeting:
                return None
            
            for key, value in kwargs.items():
                if hasattr(meeting, key):
                    if key == 'attendees' and isinstance(value, list):
                        setattr(meeting, key, json.dumps(value))
                    else:
                        setattr(meeting, key, value)
            
            meeting.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(meeting)
            return meeting
        except Exception as e:
            self.db.rollback()
            raise e
    
    def mark_reminders_sent(self, meeting_id: int) -> Optional[Meeting]:
        """Mark reminders as sent for a meeting."""
        return self.update_meeting(meeting_id, reminders_sent=True)
    
    def get_meeting_attendees(self, meeting_id: int) -> List[str]:
        """Get meeting attendees as a list."""
        meeting = self.get_meeting(meeting_id)
        if not meeting or not meeting.attendees:
            return []
        
        try:
            return json.loads(meeting.attendees)
        except json.JSONDecodeError:
            return []
    
    def delete_meeting(self, meeting_id: int) -> bool:
        """Delete a meeting."""
        try:
            meeting = self.get_meeting(meeting_id)
            if not meeting:
                return False
            
            self.db.delete(meeting)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e
    
    # Follow-up Task Management
    def create_follow_up_task(self, description: str, due_date: date = None,
                             assigned_to: str = None, related_entity_id: int = None,
                             related_entity_type: str = None) -> FollowUpTask:
        """Create a new follow-up task."""
        try:
            task = FollowUpTask(
                description=description,
                due_date=datetime.combine(due_date, datetime.min.time()) if due_date else None,
                status="Pending",
                assigned_to=assigned_to,
                related_entity_id=related_entity_id,
                related_entity_type=related_entity_type,
                created_at=datetime.now()
            )
            
            self.db.add(task)
            self.db.commit()
            self.db.refresh(task)
            return task
        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_follow_up_task(self, task_id: int) -> Optional[FollowUpTask]:
        """Get a follow-up task by ID."""
        return self.db.query(FollowUpTask).filter(FollowUpTask.id == task_id).first()
    
    def get_all_follow_up_tasks(self) -> List[FollowUpTask]:
        """Get all follow-up tasks."""
        return self.db.query(FollowUpTask).order_by(FollowUpTask.due_date.asc()).all()
    
    def get_pending_tasks(self) -> List[FollowUpTask]:
        """Get pending follow-up tasks."""
        return self.db.query(FollowUpTask).filter(
            FollowUpTask.status == "Pending"
        ).order_by(FollowUpTask.due_date.asc()).all()
    
    def get_overdue_tasks(self) -> List[FollowUpTask]:
        """Get overdue follow-up tasks."""
        current_date = datetime.now().date()
        return self.db.query(FollowUpTask).filter(
            FollowUpTask.status == "Pending",
            FollowUpTask.due_date < datetime.combine(current_date, datetime.min.time())
        ).order_by(FollowUpTask.due_date.asc()).all()
    
    def get_tasks_by_entity(self, entity_id: int, entity_type: str) -> List[FollowUpTask]:
        """Get follow-up tasks related to a specific entity."""
        return self.db.query(FollowUpTask).filter(
            FollowUpTask.related_entity_id == entity_id,
            FollowUpTask.related_entity_type == entity_type
        ).order_by(FollowUpTask.due_date.asc()).all()
    
    def complete_task(self, task_id: int) -> Optional[FollowUpTask]:
        """Mark a follow-up task as completed."""
        try:
            task = self.get_follow_up_task(task_id)
            if not task:
                return None
            
            task.status = "Completed"
            task.updated_at = datetime.now()
            
            self.db.commit()
            self.db.refresh(task)
            return task
        except Exception as e:
            self.db.rollback()
            raise e
    
    def update_task_status(self, task_id: int, status: str) -> Optional[FollowUpTask]:
        """Update follow-up task status."""
        try:
            task = self.get_follow_up_task(task_id)
            if not task:
                return None
            
            task.status = status
            task.updated_at = datetime.now()
            
            self.db.commit()
            self.db.refresh(task)
            return task
        except Exception as e:
            self.db.rollback()
            raise e
    
    def update_follow_up_task(self, task_id: int, **kwargs) -> Optional[FollowUpTask]:
        """Update follow-up task information."""
        try:
            task = self.get_follow_up_task(task_id)
            if not task:
                return None
            
            for key, value in kwargs.items():
                if hasattr(task, key):
                    if key == 'due_date' and isinstance(value, date):
                        setattr(task, key, datetime.combine(value, datetime.min.time()))
                    else:
                        setattr(task, key, value)
            
            task.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(task)
            return task
        except Exception as e:
            self.db.rollback()
            raise e
    
    def delete_follow_up_task(self, task_id: int) -> bool:
        """Delete a follow-up task."""
        try:
            task = self.get_follow_up_task(task_id)
            if not task:
                return False
            
            self.db.delete(task)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e
    
    # Communication Analytics
    def get_communication_summary(self) -> Dict[str, Any]:
        """Get communication activity summary."""
        templates = self.get_all_message_templates()
        meetings = self.get_all_meetings()
        tasks = self.get_all_follow_up_tasks()
        
        # Template statistics
        template_types = {}
        for template in templates:
            template_types[template.type] = template_types.get(template.type, 0) + 1
        
        # Meeting statistics
        upcoming_meetings = self.get_upcoming_meetings()
        past_meetings = [m for m in meetings if m.date_time < datetime.now()]
        
        # Task statistics
        pending_tasks = self.get_pending_tasks()
        overdue_tasks = self.get_overdue_tasks()
        completed_tasks = [t for t in tasks if t.status == "Completed"]
        
        return {
            'templates': {
                'total': len(templates),
                'by_type': template_types
            },
            'meetings': {
                'total': len(meetings),
                'upcoming': len(upcoming_meetings),
                'past': len(past_meetings)
            },
            'tasks': {
                'total': len(tasks),
                'pending': len(pending_tasks),
                'overdue': len(overdue_tasks),
                'completed': len(completed_tasks)
            }
        }
    
    # Default Templates Creation
    def create_default_templates(self):
        """Create default message templates for common scenarios."""
        default_templates = [
            {
                'name': 'Order Confirmation',
                'type': 'WhatsApp',
                'body': 'Hello {customer_name}! Your order #{order_id} has been confirmed. Delivery scheduled for {delivery_date}. Total: ${total_amount}. Thank you for choosing Island Harvest Hub!'
            },
            {
                'name': 'Delivery Notification',
                'type': 'WhatsApp',
                'body': 'Good morning {customer_name}! Your fresh produce order is on its way and will arrive between {delivery_time}. Our driver will contact you upon arrival.'
            },
            {
                'name': 'Payment Reminder',
                'type': 'Email',
                'subject': 'Payment Reminder - Invoice #{invoice_id}',
                'body': 'Dear {customer_name},\n\nThis is a friendly reminder that Invoice #{invoice_id} for ${amount} is due on {due_date}.\n\nPlease arrange payment at your earliest convenience.\n\nBest regards,\nBrian Miller\nIsland Harvest Hub'
            },
            {
                'name': 'Farmer Pickup Schedule',
                'type': 'WhatsApp',
                'body': 'Hello {farmer_name}! Pickup scheduled for {pickup_date} at {pickup_time}. Please have your {products} ready. Expected quantity: {quantity}. See you soon!'
            },
            {
                'name': 'Quality Feedback',
                'type': 'WhatsApp',
                'body': 'Hi {farmer_name}, thank you for the excellent {product} delivery! Quality score: {quality_score}/5. {feedback_notes}. Keep up the great work!'
            },
            {
                'name': 'New Customer Welcome',
                'type': 'Email',
                'subject': 'Welcome to Island Harvest Hub!',
                'body': 'Dear {customer_name},\n\nWelcome to Island Harvest Hub! We\'re excited to partner with you in bringing the freshest local produce to your establishment.\n\nOur team is committed to providing you with:\n- Premium quality local produce\n- Reliable delivery schedules\n- Competitive pricing\n- Excellent customer service\n\nYour account is now set up and ready to use. Feel free to contact us anytime.\n\nBest regards,\nBrian Miller\nFounder, Island Harvest Hub'
            }
        ]
        
        for template_data in default_templates:
            existing = self.get_message_template_by_name(template_data['name'])
            if not existing:
                self.create_message_template(**template_data)

