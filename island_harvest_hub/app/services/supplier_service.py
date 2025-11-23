"""
Supplier (Farmer) management service for Island Harvest Hub AI Assistant.
"""

import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models import Farmer, FarmerPayment
from app.database.config import SessionLocal

class SupplierService:
    """Service class for supplier (farmer) management operations."""
    
    def __init__(self):
        self.db: Session = SessionLocal()
    
    def __del__(self):
        """Close database session when service is destroyed."""
        if hasattr(self, 'db'):
            self.db.close()
    
    def create_farmer(self, name: str, business_id: str = 'island_harvest',
                     contact_person: str = None, phone: str = None, 
                     email: str = None, address: str = None, 
                     product_specialties: List[str] = None,
                     pickup_schedule: Dict = None) -> Farmer:
        """Create a new farmer."""
        try:
            # Check for duplicate name within the same business
            existing = self.db.query(Farmer).filter(
                Farmer.name == name,
                Farmer.business_id == business_id
            ).first()
            if existing:
                raise ValueError(f"Supplier '{name}' already exists for this business.")
            
            farmer = Farmer(
                business_id=business_id,
                name=name,
                contact_person=contact_person,
                phone=phone,
                email=email,
                address=address,
                product_specialties=json.dumps(product_specialties) if product_specialties else None,
                pickup_schedule=json.dumps(pickup_schedule) if pickup_schedule else None,
                created_at=datetime.now()
            )
            self.db.add(farmer)
            self.db.commit()
            self.db.refresh(farmer)
            return farmer
        except ValueError:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_farmer(self, farmer_id: int) -> Optional[Farmer]:
        """Get a farmer by ID."""
        return self.db.query(Farmer).filter(Farmer.id == farmer_id).first()
    
    def get_farmer_by_name(self, name: str, business_id: str = None) -> Optional[Farmer]:
        """Get a farmer by name, optionally filtered by business."""
        query = self.db.query(Farmer).filter(Farmer.name == name)
        if business_id:
            query = query.filter(Farmer.business_id == business_id)
        return query.first()
    
    def get_all_farmers(self, business_id: str = None) -> List[Farmer]:
        """Get all farmers, optionally filtered by business."""
        query = self.db.query(Farmer)
        if business_id:
            query = query.filter(Farmer.business_id == business_id)
        return query.order_by(Farmer.name).all()
    
    def update_farmer(self, farmer_id: int, **kwargs) -> Optional[Farmer]:
        """Update farmer information."""
        try:
            farmer = self.get_farmer(farmer_id)
            if not farmer:
                return None
            
            for key, value in kwargs.items():
                if hasattr(farmer, key):
                    if key in ['product_specialties', 'pickup_schedule'] and isinstance(value, (list, dict)):
                        setattr(farmer, key, json.dumps(value))
                    else:
                        setattr(farmer, key, value)
            
            farmer.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(farmer)
            return farmer
        except Exception as e:
            self.db.rollback()
            raise e
    
    def delete_farmer(self, farmer_id: int) -> bool:
        """Delete a farmer."""
        try:
            farmer = self.get_farmer(farmer_id)
            if not farmer:
                return False
            
            self.db.delete(farmer)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_farmer_specialties(self, farmer_id: int) -> List[str]:
        """Get farmer product specialties as a list."""
        farmer = self.get_farmer(farmer_id)
        if not farmer or not farmer.product_specialties:
            return []
        
        try:
            return json.loads(farmer.product_specialties)
        except json.JSONDecodeError:
            return []
    
    def get_farmer_pickup_schedule(self, farmer_id: int) -> Dict:
        """Get farmer pickup schedule as a dictionary."""
        farmer = self.get_farmer(farmer_id)
        if not farmer or not farmer.pickup_schedule:
            return {}
        
        try:
            return json.loads(farmer.pickup_schedule)
        except json.JSONDecodeError:
            return {}
    
    def add_quality_record(self, farmer_id: int, product: str, quality_score: int, notes: str = None) -> Optional[Farmer]:
        """Add a quality record for a farmer's product."""
        farmer = self.get_farmer(farmer_id)
        if not farmer:
            return None
        
        quality_records = []
        if farmer.quality_records:
            try:
                quality_records = json.loads(farmer.quality_records)
            except json.JSONDecodeError:
                quality_records = []
        
        new_record = {
            'date': datetime.now().isoformat(),
            'product': product,
            'quality_score': quality_score,
            'notes': notes
        }
        quality_records.append(new_record)
        
        return self.update_farmer(farmer_id, quality_records=quality_records)
    
    def get_farmer_quality_records(self, farmer_id: int) -> List[Dict]:
        """Get farmer quality records."""
        farmer = self.get_farmer(farmer_id)
        if not farmer or not farmer.quality_records:
            return []
        
        try:
            return json.loads(farmer.quality_records)
        except json.JSONDecodeError:
            return []
    
    def create_payment(self, farmer_id: int, amount: float, notes: str = None) -> Optional[FarmerPayment]:
        """Create a payment record for a farmer."""
        try:
            farmer = self.get_farmer(farmer_id)
            if not farmer:
                return None
            
            payment = FarmerPayment(
                farmer_id=farmer_id,
                payment_date=datetime.now(),
                amount=amount,
                notes=notes
            )
            
            self.db.add(payment)
            self.db.commit()
            self.db.refresh(payment)
            
            # Update farmer's payment history
            payment_history = []
            if farmer.payment_history:
                try:
                    payment_history = json.loads(farmer.payment_history)
                except json.JSONDecodeError:
                    payment_history = []
            
            payment_history.append({
                'date': datetime.now().isoformat(),
                'amount': amount,
                'notes': notes
            })
            
            self.update_farmer(farmer_id, payment_history=payment_history)
            
            return payment
        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_farmer_payments(self, farmer_id: int) -> List[FarmerPayment]:
        """Get all payments for a farmer."""
        return self.db.query(FarmerPayment).filter(FarmerPayment.farmer_id == farmer_id).all()
    
    def get_farmer_payment_history(self, farmer_id: int) -> List[Dict]:
        """Get farmer payment history."""
        farmer = self.get_farmer(farmer_id)
        if not farmer or not farmer.payment_history:
            return []
        
        try:
            return json.loads(farmer.payment_history)
        except json.JSONDecodeError:
            return []
    
    def add_performance_note(self, farmer_id: int, note: str) -> Optional[Farmer]:
        """Add a performance note for a farmer."""
        farmer = self.get_farmer(farmer_id)
        if not farmer:
            return None
        
        existing_notes = farmer.performance_notes or ""
        new_notes = f"{existing_notes}\n[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {note}"
        return self.update_farmer(farmer_id, performance_notes=new_notes.strip())
    
    def add_training_need(self, farmer_id: int, training_need: str) -> Optional[Farmer]:
        """Add a training need for a farmer."""
        farmer = self.get_farmer(farmer_id)
        if not farmer:
            return None
        
        existing_needs = farmer.training_needs or ""
        new_needs = f"{existing_needs}\n[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {training_need}"
        return self.update_farmer(farmer_id, training_needs=new_needs.strip())
    
    def get_farmer_analytics(self, farmer_id: int) -> Dict[str, Any]:
        """Get analytics for a specific farmer."""
        farmer = self.get_farmer(farmer_id)
        if not farmer:
            return {}
        
        payments = self.get_farmer_payments(farmer_id)
        quality_records = self.get_farmer_quality_records(farmer_id)
        
        total_payments = sum(payment.amount for payment in payments)
        payment_count = len(payments)
        avg_payment = total_payments / payment_count if payment_count > 0 else 0
        
        # Calculate average quality score
        quality_scores = [record['quality_score'] for record in quality_records if 'quality_score' in record]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        return {
            'farmer_name': farmer.name,
            'product_specialties': self.get_farmer_specialties(farmer_id),
            'total_payments': total_payments,
            'payment_count': payment_count,
            'average_payment': avg_payment,
            'average_quality_score': avg_quality,
            'quality_record_count': len(quality_records),
            'last_payment_date': max([payment.payment_date for payment in payments]) if payments else None
        }
    
    def get_all_farmers_analytics(self, business_id: str = None) -> Dict[str, Any]:
        """Get analytics for all farmers, optionally filtered by business."""
        farmers = self.get_all_farmers(business_id=business_id)
        # Filter payments by business_id through farmer relationship
        if business_id:
            farmer_ids = [f.id for f in farmers]
            all_payments = self.db.query(FarmerPayment).filter(
                FarmerPayment.farmer_id.in_(farmer_ids)
            ).all() if farmer_ids else []
        else:
            all_payments = self.db.query(FarmerPayment).all()
        
        total_farmers = len(farmers)
        total_payments_amount = sum(payment.amount for payment in all_payments)
        total_payment_count = len(all_payments)
        
        # Top farmers by payment amount
        farmer_payments = {}
        for payment in all_payments:
            farmer_payments[payment.farmer_id] = farmer_payments.get(payment.farmer_id, 0) + payment.amount
        
        top_farmers = sorted(farmer_payments.items(), key=lambda x: x[1], reverse=True)[:5]
        top_farmers_info = []
        for farmer_id, total_payment in top_farmers:
            farmer = self.get_farmer(farmer_id)
            if farmer:
                top_farmers_info.append({
                    'name': farmer.name,
                    'total_payments': total_payment
                })
        
        # Calculate average quality scores across all farmers
        all_quality_scores = []
        for farmer in farmers:
            quality_records = self.get_farmer_quality_records(farmer.id)
            quality_scores = [record['quality_score'] for record in quality_records if 'quality_score' in record]
            all_quality_scores.extend(quality_scores)
        
        avg_quality_all = sum(all_quality_scores) / len(all_quality_scores) if all_quality_scores else 0
        
        return {
            'total_farmers': total_farmers,
            'total_payments_amount': total_payments_amount,
            'total_payment_count': total_payment_count,
            'average_quality_score': avg_quality_all,
            'top_farmers_by_payments': top_farmers_info
        }
    
    def search_farmers_by_product(self, product: str) -> List[Farmer]:
        """Search farmers who specialize in a specific product."""
        farmers = self.get_all_farmers()
        matching_farmers = []
        
        for farmer in farmers:
            specialties = self.get_farmer_specialties(farmer.id)
            if any(product.lower() in specialty.lower() for specialty in specialties):
                matching_farmers.append(farmer)
        
        return matching_farmers

