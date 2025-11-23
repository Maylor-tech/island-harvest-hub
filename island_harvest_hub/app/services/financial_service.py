"""
Financial management service for Island Harvest Hub AI Assistant.
"""

from datetime import datetime, date
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models import Transaction, Invoice, Order, Customer
from app.database.config import SessionLocal

class FinancialService:
    """Service class for financial management operations."""
    
    def __init__(self):
        self.db: Session = SessionLocal()
    
    def __del__(self):
        """Close database session when service is destroyed."""
        if hasattr(self, 'db'):
            self.db.close()
    
    def create_transaction(self, date: datetime, transaction_type: str, 
                          description: str, amount: float,
                          related_entity_id: int = None, 
                          related_entity_type: str = None) -> Transaction:
        """Create a new financial transaction."""
        try:
            transaction = Transaction(
                date=date,
                type=transaction_type,
                description=description,
                amount=amount,
                related_entity_id=related_entity_id,
                related_entity_type=related_entity_type,
                created_at=datetime.now()
            )
            
            self.db.add(transaction)
            self.db.commit()
            self.db.refresh(transaction)
            return transaction
        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_transaction(self, transaction_id: int) -> Optional[Transaction]:
        """Get a transaction by ID."""
        return self.db.query(Transaction).filter(Transaction.id == transaction_id).first()
    
    def get_all_transactions(self) -> List[Transaction]:
        """Get all transactions."""
        return self.db.query(Transaction).order_by(Transaction.date.desc()).all()
    
    def get_transactions_by_type(self, transaction_type: str) -> List[Transaction]:
        """Get transactions by type."""
        return self.db.query(Transaction).filter(Transaction.type == transaction_type).order_by(Transaction.date.desc()).all()
    
    def get_transactions_by_date_range(self, start_date: date, end_date: date) -> List[Transaction]:
        """Get transactions within a date range."""
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        return self.db.query(Transaction).filter(
            Transaction.date >= start_datetime,
            Transaction.date <= end_datetime
        ).order_by(Transaction.date.desc()).all()
    
    def update_transaction(self, transaction_id: int, **kwargs) -> Optional[Transaction]:
        """Update transaction information."""
        try:
            transaction = self.get_transaction(transaction_id)
            if not transaction:
                return None
            
            for key, value in kwargs.items():
                if hasattr(transaction, key):
                    setattr(transaction, key, value)
            
            transaction.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(transaction)
            return transaction
        except Exception as e:
            self.db.rollback()
            raise e
    
    def delete_transaction(self, transaction_id: int) -> bool:
        """Delete a transaction."""
        try:
            transaction = self.get_transaction(transaction_id)
            if not transaction:
                return False
            
            self.db.delete(transaction)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e
    
    def create_invoice(self, customer_id: int, order_id: int, 
                      invoice_date: datetime, due_date: datetime,
                      total_amount: float) -> Invoice:
        """Create a new invoice."""
        try:
            invoice = Invoice(
                customer_id=customer_id,
                order_id=order_id,
                invoice_date=invoice_date,
                due_date=due_date,
                total_amount=total_amount,
                status="Issued",
                created_at=datetime.now()
            )
            
            self.db.add(invoice)
            self.db.commit()
            self.db.refresh(invoice)
            
            # Create corresponding revenue transaction
            customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
            customer_name = customer.name if customer else f"Customer {customer_id}"
            
            self.create_transaction(
                date=invoice_date,
                transaction_type="Revenue",
                description=f"Invoice #{invoice.id} for {customer_name}",
                amount=total_amount,
                related_entity_id=invoice.id,
                related_entity_type="Invoice"
            )
            
            return invoice
        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_invoice(self, invoice_id: int) -> Optional[Invoice]:
        """Get an invoice by ID."""
        return self.db.query(Invoice).filter(Invoice.id == invoice_id).first()
    
    def get_all_invoices(self) -> List[Invoice]:
        """Get all invoices."""
        return self.db.query(Invoice).order_by(Invoice.invoice_date.desc()).all()
    
    def get_invoices_by_customer(self, customer_id: int) -> List[Invoice]:
        """Get invoices for a specific customer."""
        return self.db.query(Invoice).filter(Invoice.customer_id == customer_id).order_by(Invoice.invoice_date.desc()).all()
    
    def get_overdue_invoices(self) -> List[Invoice]:
        """Get overdue invoices."""
        current_date = datetime.now()
        return self.db.query(Invoice).filter(
            Invoice.due_date < current_date,
            Invoice.status != "Paid"
        ).all()
    
    def update_invoice_status(self, invoice_id: int, status: str) -> Optional[Invoice]:
        """Update invoice status."""
        try:
            invoice = self.get_invoice(invoice_id)
            if not invoice:
                return None
            
            old_status = invoice.status
            invoice.status = status
            invoice.updated_at = datetime.now()
            
            # If invoice is marked as paid, create a payment transaction
            if status == "Paid" and old_status != "Paid":
                customer = self.db.query(Customer).filter(Customer.id == invoice.customer_id).first()
                customer_name = customer.name if customer else f"Customer {invoice.customer_id}"
                
                self.create_transaction(
                    date=datetime.now(),
                    transaction_type="Payment Received",
                    description=f"Payment received for Invoice #{invoice.id} from {customer_name}",
                    amount=invoice.total_amount,
                    related_entity_id=invoice.id,
                    related_entity_type="Invoice"
                )
            
            self.db.commit()
            self.db.refresh(invoice)
            return invoice
        except Exception as e:
            self.db.rollback()
            raise e
    
    def create_expense_transaction(self, date: datetime, description: str, 
                                 amount: float, category: str = None) -> Transaction:
        """Create an expense transaction."""
        expense_description = f"{category}: {description}" if category else description
        return self.create_transaction(
            date=date,
            transaction_type="Expense",
            description=expense_description,
            amount=-abs(amount)  # Expenses are negative
        )
    
    def create_farmer_payment_transaction(self, farmer_id: int, amount: float, 
                                        description: str = None) -> Transaction:
        """Create a farmer payment transaction."""
        payment_description = description or f"Payment to Farmer ID {farmer_id}"
        return self.create_transaction(
            date=datetime.now(),
            transaction_type="Farmer Payment",
            description=payment_description,
            amount=-abs(amount),  # Payments are negative (outgoing)
            related_entity_id=farmer_id,
            related_entity_type="Farmer"
        )
    
    def get_revenue_summary(self, start_date: date = None, end_date: date = None) -> Dict[str, Any]:
        """Get revenue summary for a date range."""
        transactions = self.get_transactions_by_date_range(start_date, end_date) if start_date and end_date else self.get_all_transactions()
        
        revenue_transactions = [t for t in transactions if t.type in ["Revenue", "Payment Received"]]
        total_revenue = sum(t.amount for t in revenue_transactions)
        
        # Group by month for trend analysis
        monthly_revenue = {}
        for transaction in revenue_transactions:
            month_key = transaction.date.strftime("%Y-%m")
            monthly_revenue[month_key] = monthly_revenue.get(month_key, 0) + transaction.amount
        
        return {
            'total_revenue': total_revenue,
            'transaction_count': len(revenue_transactions),
            'average_transaction': total_revenue / len(revenue_transactions) if revenue_transactions else 0,
            'monthly_breakdown': monthly_revenue
        }
    
    def get_expense_summary(self, start_date: date = None, end_date: date = None) -> Dict[str, Any]:
        """Get expense summary for a date range."""
        transactions = self.get_transactions_by_date_range(start_date, end_date) if start_date and end_date else self.get_all_transactions()
        
        expense_transactions = [t for t in transactions if t.type in ["Expense", "Farmer Payment"]]
        total_expenses = sum(abs(t.amount) for t in expense_transactions)
        
        # Group by category (extracted from description)
        expense_categories = {}
        for transaction in expense_transactions:
            category = transaction.description.split(':')[0] if ':' in transaction.description else 'Other'
            expense_categories[category] = expense_categories.get(category, 0) + abs(transaction.amount)
        
        # Group by month for trend analysis
        monthly_expenses = {}
        for transaction in expense_transactions:
            month_key = transaction.date.strftime("%Y-%m")
            monthly_expenses[month_key] = monthly_expenses.get(month_key, 0) + abs(transaction.amount)
        
        return {
            'total_expenses': total_expenses,
            'transaction_count': len(expense_transactions),
            'average_expense': total_expenses / len(expense_transactions) if expense_transactions else 0,
            'category_breakdown': expense_categories,
            'monthly_breakdown': monthly_expenses
        }
    
    def get_profit_loss_summary(self, start_date: date = None, end_date: date = None) -> Dict[str, Any]:
        """Get profit and loss summary for a date range."""
        revenue_summary = self.get_revenue_summary(start_date, end_date)
        expense_summary = self.get_expense_summary(start_date, end_date)
        
        total_revenue = revenue_summary['total_revenue']
        total_expenses = expense_summary['total_expenses']
        net_profit = total_revenue - total_expenses
        profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        return {
            'total_revenue': total_revenue,
            'total_expenses': total_expenses,
            'net_profit': net_profit,
            'profit_margin_percentage': profit_margin,
            'revenue_breakdown': revenue_summary,
            'expense_breakdown': expense_summary
        }
    
    def get_cash_flow_analysis(self, start_date: date = None, end_date: date = None) -> Dict[str, Any]:
        """Get cash flow analysis for a date range."""
        transactions = self.get_transactions_by_date_range(start_date, end_date) if start_date and end_date else self.get_all_transactions()
        
        cash_inflows = sum(t.amount for t in transactions if t.amount > 0)
        cash_outflows = sum(abs(t.amount) for t in transactions if t.amount < 0)
        net_cash_flow = cash_inflows - cash_outflows
        
        # Daily cash flow
        daily_cash_flow = {}
        for transaction in transactions:
            date_key = transaction.date.strftime("%Y-%m-%d")
            daily_cash_flow[date_key] = daily_cash_flow.get(date_key, 0) + transaction.amount
        
        return {
            'cash_inflows': cash_inflows,
            'cash_outflows': cash_outflows,
            'net_cash_flow': net_cash_flow,
            'daily_cash_flow': daily_cash_flow
        }
    
    def get_accounts_receivable(self) -> Dict[str, Any]:
        """Get accounts receivable summary."""
        unpaid_invoices = self.db.query(Invoice).filter(Invoice.status != "Paid").all()
        overdue_invoices = self.get_overdue_invoices()
        
        total_outstanding = sum(invoice.total_amount for invoice in unpaid_invoices)
        total_overdue = sum(invoice.total_amount for invoice in overdue_invoices)
        
        # Group by customer
        customer_balances = {}
        for invoice in unpaid_invoices:
            customer_id = invoice.customer_id
            customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
            customer_name = customer.name if customer else f"Customer {customer_id}"
            
            if customer_name not in customer_balances:
                customer_balances[customer_name] = {
                    'total_outstanding': 0,
                    'overdue_amount': 0,
                    'invoice_count': 0
                }
            
            customer_balances[customer_name]['total_outstanding'] += invoice.total_amount
            customer_balances[customer_name]['invoice_count'] += 1
            
            if invoice in overdue_invoices:
                customer_balances[customer_name]['overdue_amount'] += invoice.total_amount
        
        return {
            'total_outstanding': total_outstanding,
            'total_overdue': total_overdue,
            'unpaid_invoice_count': len(unpaid_invoices),
            'overdue_invoice_count': len(overdue_invoices),
            'customer_balances': customer_balances
        }

