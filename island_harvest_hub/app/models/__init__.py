"""
SQLAlchemy models for Island Harvest Hub AI Assistant.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.config import Base

class Customer(Base):
    """Customer model for hotels and restaurants."""
    __tablename__ = 'customers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    business_id = Column(String(50), nullable=False, default='island_harvest')
    name = Column(String(255), nullable=False)
    contact_person = Column(String(255))
    phone = Column(String(50))
    email = Column(String(255))
    address = Column(Text)
    preferences = Column(Text)  # JSON string
    satisfaction_score = Column(Integer)
    feedback = Column(Text)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, onupdate=func.current_timestamp())
    
    # Unique constraint on business_id + name combination
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )
    
    # Relationships
    orders = relationship("Order", back_populates="customer")
    invoices = relationship("Invoice", back_populates="customer")

class Order(Base):
    """Order model for customer orders."""
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    business_id = Column(String(50), nullable=False, default='island_harvest')
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    order_date = Column(DateTime, nullable=False)
    delivery_date = Column(DateTime, nullable=False)
    status = Column(String(50), nullable=False)
    total_amount = Column(Float)
    notes = Column(Text)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, onupdate=func.current_timestamp())
    
    # Relationships
    customer = relationship("Customer", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order")
    invoice = relationship("Invoice", back_populates="order", uselist=False)

class OrderItem(Base):
    """Order item model for products within orders."""
    __tablename__ = 'order_items'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_name = Column(String(255), nullable=False)
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    subtotal = Column(Float)
    
    # Relationships
    order = relationship("Order", back_populates="order_items")

class Farmer(Base):
    """Farmer model for local suppliers."""
    __tablename__ = 'farmers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    business_id = Column(String(50), nullable=False, default='island_harvest')
    name = Column(String(255), nullable=False)
    contact_person = Column(String(255))
    phone = Column(String(50))
    email = Column(String(255))
    address = Column(Text)
    product_specialties = Column(Text)  # JSON string
    pickup_schedule = Column(Text)  # JSON string
    quality_records = Column(Text)  # JSON string
    payment_history = Column(Text)  # JSON string
    performance_notes = Column(Text)
    training_needs = Column(Text)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, onupdate=func.current_timestamp())
    
    # Relationships
    payments = relationship("FarmerPayment", back_populates="farmer")

class FarmerPayment(Base):
    """Farmer payment model for tracking payments to farmers."""
    __tablename__ = 'farmer_payments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    farmer_id = Column(Integer, ForeignKey('farmers.id'), nullable=False)
    payment_date = Column(DateTime, nullable=False)
    amount = Column(Float, nullable=False)
    notes = Column(Text)
    
    # Relationships
    farmer = relationship("Farmer", back_populates="payments")

class DailyLog(Base):
    """Daily log model for operational tracking."""
    __tablename__ = 'daily_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    business_id = Column(String(50), nullable=False, default='island_harvest')
    log_date = Column(DateTime, nullable=False)
    orders_fulfilled = Column(Integer)
    quality_control_notes = Column(Text)
    temperature_logs = Column(Text)  # JSON string
    delivery_route_notes = Column(Text)
    issue_tracking = Column(Text)  # JSON string
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, onupdate=func.current_timestamp())

class Transaction(Base):
    """Transaction model for financial tracking."""
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    business_id = Column(String(50), nullable=False, default='island_harvest')
    date = Column(DateTime, nullable=False)
    type = Column(String(50), nullable=False)
    description = Column(Text)
    amount = Column(Float, nullable=False)
    related_entity_id = Column(Integer)
    related_entity_type = Column(String(50))
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, onupdate=func.current_timestamp())

class Invoice(Base):
    """Invoice model for customer billing."""
    __tablename__ = 'invoices'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    business_id = Column(String(50), nullable=False, default='island_harvest')
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    invoice_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, onupdate=func.current_timestamp())
    
    # Relationships
    customer = relationship("Customer", back_populates="invoices")
    order = relationship("Order", back_populates="invoice")

class MessageTemplate(Base):
    """Message template model for communication."""
    __tablename__ = 'message_templates'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    type = Column(String(50), nullable=False)
    subject = Column(String(255))
    body = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, onupdate=func.current_timestamp())

class Meeting(Base):
    """Meeting model for scheduling."""
    __tablename__ = 'meetings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    date_time = Column(DateTime, nullable=False)
    attendees = Column(Text)  # JSON string
    notes = Column(Text)
    reminders_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, onupdate=func.current_timestamp())

class FollowUpTask(Base):
    """Follow-up task model for task management."""
    __tablename__ = 'follow_up_tasks'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(Text, nullable=False)
    due_date = Column(DateTime)
    status = Column(String(50), nullable=False)
    assigned_to = Column(String(255))
    related_entity_id = Column(Integer)
    related_entity_type = Column(String(50))
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, onupdate=func.current_timestamp())

class Document(Base):
    """Document model for file management."""
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False, unique=True)
    type = Column(String(50))
    version = Column(String(50))
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, onupdate=func.current_timestamp())

class Goal(Base):
    """Goal model for strategic planning."""
    __tablename__ = 'goals'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    business_id = Column(String(50), nullable=False, default='island_harvest')
    name = Column(String(255), nullable=False)
    description = Column(Text)
    target_value = Column(Float)
    current_value = Column(Float, default=0.0)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, onupdate=func.current_timestamp())

class PerformanceMetric(Base):
    """Performance metric model for KPI tracking."""
    __tablename__ = 'performance_metrics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    value = Column(Float, nullable=False)
    date = Column(DateTime, nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, onupdate=func.current_timestamp())

class Partnership(Base):
    """Partnership model for tracking business partnerships."""
    __tablename__ = 'partnerships'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    type = Column(String(50))
    contact_person = Column(String(255))
    status = Column(String(50), nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, onupdate=func.current_timestamp())

