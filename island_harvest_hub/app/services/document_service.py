"""
Document management service for Island Harvest Hub AI Assistant.
"""

import os
import json
import shutil
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models import Document
from app.database.config import SessionLocal

class DocumentService:
    """Service class for document management operations."""
    
    def __init__(self, base_document_path: str = "documents"):
        self.db: Session = SessionLocal()
        self.base_path = base_document_path
        self._ensure_document_directories()
    
    def __del__(self):
        """Close database session when service is destroyed."""
        if hasattr(self, 'db'):
            self.db.close()
    
    def _ensure_document_directories(self):
        """Ensure document directories exist."""
        directories = [
            self.base_path,
            os.path.join(self.base_path, "invoices"),
            os.path.join(self.base_path, "reports"),
            os.path.join(self.base_path, "contracts"),
            os.path.join(self.base_path, "templates"),
            os.path.join(self.base_path, "backups")
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def create_document_record(self, name: str, file_path: str, 
                              doc_type: str = None, version: str = "1.0") -> Document:
        """Create a new document record in the database."""
        try:
            document = Document(
                name=name,
                file_path=file_path,
                type=doc_type,
                version=version,
                created_at=datetime.now()
            )
            
            self.db.add(document)
            self.db.commit()
            self.db.refresh(document)
            return document
        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_document(self, document_id: int) -> Optional[Document]:
        """Get a document by ID."""
        return self.db.query(Document).filter(Document.id == document_id).first()
    
    def get_document_by_path(self, file_path: str) -> Optional[Document]:
        """Get a document by file path."""
        return self.db.query(Document).filter(Document.file_path == file_path).first()
    
    def get_all_documents(self) -> List[Document]:
        """Get all documents."""
        return self.db.query(Document).order_by(Document.created_at.desc()).all()
    
    def get_documents_by_type(self, doc_type: str) -> List[Document]:
        """Get documents by type."""
        return self.db.query(Document).filter(
            Document.type == doc_type
        ).order_by(Document.created_at.desc()).all()
    
    def update_document(self, document_id: int, **kwargs) -> Optional[Document]:
        """Update document information."""
        try:
            document = self.get_document(document_id)
            if not document:
                return None
            
            for key, value in kwargs.items():
                if hasattr(document, key):
                    setattr(document, key, value)
            
            document.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(document)
            return document
        except Exception as e:
            self.db.rollback()
            raise e
    
    def delete_document(self, document_id: int, delete_file: bool = False) -> bool:
        """Delete a document record and optionally the file."""
        try:
            document = self.get_document(document_id)
            if not document:
                return False
            
            # Delete physical file if requested
            if delete_file and os.path.exists(document.file_path):
                os.remove(document.file_path)
            
            self.db.delete(document)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e
    
    def generate_file_name(self, base_name: str, doc_type: str, 
                          extension: str = ".pdf") -> str:
        """Generate a standardized file name."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = "".join(c for c in base_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_')
        
        return f"{doc_type}_{safe_name}_{timestamp}{extension}"
    
    def get_file_path(self, doc_type: str, filename: str) -> str:
        """Get the full file path for a document."""
        type_folder = doc_type.lower() + "s" if not doc_type.endswith('s') else doc_type.lower()
        return os.path.join(self.base_path, type_folder, filename)
    
    def create_invoice_document(self, invoice_data: Dict[str, Any]) -> str:
        """Create an invoice document."""
        filename = self.generate_file_name(
            f"invoice_{invoice_data.get('customer_name', 'unknown')}", 
            "invoice"
        )
        file_path = self.get_file_path("invoice", filename)
        
        # Create invoice content (simplified HTML/text format)
        invoice_content = self._generate_invoice_content(invoice_data)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(invoice_content)
        
        # Create document record
        self.create_document_record(
            name=f"Invoice #{invoice_data.get('invoice_id', 'N/A')}",
            file_path=file_path,
            doc_type="Invoice"
        )
        
        return file_path
    
    def _generate_invoice_content(self, invoice_data: Dict[str, Any]) -> str:
        """Generate invoice content in HTML format."""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Invoice #{invoice_data.get('invoice_id', 'N/A')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .company-info {{ margin-bottom: 20px; }}
        .invoice-details {{ margin-bottom: 20px; }}
        .items-table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
        .items-table th, .items-table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        .items-table th {{ background-color: #f2f2f2; }}
        .total {{ text-align: right; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Island Harvest Hub</h1>
        <p>Port Antonio, Portland Parish, Jamaica</p>
        <p>Farm-to-Table Distribution</p>
    </div>
    
    <div class="company-info">
        <h2>INVOICE</h2>
        <p><strong>Invoice #:</strong> {invoice_data.get('invoice_id', 'N/A')}</p>
        <p><strong>Date:</strong> {invoice_data.get('invoice_date', datetime.now().strftime('%Y-%m-%d'))}</p>
        <p><strong>Due Date:</strong> {invoice_data.get('due_date', 'N/A')}</p>
    </div>
    
    <div class="invoice-details">
        <h3>Bill To:</h3>
        <p><strong>{invoice_data.get('customer_name', 'N/A')}</strong></p>
        <p>{invoice_data.get('customer_address', 'N/A')}</p>
        <p>Contact: {invoice_data.get('customer_contact', 'N/A')}</p>
    </div>
    
    <table class="items-table">
        <thead>
            <tr>
                <th>Product</th>
                <th>Quantity</th>
                <th>Unit Price</th>
                <th>Total</th>
            </tr>
        </thead>
        <tbody>
"""
        
        # Add items
        items = invoice_data.get('items', [])
        for item in items:
            invoice_content += f"""
            <tr>
                <td>{item.get('product_name', 'N/A')}</td>
                <td>{item.get('quantity', 0)}</td>
                <td>${item.get('unit_price', 0):.2f}</td>
                <td>${item.get('subtotal', 0):.2f}</td>
            </tr>
"""
        
        invoice_content += f"""
        </tbody>
    </table>
    
    <div class="total">
        <p><strong>Total Amount: ${invoice_data.get('total_amount', 0):.2f}</strong></p>
    </div>
    
    <div style="margin-top: 30px;">
        <p>Thank you for your business!</p>
        <p>For questions about this invoice, please contact Brian Miller.</p>
    </div>
</body>
</html>
"""
        return invoice_content
    
    def create_report_document(self, report_type: str, report_data: Dict[str, Any]) -> str:
        """Create a report document."""
        filename = self.generate_file_name(f"{report_type}_report", "report")
        file_path = self.get_file_path("report", filename)
        
        # Create report content based on type
        if report_type == "customer_analytics":
            content = self._generate_customer_analytics_report(report_data)
        elif report_type == "financial_summary":
            content = self._generate_financial_summary_report(report_data)
        elif report_type == "operations_summary":
            content = self._generate_operations_summary_report(report_data)
        else:
            content = self._generate_generic_report(report_type, report_data)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Create document record
        self.create_document_record(
            name=f"{report_type.replace('_', ' ').title()} Report",
            file_path=file_path,
            doc_type="Report"
        )
        
        return file_path
    
    def _generate_customer_analytics_report(self, data: Dict[str, Any]) -> str:
        """Generate customer analytics report."""
        return f"""
# Customer Analytics Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- Total Customers: {data.get('total_customers', 0)}
- Total Orders: {data.get('total_orders', 0)}
- Total Revenue: ${data.get('total_revenue', 0):.2f}
- Average Satisfaction Score: {data.get('average_satisfaction_score', 0):.1f}/5

## Top Customers by Revenue
{self._format_top_customers(data.get('top_customers', []))}

## Recommendations
- Focus on maintaining relationships with top revenue customers
- Implement customer satisfaction improvement programs
- Consider loyalty programs for repeat customers
"""
    
    def _generate_financial_summary_report(self, data: Dict[str, Any]) -> str:
        """Generate financial summary report."""
        return f"""
# Financial Summary Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Profit & Loss Summary
- Total Revenue: ${data.get('total_revenue', 0):.2f}
- Total Expenses: ${data.get('total_expenses', 0):.2f}
- Net Profit: ${data.get('net_profit', 0):.2f}
- Profit Margin: {data.get('profit_margin_percentage', 0):.1f}%

## Cash Flow
- Cash Inflows: ${data.get('cash_inflows', 0):.2f}
- Cash Outflows: ${data.get('cash_outflows', 0):.2f}
- Net Cash Flow: ${data.get('net_cash_flow', 0):.2f}

## Accounts Receivable
- Total Outstanding: ${data.get('total_outstanding', 0):.2f}
- Overdue Amount: ${data.get('total_overdue', 0):.2f}
"""
    
    def _generate_operations_summary_report(self, data: Dict[str, Any]) -> str:
        """Generate operations summary report."""
        return f"""
# Operations Summary Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Daily Operations
- Total Days Logged: {data.get('total_days_logged', 0)}
- Total Orders Fulfilled: {data.get('total_orders_fulfilled', 0)}
- Average Orders per Day: {data.get('average_orders_per_day', 0):.1f}

## Quality Control
- Average Temperature: {data.get('average_temperature', 0):.1f}°C
- Temperature Readings: {data.get('temperature_readings_count', 0)}

## Issue Tracking
- Total Issues: {data.get('total_issues', 0)}
- Open Issues: {data.get('open_issues', 0)}
- Resolved Issues: {data.get('resolved_issues', 0)}
"""
    
    def _generate_generic_report(self, report_type: str, data: Dict[str, Any]) -> str:
        """Generate a generic report."""
        content = f"""
# {report_type.replace('_', ' ').title()} Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Data Summary
"""
        for key, value in data.items():
            content += f"- {key.replace('_', ' ').title()}: {value}\n"
        
        return content
    
    def _format_top_customers(self, top_customers: List[Dict]) -> str:
        """Format top customers list for report."""
        if not top_customers:
            return "No customer data available."
        
        formatted = ""
        for i, customer in enumerate(top_customers, 1):
            formatted += f"{i}. {customer.get('name', 'Unknown')} - ${customer.get('revenue', 0):.2f}\n"
        
        return formatted
    
    def create_backup(self, source_path: str) -> str:
        """Create a backup of a document."""
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source file not found: {source_path}")
        
        filename = os.path.basename(source_path)
        name, ext = os.path.splitext(filename)
        backup_filename = f"{name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
        backup_path = os.path.join(self.base_path, "backups", backup_filename)
        
        shutil.copy2(source_path, backup_path)
        
        # Create document record for backup
        self.create_document_record(
            name=f"Backup of {filename}",
            file_path=backup_path,
            doc_type="Backup"
        )
        
        return backup_path
    
    def get_document_templates(self) -> List[str]:
        """Get list of available document templates."""
        templates_path = os.path.join(self.base_path, "templates")
        if not os.path.exists(templates_path):
            return []
        
        return [f for f in os.listdir(templates_path) if f.endswith(('.html', '.txt', '.md'))]
    
    def create_document_from_template(self, template_name: str, 
                                    output_name: str, variables: Dict[str, str]) -> str:
        """Create a document from a template."""
        template_path = os.path.join(self.base_path, "templates", template_name)
        
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template not found: {template_name}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Replace variables in template
        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            template_content = template_content.replace(placeholder, str(value))
        
        # Generate output file
        output_path = os.path.join(self.base_path, output_name)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        # Create document record
        self.create_document_record(
            name=output_name,
            file_path=output_path,
            doc_type="Generated"
        )
        
        return output_path
    
    def get_document_statistics(self) -> Dict[str, Any]:
        """Get document management statistics."""
        documents = self.get_all_documents()
        
        # Count by type
        type_counts = {}
        for doc in documents:
            doc_type = doc.type or "Unknown"
            type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
        
        # Calculate storage usage (simplified)
        total_size = 0
        for doc in documents:
            if os.path.exists(doc.file_path):
                total_size += os.path.getsize(doc.file_path)
        
        return {
            'total_documents': len(documents),
            'documents_by_type': type_counts,
            'total_storage_bytes': total_size,
            'total_storage_mb': total_size / (1024 * 1024)
        }

