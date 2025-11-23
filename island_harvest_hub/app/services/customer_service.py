"""
Customer management service for Island Harvest Hub AI Assistant.
"""

import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models import Customer, Order, OrderItem, Invoice
from app.database.config import SessionLocal

class CustomerService:
    """Service class for customer management operations."""
    
    def __init__(self):
        self.db: Session = SessionLocal()
    
    def __del__(self):
        """Close database session when service is destroyed."""
        if hasattr(self, 'db'):
            self.db.close()
    
    def create_customer(self, name: str, business_id: str = 'island_harvest',
                       contact_person: str = None, phone: str = None, 
                       email: str = None, address: str = None, 
                       preferences: Dict = None) -> Customer:
        """Create a new customer."""
        try:
            # Check for duplicate name within the same business
            existing = self.db.query(Customer).filter(
                Customer.name == name,
                Customer.business_id == business_id
            ).first()
            if existing:
                raise ValueError(f"Customer '{name}' already exists for this business.")
            
            customer = Customer(
                business_id=business_id,
                name=name,
                contact_person=contact_person,
                phone=phone,
                email=email,
                address=address,
                preferences=json.dumps(preferences) if preferences else None,
                created_at=datetime.now()
            )
            self.db.add(customer)
            self.db.commit()
            self.db.refresh(customer)
            return customer
        except ValueError:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_customer(self, customer_id: int) -> Optional[Customer]:
        """Get a customer by ID."""
        return self.db.query(Customer).filter(Customer.id == customer_id).first()
    
    def get_customer_by_name(self, name: str, business_id: str = None) -> Optional[Customer]:
        """Get a customer by name, optionally filtered by business."""
        query = self.db.query(Customer).filter(Customer.name == name)
        if business_id:
            query = query.filter(Customer.business_id == business_id)
        return query.first()
    
    def get_all_customers(self, business_id: str = None) -> List[Customer]:
        """Get all customers, optionally filtered by business."""
        query = self.db.query(Customer)
        if business_id:
            query = query.filter(Customer.business_id == business_id)
        return query.order_by(Customer.name).all()
    
    def update_customer(self, customer_id: int, **kwargs) -> Optional[Customer]:
        """Update customer information."""
        try:
            customer = self.get_customer(customer_id)
            if not customer:
                return None
            
            for key, value in kwargs.items():
                if hasattr(customer, key):
                    if key == 'preferences' and isinstance(value, dict):
                        setattr(customer, key, json.dumps(value))
                    else:
                        setattr(customer, key, value)
            
            customer.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(customer)
            return customer
        except Exception as e:
            self.db.rollback()
            raise e
    
    def delete_customer(self, customer_id: int) -> bool:
        """Delete a customer."""
        try:
            customer = self.get_customer(customer_id)
            if not customer:
                return False
            
            self.db.delete(customer)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e
    
    def update_satisfaction_score(self, customer_id: int, score: int) -> Optional[Customer]:
        """Update customer satisfaction score."""
        return self.update_customer(customer_id, satisfaction_score=score)
    
    def add_feedback(self, customer_id: int, feedback: str) -> Optional[Customer]:
        """Add feedback for a customer."""
        customer = self.get_customer(customer_id)
        if not customer:
            return None
        
        existing_feedback = customer.feedback or ""
        new_feedback = f"{existing_feedback}\n[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {feedback}"
        return self.update_customer(customer_id, feedback=new_feedback.strip())
    
    def get_customer_preferences(self, customer_id: int) -> Dict:
        """Get customer preferences as a dictionary."""
        customer = self.get_customer(customer_id)
        if not customer or not customer.preferences:
            return {}
        
        try:
            return json.loads(customer.preferences)
        except json.JSONDecodeError:
            return {}
    
    def create_order(self, customer_id: int, order_date: datetime, 
                    delivery_date: datetime, items: List[Dict], 
                    notes: str = None) -> Optional[Order]:
        """Create a new order for a customer."""
        try:
            customer = self.get_customer(customer_id)
            if not customer:
                return None
            
            # Calculate total amount
            total_amount = sum(item['quantity'] * item['unit_price'] for item in items)
            
            # Get customer to get business_id
            customer = self.get_customer(customer_id)
            if not customer:
                return None
            
            order = Order(
                business_id=customer.business_id,
                customer_id=customer_id,
                order_date=order_date,
                delivery_date=delivery_date,
                status="Pending",
                total_amount=total_amount,
                notes=notes,
                created_at=datetime.now()
            )
            
            self.db.add(order)
            self.db.flush()  # Get the order ID
            
            # Add order items
            for item in items:
                order_item = OrderItem(
                    order_id=order.id,
                    product_name=item['product_name'],
                    quantity=item['quantity'],
                    unit_price=item['unit_price'],
                    subtotal=item['quantity'] * item['unit_price']
                )
                self.db.add(order_item)
            
            self.db.commit()
            self.db.refresh(order)
            return order
        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_customer_orders(self, customer_id: int) -> List[Order]:
        """Get all orders for a customer."""
        return self.db.query(Order).filter(Order.customer_id == customer_id).all()
    
    def update_order_status(self, order_id: int, status: str) -> Optional[Order]:
        """Update order status."""
        try:
            order = self.db.query(Order).filter(Order.id == order_id).first()
            if not order:
                return None
            
            order.status = status
            order.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(order)
            return order
        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_customer_analytics(self, customer_id: int) -> Dict[str, Any]:
        """Get analytics for a specific customer."""
        customer = self.get_customer(customer_id)
        if not customer:
            return {}
        
        orders = self.get_customer_orders(customer_id)
        
        total_orders = len(orders)
        total_revenue = sum(order.total_amount or 0 for order in orders)
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        # Order status breakdown
        status_counts = {}
        for order in orders:
            status_counts[order.status] = status_counts.get(order.status, 0) + 1
        
        return {
            'customer_name': customer.name,
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'average_order_value': avg_order_value,
            'satisfaction_score': customer.satisfaction_score,
            'order_status_breakdown': status_counts,
            'last_order_date': max([order.order_date for order in orders]) if orders else None
        }
    
    def get_all_customers_analytics(self, business_id: str = None) -> Dict[str, Any]:
        """Get analytics for all customers, optionally filtered by business."""
        customers = self.get_all_customers(business_id=business_id)
        query = self.db.query(Order)
        if business_id:
            query = query.filter(Order.business_id == business_id)
        all_orders = query.all()
        
        total_customers = len(customers)
        total_orders = len(all_orders)
        total_revenue = sum(order.total_amount or 0 for order in all_orders)
        avg_satisfaction = sum(c.satisfaction_score or 0 for c in customers) / total_customers if total_customers > 0 else 0
        
        # Top customers by revenue
        customer_revenues = {}
        for order in all_orders:
            customer_revenues[order.customer_id] = customer_revenues.get(order.customer_id, 0) + (order.total_amount or 0)
        
        top_customers = sorted(customer_revenues.items(), key=lambda x: x[1], reverse=True)[:5]
        top_customers_info = []
        for customer_id, revenue in top_customers:
            customer = self.get_customer(customer_id)
            if customer:
                top_customers_info.append({
                    'name': customer.name,
                    'revenue': revenue
                })
        
        return {
            'total_customers': total_customers,
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'average_satisfaction_score': avg_satisfaction,
            'top_customers': top_customers_info
        }

