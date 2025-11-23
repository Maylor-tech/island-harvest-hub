"""
Document generation service for Island Harvest Hub.
Handles creation of invoices, reports, and other business documents.
"""

import os
from datetime import datetime, date
from typing import Dict, List, Optional
import json

class DocumentGenerationService:
    """Service for generating business documents."""
    
    def __init__(self, output_dir: str = "documents"):
        """Initialize document generation service."""
        self.output_dir = output_dir
        self.ensure_output_directory()
    
    def ensure_output_directory(self):
        """Ensure output directory exists."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def generate_invoice(self, customer_data: Dict, order_data: Dict, 
                        invoice_id: str) -> str:
        """
        Generate an invoice document.
        
        Args:
            customer_data: Customer information
            order_data: Order details
            invoice_id: Invoice identifier
            
        Returns:
            Path to generated invoice file
        """
        # Prepare date strings
        current_date = datetime.now().strftime('%B %d, %Y')
        
        invoice_content = f"""
# INVOICE

**Island Harvest Hub**  
Farm-to-Table Distribution  
Port Antonio, Portland Parish, Jamaica  
Phone: +1-876-555-FARM  
Email: info@islandharvesthub.com  

---

**INVOICE #{invoice_id}**  
**Date:** {current_date}  
**Due Date:** {order_data.get('due_date', 'Upon Receipt')}  

---

## BILL TO:
**{customer_data.get('name', 'Customer Name')}**  
{customer_data.get('address', 'Customer Address')}  
Contact: {customer_data.get('contact_person', 'N/A')}  
Phone: {customer_data.get('phone', 'N/A')}  
Email: {customer_data.get('email', 'N/A')}  

---

## ORDER DETAILS:
**Delivery Address:** {order_data.get('delivery_address', customer_data.get('address', 'N/A'))}  
**Delivery Date:** {order_data.get('delivery_date', 'TBD')}  
**Delivery Time:** {order_data.get('delivery_time', 'TBD')}  

---

## ITEMS:

| Item | Quantity | Unit Price | Total |
|------|----------|------------|-------|
"""
        
        # Add order items
        items = order_data.get('items', [])
        subtotal = 0
        
        for item in items:
            quantity = item.get('quantity', 0)
            unit_price = item.get('unit_price', 0)
            total = quantity * unit_price
            subtotal += total
            
            invoice_content += f"| {item.get('name', 'Item')} | {quantity} {item.get('unit', 'units')} | ${unit_price:.2f} | ${total:.2f} |\n"
        
        # Add totals
        delivery_fee = order_data.get('delivery_fee', 0)
        tax = order_data.get('tax', 0)
        total_amount = subtotal + delivery_fee + tax
        
        invoice_content += f"""
---

**Subtotal:** ${subtotal:.2f}  
**Delivery Fee:** ${delivery_fee:.2f}  
**Tax:** ${tax:.2f}  
**TOTAL:** ${total_amount:.2f}  

---

## PAYMENT INFORMATION:
**Payment Methods:**
- Bank Transfer: NCB Account #123-456-789
- Mobile Money: Send to +1-876-555-FARM
- Cash on Delivery (add $5.00 fee)

**Payment Terms:** {order_data.get('payment_terms', 'Net 30 days')}

Please include Invoice #{invoice_id} as reference for all payments.

---

## NOTES:
{order_data.get('notes', 'Thank you for supporting local farmers and choosing Island Harvest Hub!')}

---

*This invoice was generated automatically by Island Harvest Hub AI Assistant*
        """
        
        # Save invoice
        timestamp = datetime.now().strftime('%Y%m%d')
        filename = f"invoice_{invoice_id}_{timestamp}.md"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(invoice_content)
        
        return filepath
    
    def generate_customer_report(self, customer_data: Dict, 
                               analytics_data: Dict) -> str:
        """
        Generate a customer analytics report.
        
        Args:
            customer_data: Customer information
            analytics_data: Customer analytics
            
        Returns:
            Path to generated report file
        """
        # Prepare date strings
        current_datetime = datetime.now().strftime('%B %d, %Y at %I:%M %p')
        
        report_content = f"""
# CUSTOMER ANALYTICS REPORT

**Island Harvest Hub**  
Generated on: {current_datetime}

---

## CUSTOMER OVERVIEW

**Customer Name:** {customer_data.get('name', 'N/A')}  
**Customer ID:** {customer_data.get('id', 'N/A')}  
**Contact Person:** {customer_data.get('contact_person', 'N/A')}  
**Phone:** {customer_data.get('phone', 'N/A')}  
**Email:** {customer_data.get('email', 'N/A')}  
**Address:** {customer_data.get('address', 'N/A')}  
**Customer Since:** {customer_data.get('created_at', 'N/A')}  

---

## PERFORMANCE METRICS

**Total Orders:** {analytics_data.get('total_orders', 0)}  
**Total Revenue:** ${analytics_data.get('total_revenue', 0):,.2f}  
**Average Order Value:** ${analytics_data.get('average_order_value', 0):,.2f}  
**Last Order Date:** {analytics_data.get('last_order_date', 'N/A')}  
**Customer Satisfaction:** {analytics_data.get('satisfaction_score', 'N/A')}/5 ⭐  

---

## ORDER HISTORY

"""
        
        # Add order history if available
        orders = analytics_data.get('recent_orders', [])
        if orders:
            report_content += "| Date | Order ID | Items | Total |\n"
            report_content += "|------|----------|-------|-------|\n"
            
            for order in orders:
                report_content += f"| {order.get('date', 'N/A')} | #{order.get('id', 'N/A')} | {order.get('item_count', 0)} items | ${order.get('total', 0):.2f} |\n"
        else:
            report_content += "*No recent orders found*\n"
        
        report_content += f"""

---

## PREFERENCES

**Preferred Delivery Days:** {', '.join(customer_data.get('delivery_days', []))}  
**Preferred Delivery Time:** {customer_data.get('delivery_time', 'N/A')}  
**Product Interests:** {', '.join(customer_data.get('product_types', []))}  
**Special Requirements:** {customer_data.get('special_requirements', 'None')}  

---

## RECOMMENDATIONS

Based on this customer's order history and preferences:

1. **Product Recommendations:** Focus on {', '.join(customer_data.get('product_types', ['seasonal produce']))}
2. **Delivery Optimization:** Schedule deliveries on {', '.join(customer_data.get('delivery_days', ['preferred days']))}
3. **Relationship Building:** {analytics_data.get('relationship_notes', 'Continue excellent service')}

---

*Report generated by Island Harvest Hub AI Assistant*
        """
        
        # Save report
        timestamp = datetime.now().strftime('%Y%m%d')
        filename = f"customer_report_{customer_data.get('id', 'unknown')}_{timestamp}.md"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(report_content)
        
        return filepath
    
    def generate_supplier_report(self, supplier_data: Dict, 
                               analytics_data: Dict) -> str:
        """
        Generate a supplier performance report.
        
        Args:
            supplier_data: Supplier information
            analytics_data: Supplier analytics
            
        Returns:
            Path to generated report file
        """
        # Prepare date strings
        current_datetime = datetime.now().strftime('%B %d, %Y at %I:%M %p')
        
        report_content = f"""
# SUPPLIER PERFORMANCE REPORT

**Island Harvest Hub**  
Generated on: {current_datetime}

---

## SUPPLIER OVERVIEW

**Supplier Name:** {supplier_data.get('name', 'N/A')}  
**Supplier ID:** {supplier_data.get('id', 'N/A')}  
**Contact Person:** {supplier_data.get('contact_person', 'N/A')}  
**Phone:** {supplier_data.get('phone', 'N/A')}  
**Email:** {supplier_data.get('email', 'N/A')}  
**Farm Address:** {supplier_data.get('address', 'N/A')}  
**Partnership Since:** {supplier_data.get('created_at', 'N/A')}  

---

## PERFORMANCE METRICS

**Total Deliveries:** {analytics_data.get('total_deliveries', 0)}  
**Total Payments:** ${analytics_data.get('total_payments', 0):,.2f}  
**Average Quality Score:** {analytics_data.get('average_quality', 0):.1f}/5 ⭐  
**Last Delivery:** {analytics_data.get('last_delivery_date', 'N/A')}  
**Reliability Score:** {analytics_data.get('reliability_score', 'N/A')}%  

---

## PRODUCT SPECIALTIES

"""
        
        specialties = supplier_data.get('specialties', [])
        if specialties:
            for specialty in specialties:
                report_content += f"- {specialty}\n"
        else:
            report_content += "*No specialties recorded*\n"
        
        report_content += f"""

---

## QUALITY PERFORMANCE

**Recent Quality Scores:**

"""
        
        # Add quality history if available
        quality_records = analytics_data.get('quality_history', [])
        if quality_records:
            report_content += "| Date | Product | Quality Score | Notes |\n"
            report_content += "|------|---------|---------------|-------|\n"
            
            for record in quality_records:
                report_content += f"| {record.get('date', 'N/A')} | {record.get('product', 'N/A')} | {record.get('score', 'N/A')}/5 | {record.get('notes', 'N/A')} |\n"
        else:
            report_content += "*No quality records found*\n"
        
        report_content += f"""

---

## PAYMENT HISTORY

**Recent Payments:**

"""
        
        # Add payment history if available
        payments = analytics_data.get('recent_payments', [])
        if payments:
            report_content += "| Date | Amount | Notes |\n"
            report_content += "|------|--------|-------|\n"
            
            for payment in payments:
                report_content += f"| {payment.get('date', 'N/A')} | ${payment.get('amount', 0):.2f} | {payment.get('notes', 'N/A')} |\n"
        else:
            report_content += "*No recent payments found*\n"
        
        report_content += f"""

---

## PICKUP SCHEDULE

**Preferred Pickup Days:** {', '.join(supplier_data.get('pickup_days', []))}  
**Preferred Pickup Time:** {supplier_data.get('pickup_time', 'N/A')}  

---

## RECOMMENDATIONS

Based on this supplier's performance:

1. **Quality Improvement:** {analytics_data.get('quality_recommendations', 'Continue excellent quality standards')}
2. **Delivery Optimization:** {analytics_data.get('delivery_recommendations', 'Maintain current schedule')}
3. **Partnership Growth:** {analytics_data.get('growth_recommendations', 'Explore expanding product range')}

---

*Report generated by Island Harvest Hub AI Assistant*
        """
        
        # Save report
        timestamp = datetime.now().strftime('%Y%m%d')
        filename = f"supplier_report_{supplier_data.get('id', 'unknown')}_{timestamp}.md"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(report_content)
        
        return filepath
    
    def generate_business_summary(self, business_data: Dict) -> str:
        """
        Generate a business summary report.
        
        Args:
            business_data: Business analytics data
            
        Returns:
            Path to generated report file
        """
        # Prepare date strings
        current_datetime = datetime.now().strftime('%B %d, %Y at %I:%M %p')
        
        # Build report content in parts to avoid f-string issues
        report_header = f"""# BUSINESS SUMMARY REPORT

**Island Harvest Hub**  
Farm-to-Table Distribution Business  
Port Antonio, Portland Parish, Jamaica  

**Report Period:** {business_data.get('period', 'Current Month')}  
**Generated on:** {current_datetime}

---

## EXECUTIVE SUMMARY

Island Harvest Hub continues to connect local farmers with hotels and restaurants across Jamaica, 
providing fresh, quality produce while supporting the local agricultural community.

---

## KEY METRICS

### Customer Metrics
- **Total Customers:** {business_data.get('total_customers', 0)}
- **Active Customers:** {business_data.get('active_customers', 0)}
- **New Customers This Period:** {business_data.get('new_customers', 0)}
- **Customer Retention Rate:** {business_data.get('retention_rate', 0)}%

### Supplier Metrics
- **Total Suppliers:** {business_data.get('total_suppliers', 0)}
- **Active Suppliers:** {business_data.get('active_suppliers', 0)}
- **New Suppliers This Period:** {business_data.get('new_suppliers', 0)}
- **Average Quality Score:** {business_data.get('avg_quality_score', 0):.1f}/5

### Financial Metrics
- **Total Revenue:** ${business_data.get('total_revenue', 0):,.2f}
- **Total Expenses:** ${business_data.get('total_expenses', 0):,.2f}
- **Net Profit:** ${business_data.get('net_profit', 0):,.2f}
- **Profit Margin:** {business_data.get('profit_margin', 0):.1f}%

### Operational Metrics
- **Total Orders:** {business_data.get('total_orders', 0)}
- **Orders Fulfilled:** {business_data.get('fulfilled_orders', 0)}
- **Fulfillment Rate:** {business_data.get('fulfillment_rate', 0)}%
- **Average Delivery Time:** {business_data.get('avg_delivery_time', 'N/A')}

---

## TOP PERFORMERS

### Top Customers by Revenue
"""
        
        # Add top customers
        top_customers = business_data.get('top_customers', [])
        if top_customers:
            for i, customer in enumerate(top_customers, 1):
                report_header += f"{i}. **{customer.get('name', 'N/A')}** - ${customer.get('revenue', 0):,.2f}\n"
        else:
            report_header += "*No customer data available*\n"
        
        report_header += "\n### Top Suppliers by Quality\n"
        
        # Add top suppliers
        top_suppliers = business_data.get('top_suppliers', [])
        if top_suppliers:
            for i, supplier in enumerate(top_suppliers, 1):
                report_header += f"{i}. **{supplier.get('name', 'N/A')}** - {supplier.get('quality_score', 0):.1f}/5 ⭐\n"
        else:
            report_header += "*No supplier data available*\n"
        
        # Build the rest of the report
        challenges = business_data.get('challenges', '- Seasonal produce availability\n- Weather-dependent deliveries\n- Quality consistency')
        opportunities = business_data.get('opportunities', '- Expand to new parishes\n- Add organic certification program\n- Develop mobile app for customers')
        short_term_goals = business_data.get('short_term_goals', '- Reach 30 active customers\n- Onboard 5 new suppliers\n- Achieve 95% fulfillment rate')
        long_term_goals = business_data.get('long_term_goals', '- Expand to Kingston market\n- Launch organic produce line\n- Implement farm-to-table certification')
        customer_recommendations = business_data.get('customer_recommendations', 'Focus on boutique hotels and high-end restaurants')
        supplier_recommendations = business_data.get('supplier_recommendations', 'Invest in farmer training programs')
        operational_recommendations = business_data.get('operational_recommendations', 'Optimize delivery routes and schedules')
        financial_recommendations = business_data.get('financial_recommendations', 'Improve cash flow with better payment terms')
        conclusion = business_data.get('conclusion', 'Island Harvest Hub is well-positioned for continued growth in the Jamaica farm-to-table market. Focus on quality, reliability, and community partnerships will drive future success.')
        
        report_content = report_header + f"""

---

## CHALLENGES & OPPORTUNITIES

### Current Challenges
{challenges}

### Growth Opportunities
{opportunities}

---

## STRATEGIC GOALS

### Short-term Goals (Next 3 Months)
{short_term_goals}

### Long-term Goals (Next 12 Months)
{long_term_goals}

---

## RECOMMENDATIONS

Based on current performance and market conditions:

1. **Customer Acquisition:** {customer_recommendations}

2. **Supplier Development:** {supplier_recommendations}

3. **Operational Efficiency:** {operational_recommendations}

4. **Financial Management:** {financial_recommendations}

---

## CONCLUSION

{conclusion}

---

*Report generated by Island Harvest Hub AI Assistant*  
*For questions about this report, contact Brian Miller at brian@islandharvesthub.com*
"""
        
        # Save report
        timestamp = datetime.now().strftime('%Y%m%d')
        filename = f"business_summary_{timestamp}.md"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(report_content)
        
        return filepath
    
    def convert_to_pdf(self, markdown_file: str) -> str:
        """
        Convert markdown file to PDF using manus-md-to-pdf utility.
        
        Args:
            markdown_file: Path to markdown file
            
        Returns:
            Path to generated PDF file
        """
        pdf_file = markdown_file.replace('.md', '.pdf')
        
        # Use the pre-installed utility
        os.system(f"manus-md-to-pdf {markdown_file} {pdf_file}")
        
        return pdf_file
    
    def get_document_templates(self) -> List[Dict]:
        """
        Get available document templates.
        
        Returns:
            List of document templates
        """
        return [
            {
                "name": "invoice",
                "title": "Customer Invoice",
                "description": "Generate professional invoices for customer orders",
                "required_data": ["customer_data", "order_data", "invoice_id"]
            },
            {
                "name": "customer_report",
                "title": "Customer Analytics Report",
                "description": "Detailed customer performance and analytics report",
                "required_data": ["customer_data", "analytics_data"]
            },
            {
                "name": "supplier_report",
                "title": "Supplier Performance Report",
                "description": "Comprehensive supplier performance analysis",
                "required_data": ["supplier_data", "analytics_data"]
            },
            {
                "name": "business_summary",
                "title": "Business Summary Report",
                "description": "Executive summary of business performance",
                "required_data": ["business_data"]
            }
        ]
    
    def list_generated_documents(self) -> List[Dict]:
        """
        List all generated documents.
        
        Returns:
            List of document information
        """
        documents = []
        
        if os.path.exists(self.output_dir):
            for filename in os.listdir(self.output_dir):
                if filename.endswith(('.md', '.pdf')):
                    filepath = os.path.join(self.output_dir, filename)
                    stat = os.stat(filepath)
                    
                    documents.append({
                        "filename": filename,
                        "filepath": filepath,
                        "size": stat.st_size,
                        "created": datetime.fromtimestamp(stat.st_ctime),
                        "modified": datetime.fromtimestamp(stat.st_mtime),
                        "type": "PDF" if filename.endswith('.pdf') else "Markdown"
                    })
        
        return sorted(documents, key=lambda x: x["modified"], reverse=True)

