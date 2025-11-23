"""
Script to populate the Island Harvest Hub database with sample data for testing.
"""

import sys
import os
from datetime import datetime, timedelta
import json
from sqlalchemy.orm import Session

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.config import get_db
from app.models import Customer, Farmer, Order, OrderItem, Transaction, Document, MessageTemplate

def create_sample_customers(db: Session):
    """Create sample hotel and restaurant customers."""
    customers = [
        Customer(
            name="Trident Castle",
            contact_person="Michael Thompson",
            phone="+1 (876) 555-0101",
            email="michael@tridentcastle.com",
            address="Port Antonio, Portland, Jamaica",
            preferences=json.dumps({
                "delivery_times": ["Monday", "Wednesday", "Friday"],
                "preferred_products": ["organic vegetables", "fresh herbs", "exotic fruits"]
            }),
            satisfaction_score=5
        ),
        Customer(
            name="Geejam Hotel",
            contact_person="Sarah Williams",
            phone="+1 (876) 555-0102",
            email="sarah@geejam.com",
            address="San San, Port Antonio, Jamaica",
            preferences=json.dumps({
                "delivery_times": ["Tuesday", "Thursday", "Saturday"],
                "preferred_products": ["fresh seafood", "local vegetables", "tropical fruits"]
            }),
            satisfaction_score=4
        ),
        Customer(
            name="Moon San Villa",
            contact_person="David Chen",
            phone="+1 (876) 555-0103",
            email="david@moonsanvilla.com",
            address="Port Antonio, Portland, Jamaica",
            preferences=json.dumps({
                "delivery_times": ["Monday", "Friday"],
                "preferred_products": ["organic produce", "fresh herbs", "local fruits"]
            }),
            satisfaction_score=5
        )
    ]
    
    for customer in customers:
        db.add(customer)
    db.commit()
    return customers

def create_sample_farmers(db: Session):
    """Create sample farmers/suppliers."""
    farmers = [
        Farmer(
            name="Devon Brown",
            contact_person="Devon Brown",
            phone="+1 (876) 555-0201",
            email="devon@brownfarm.com",
            address="St. Mary, Jamaica",
            product_specialties=json.dumps(["yams", "cassava", "sweet potatoes"]),
            pickup_schedule=json.dumps({
                "Monday": "9:00 AM",
                "Wednesday": "9:00 AM",
                "Friday": "9:00 AM"
            }),
            quality_records=json.dumps({
                "last_inspection": "2024-03-15",
                "rating": "A+",
                "notes": "Excellent produce quality"
            })
        ),
        Farmer(
            name="Shanice Grant",
            contact_person="Shanice Grant",
            phone="+1 (876) 555-0202",
            email="shanice@grantfarm.com",
            address="Portland, Jamaica",
            product_specialties=json.dumps(["callaloo", "tomatoes", "peppers"]),
            pickup_schedule=json.dumps({
                "Tuesday": "10:00 AM",
                "Thursday": "10:00 AM",
                "Saturday": "10:00 AM"
            }),
            quality_records=json.dumps({
                "last_inspection": "2024-03-14",
                "rating": "A",
                "notes": "Consistent quality"
            })
        ),
        Farmer(
            name="Omar Williams",
            contact_person="Omar Williams",
            phone="+1 (876) 555-0203",
            email="omar@williamsfarm.com",
            address="St. Thomas, Jamaica",
            product_specialties=json.dumps(["bananas", "plantains", "coconuts"]),
            pickup_schedule=json.dumps({
                "Monday": "8:00 AM",
                "Wednesday": "8:00 AM",
                "Friday": "8:00 AM"
            }),
            quality_records=json.dumps({
                "last_inspection": "2024-03-13",
                "rating": "A+",
                "notes": "Premium quality tropical fruits"
            })
        )
    ]
    
    for farmer in farmers:
        db.add(farmer)
    db.commit()
    return farmers

def create_sample_orders(db: Session, customers):
    """Create sample orders for customers."""
    orders = []
    for customer in customers:
        # Create a recent order
        order = Order(
            customer_id=customer.id,
            order_date=datetime.now() - timedelta(days=2),
            delivery_date=datetime.now() + timedelta(days=1),
            status="Confirmed",
            total_amount=1500.00,
            notes=f"Regular weekly order for {customer.name}"
        )
        db.add(order)
        db.flush()  # Get the order ID
        
        # Add order items
        items = [
            OrderItem(
                order_id=order.id,
                product_name="Organic Vegetables Bundle",
                quantity=5,
                unit_price=200.00,
                subtotal=1000.00
            ),
            OrderItem(
                order_id=order.id,
                product_name="Fresh Herbs Selection",
                quantity=2,
                unit_price=250.00,
                subtotal=500.00
            )
        ]
        for item in items:
            db.add(item)
        
        orders.append(order)
    
    db.commit()
    return orders

def create_sample_transactions(db: Session, orders):
    """Create sample transactions for orders."""
    transactions = []
    for order in orders:
        transaction = Transaction(
            date=datetime.now() - timedelta(days=1),
            type="Revenue",
            description=f"Payment for Order #{order.id}",
            amount=order.total_amount,
            related_entity_id=order.id,
            related_entity_type="Order"
        )
        db.add(transaction)
        transactions.append(transaction)
    
    db.commit()
    return transactions

def create_sample_message_templates(db: Session):
    """Create sample WhatsApp message templates."""
    templates = [
        MessageTemplate(
            name="Order Confirmation",
            type="WhatsApp",
            title="Order Confirmation",
            body="Dear {customer_name},\n\nYour order #{order_id} has been confirmed for delivery on {delivery_date}.\n\nTotal amount: ${total_amount}\n\nThank you for choosing Island Harvest Hub!"
        ),
        MessageTemplate(
            name="Delivery Reminder",
            type="WhatsApp",
            title="Delivery Reminder",
            body="Dear {customer_name},\n\nThis is a reminder that your order #{order_id} will be delivered tomorrow at {delivery_time}.\n\nPlease ensure someone is available to receive the delivery.\n\nThank you!"
        ),
        MessageTemplate(
            name="Payment Reminder",
            type="WhatsApp",
            title="Payment Reminder",
            body="Dear {customer_name},\n\nThis is a friendly reminder that payment for order #{order_id} is due on {due_date}.\n\nAmount due: ${amount}\n\nThank you for your prompt attention to this matter."
        )
    ]
    
    for template in templates:
        db.add(template)
    db.commit()
    return templates

def create_sample_documents(db: Session):
    """Create sample documents."""
    documents = [
        Document(
            name="Supplier Agreement Template",
            file_path="documents/supplier_agreement.pdf",
            type="Contract",
            version="1.0"
        ),
        Document(
            name="Quality Control Checklist",
            file_path="documents/quality_control.pdf",
            type="Report",
            version="2.1"
        ),
        Document(
            name="Delivery Schedule Template",
            file_path="documents/delivery_schedule.xlsx",
            type="Report",
            version="1.0"
        )
    ]
    
    for document in documents:
        db.add(document)
    db.commit()
    return documents

def main():
    """Main function to populate the database with sample data."""
    print("Populating Island Harvest Hub database with sample data...")
    
    db = next(get_db())
    
    try:
        # Create sample data
        customers = create_sample_customers(db)
        farmers = create_sample_farmers(db)
        orders = create_sample_orders(db, customers)
        transactions = create_sample_transactions(db, orders)
        message_templates = create_sample_message_templates(db)
        documents = create_sample_documents(db)
        
        print("Sample data population complete!")
        print(f"Created {len(customers)} customers")
        print(f"Created {len(farmers)} farmers")
        print(f"Created {len(orders)} orders")
        print(f"Created {len(transactions)} transactions")
        print(f"Created {len(message_templates)} message templates")
        print(f"Created {len(documents)} documents")
        
    except Exception as e:
        print(f"Error populating sample data: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main() 