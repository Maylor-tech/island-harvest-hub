"""
Main Streamlit application for Island Harvest Hub AI Assistant.
"""

import streamlit as st
import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load API key from Streamlit secrets (for Streamlit Cloud) or .env file (for local)
if not os.environ.get('ANTHROPIC_API_KEY'):
    # First, try to get from Streamlit secrets (for Streamlit Cloud)
    try:
        if hasattr(st, 'secrets'):
            # Try dictionary access
            if 'ANTHROPIC_API_KEY' in st.secrets:
                api_key = st.secrets['ANTHROPIC_API_KEY']
                if api_key:
                    os.environ['ANTHROPIC_API_KEY'] = str(api_key).strip()
            # Try attribute access as fallback
            elif hasattr(st.secrets, 'ANTHROPIC_API_KEY'):
                api_key = getattr(st.secrets, 'ANTHROPIC_API_KEY', '')
                if api_key:
                    os.environ['ANTHROPIC_API_KEY'] = str(api_key).strip()
    except Exception as e:
        # Silently fail - secrets might not be available yet
        pass
    
    # If not in secrets, try to find .env file in parent directory (project root)
    if not os.environ.get('ANTHROPIC_API_KEY'):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        env_path = os.path.join(parent_dir, '.env')
        
        if os.path.exists(env_path):
            try:
                with open(env_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            if key.strip() == 'ANTHROPIC_API_KEY':
                                os.environ[key.strip()] = value.strip()
            except Exception:
                pass

from app.services.customer_service import CustomerService
from app.services.supplier_service import SupplierService
from app.services.operations_service import OperationsService
from app.services.financial_service import FinancialService
from app.services.strategic_service import StrategicPlanningService
from app.services.communication_service import CommunicationService
from app.services.document_service import DocumentService
from pages.database_management import main as show_database_management
from pages.ai_advisor import show_ai_advisor
from pages.unified_financials import show_unified_financials
from app.config.business_profiles import get_all_active_businesses, get_business_display_names, get_business_profile
from app.database.config import init_db, DATABASE_PATH
from app.utils.auth import check_password, login, show_logout_button
from pathlib import Path
import sqlite3

# Auto-initialize database if it doesn't exist (for Streamlit Cloud deployment)
def ensure_database_initialized():
    """Ensure database exists and is initialized."""
    db_path = Path(DATABASE_PATH)
    
    # Check if database file exists
    if not db_path.exists():
        try:
            # Initialize database
            init_db()
            # Run migration to add business_id columns if needed
            import sys
            migrate_script = os.path.join(os.path.dirname(__file__), 'migrate_add_business_id.py')
            if os.path.exists(migrate_script):
                import importlib.util
                spec = importlib.util.spec_from_file_location("migrate_add_business_id", migrate_script)
                migrate_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(migrate_module)
                migrate_module.migrate_database()
            return True
        except Exception as e:
            st.error(f"Error initializing database: {str(e)}")
            return False
    else:
        # Database exists, check if tables exist
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='customers'")
            if not cursor.fetchone():
                # Database exists but tables don't, initialize
                init_db()
                # Run migration
                migrate_script = os.path.join(os.path.dirname(__file__), 'migrate_add_business_id.py')
                if os.path.exists(migrate_script):
                    import importlib.util
                    spec = importlib.util.spec_from_file_location("migrate_add_business_id", migrate_script)
                    migrate_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(migrate_module)
                    migrate_module.migrate_database()
            else:
                # Check if business_id column exists
                cursor.execute("PRAGMA table_info(customers)")
                columns = [col[1] for col in cursor.fetchall()]
                if 'business_id' not in columns:
                    # Run migration to add business_id
                    migrate_script = os.path.join(os.path.dirname(__file__), 'migrate_add_business_id.py')
                    if os.path.exists(migrate_script):
                        import importlib.util
                        spec = importlib.util.spec_from_file_location("migrate_add_business_id", migrate_script)
                        migrate_module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(migrate_module)
                        migrate_module.migrate_database()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Error checking database: {str(e)}")
            return False

# Initialize database on app start (only once per session)
if 'db_initialized' not in st.session_state:
    ensure_database_initialized()
    st.session_state.db_initialized = True

# Page configuration
st.set_page_config(
    page_title="Island Harvest Hub AI Assistant",
    page_icon="🌴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Jamaica-themed styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #009639 0%, #FFCD00 50%, #000000 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        color: white;
        text-align: center;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #009639;
    }
    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 0.75rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
    }
    .warning-message {
        background: #fff3cd;
        color: #856404;
        padding: 0.75rem;
        border-radius: 5px;
        border: 1px solid #ffeaa7;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #009639 0%, #FFCD00 100%);
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application function."""
    
    # Check authentication - must be logged in to access
    if not check_password():
        login()
        return
    
    # Show logout button in sidebar
    show_logout_button()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🌴 Island Harvest Hub AI Assistant</h1>
        <p style="text-align: center; color: white; margin: 0;">
            Farm-to-Table Distribution Management • Port Antonio, Jamaica
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Business Profile Selector
    st.markdown("---")
    st.markdown("### 🏢 Business Profile")
    
    # Initialize session state for business selection
    if 'selected_business' not in st.session_state:
        st.session_state.selected_business = 'island_harvest'
    
    # Get business profiles
    business_names = get_business_display_names()
    business_ids = list(get_all_active_businesses().keys())
    
    # Create a mapping between display names and IDs
    name_to_id = {get_business_profile(bid)["display_name"]: bid for bid in business_ids}
    
    # Business selector
    selected_display_name = st.selectbox(
        "Select Business:",
        business_names,
        index=business_ids.index(st.session_state.selected_business) if st.session_state.selected_business in business_ids else 0,
        key="business_selector"
    )
    
    # Update session state
    st.session_state.selected_business = name_to_id[selected_display_name]
    
    # Get current business profile
    current_business = get_business_profile(st.session_state.selected_business)
    
    # Display business info
    st.info(f"**{current_business['name']}**\n\n{current_business['tagline']}")
    
    st.markdown("---")
    
    # Sidebar navigation
    st.sidebar.title("🏝️ Navigation")
    st.sidebar.markdown("---")
    
    # Navigation options
    pages = {
        "🏠 Dashboard": "dashboard",
        "👥 Customer Management": "customers",
        "🚜 Supplier Management": "suppliers", 
        "📋 Daily Operations": "operations",
        "💰 Financial Management": "financial",
        "📞 Communication Hub": "communication",
        "📄 Document Center": "documents",
        "🎯 Strategic Planning": "strategic",
        "🗄️ Database Management": "database",
        "🤖 AI Business Advisor": "ai_advisor",
        "💰 Unified Financials": "unified_financials"
    }
    
    selected_page = st.sidebar.selectbox(
        "Select a module:",
        list(pages.keys()),
        index=0
    )
    
    # Add motivational quote
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    ### 💪 Daily Motivation
    *"Success is not final, failure is not fatal: it is the courage to continue that counts."*
    
    **Keep growing, Brian! 🌱**
    """)
    
    # Route to selected page
    page_key = pages[selected_page]
    
    try:
        if page_key == "dashboard":
            show_dashboard()
        elif page_key == "customers":
            show_customer_management()
        elif page_key == "suppliers":
            show_supplier_management()
        elif page_key == "operations":
            show_operations_management()
        elif page_key == "financial":
            show_financial_management()
        elif page_key == "communication":
            show_communication_hub()
        elif page_key == "documents":
            show_document_center()
        elif page_key == "strategic":
            show_strategic_planning()
        elif page_key == "database":
            show_database_management()
        elif page_key == "ai_advisor":
            show_ai_advisor()
        elif page_key == "unified_financials":
            show_unified_financials()
        else:
            st.error(f"Page '{page_key}' not found. Please select a valid page from the sidebar.")
    except Exception as e:
        st.error(f"❌ Error loading page: {str(e)}")
        st.exception(e)  # Show full traceback for debugging
        st.info("💡 Try refreshing the page or selecting a different module from the sidebar.")

def show_dashboard():
    """Display the main dashboard."""
    st.header("📊 Business Dashboard")
    
    # Initialize services
    customer_service = CustomerService()
    supplier_service = SupplierService()
    financial_service = FinancialService()
    strategic_service = StrategicPlanningService()
    
    try:
        # Get selected business from session state
        selected_business = st.session_state.get('selected_business', 'island_harvest')
        
        # Get analytics data filtered by business
        customer_analytics = customer_service.get_all_customers_analytics(business_id=selected_business)
        supplier_analytics = supplier_service.get_all_farmers_analytics(business_id=selected_business)
        financial_summary = financial_service.get_profit_loss_summary()
        strategic_overview = strategic_service.get_strategic_overview()
        
        # Key metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Customers",
                customer_analytics.get('total_customers', 0),
                delta=None
            )
        
        with col2:
            st.metric(
                "Total Suppliers",
                supplier_analytics.get('total_farmers', 0),
                delta=None
            )
        
        with col3:
            st.metric(
                "Monthly Revenue",
                f"${financial_summary.get('total_revenue', 0):,.2f}",
                delta=None
            )
        
        with col4:
            st.metric(
                "Active Goals",
                strategic_overview.get('goals', {}).get('in_progress', 0),
                delta=None
            )
        
        # Charts and detailed analytics
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Financial Overview")
            
            profit_margin = financial_summary.get('profit_margin_percentage', 0)
            if profit_margin > 20:
                st.success(f"Excellent profit margin: {profit_margin:.1f}%")
            elif profit_margin > 10:
                st.info(f"Good profit margin: {profit_margin:.1f}%")
            else:
                st.warning(f"Profit margin needs improvement: {profit_margin:.1f}%")
            
            st.write(f"**Total Revenue:** ${financial_summary.get('total_revenue', 0):,.2f}")
            st.write(f"**Total Expenses:** ${financial_summary.get('total_expenses', 0):,.2f}")
            st.write(f"**Net Profit:** ${financial_summary.get('net_profit', 0):,.2f}")
        
        with col2:
            st.subheader("🎯 Goal Progress")
            
            goals_data = strategic_overview.get('goals', {})
            total_goals = goals_data.get('total', 0)
            achieved_goals = goals_data.get('achieved', 0)
            
            if total_goals > 0:
                achievement_rate = (achieved_goals / total_goals) * 100
                st.progress(achievement_rate / 100)
                st.write(f"**Achievement Rate:** {achievement_rate:.1f}%")
                st.write(f"**Achieved Goals:** {achieved_goals}/{total_goals}")
            else:
                st.info("No goals set yet. Visit Strategic Planning to get started!")
        
        # Recent activity and alerts
        st.subheader("🔔 Recent Activity & Alerts")
        
        # Check for overdue invoices
        overdue_invoices = financial_service.get_overdue_invoices()
        if overdue_invoices:
            st.error(f"⚠️ {len(overdue_invoices)} overdue invoices require attention!")
        
        # Check customer satisfaction
        avg_satisfaction = customer_analytics.get('average_satisfaction_score', 0)
        if avg_satisfaction > 0:
            if avg_satisfaction >= 4:
                st.success(f"🌟 Excellent customer satisfaction: {avg_satisfaction:.1f}/5")
            elif avg_satisfaction >= 3:
                st.info(f"👍 Good customer satisfaction: {avg_satisfaction:.1f}/5")
            else:
                st.warning(f"📈 Customer satisfaction needs improvement: {avg_satisfaction:.1f}/5")
        
        # Quick actions
        st.subheader("⚡ Quick Actions")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("➕ Add New Customer"):
                st.session_state.page = "customers"
                st.rerun()
        
        with col2:
            if st.button("🚜 Add New Supplier"):
                st.session_state.page = "suppliers"
                st.rerun()
        
        with col3:
            if st.button("📋 Log Daily Operations"):
                st.session_state.page = "operations"
                st.rerun()
        
        with col4:
            if st.button("💰 Record Transaction"):
                st.session_state.page = "financial"
                st.rerun()
    
    except Exception as e:
        st.error(f"Error loading dashboard: {str(e)}")
        st.info("This might be because the database is empty. Try adding some data first!")

def show_customer_management():
    """Display customer management interface."""
    st.header("👥 Customer Management")
    
    # Initialize service
    customer_service = CustomerService()
    
    # Tabs for different customer operations
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Customer List", "➕ Add Customer", "📊 Analytics", "📝 Orders"])
    
    with tab1:
        st.subheader("Customer Directory")
        
        try:
            # Get selected business from session state
            selected_business = st.session_state.get('selected_business', 'island_harvest')
            customers = customer_service.get_all_customers(business_id=selected_business)
            
            if customers:
                for customer in customers:
                    with st.expander(f"🏨 {customer.name}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Contact Person:** {customer.contact_person or 'N/A'}")
                            st.write(f"**Phone:** {customer.phone or 'N/A'}")
                            st.write(f"**Email:** {customer.email or 'N/A'}")
                        
                        with col2:
                            st.write(f"**Address:** {customer.address or 'N/A'}")
                            if customer.satisfaction_score:
                                st.write(f"**Satisfaction:** {customer.satisfaction_score}/5 ⭐")
                            st.write(f"**Added:** {customer.created_at.strftime('%Y-%m-%d') if customer.created_at else 'N/A'}")
                        
                        # Action buttons
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            if st.button(f"📊 Analytics", key=f"analytics_{customer.id}"):
                                st.session_state.selected_customer_id = customer.id
                        with col2:
                            if st.button(f"📝 Add Order", key=f"order_{customer.id}"):
                                st.session_state.selected_customer_id = customer.id
                        with col3:
                            if st.button(f"⭐ Rate", key=f"rate_{customer.id}"):
                                st.session_state.selected_customer_id = customer.id
                        with col4:
                            if customer.phone:
                                if st.button(f"💬 WhatsApp", key=f"whatsapp_{customer.id}"):
                                    st.session_state.whatsapp_customer_id = customer.id
                                    st.session_state.whatsapp_customer_phone = customer.phone
                                    st.session_state.whatsapp_customer_name = customer.name
                                    st.rerun()
                        
                        # WhatsApp messaging section (if customer selected)
                        if st.session_state.get('whatsapp_customer_id') == customer.id:
                            st.markdown("---")
                            st.subheader(f"💬 Send WhatsApp Message to {customer.name}")
                            
                            from app.services.whatsapp_automation_service import WhatsAppAutomationService
                            whatsapp_service = WhatsAppAutomationService()
                            
                            # Quick message templates
                            message_type = st.selectbox(
                                "Message Type",
                                ["Custom Message", "Order Confirmation", "Delivery Notification", "Payment Reminder"],
                                key=f"msg_type_{customer.id}"
                            )
                            
                            if message_type == "Custom Message":
                                custom_message = st.text_area("Enter your message", key=f"custom_msg_{customer.id}")
                                if st.button("Send Message", key=f"send_custom_{customer.id}"):
                                    if custom_message:
                                        success, msg = whatsapp_service.send_custom_message(customer.phone, custom_message)
                                        if success:
                                            st.success(f"✅ {msg}")
                                        else:
                                            st.error(f"❌ {msg}")
                                    else:
                                        st.warning("Please enter a message")
                            
                            elif message_type == "Order Confirmation":
                                # Get customer orders
                                orders = customer_service.get_customer_orders(customer.id)
                                if orders:
                                    order_select = st.selectbox(
                                        "Select Order",
                                        orders,
                                        format_func=lambda o: f"Order #{o.id} - ${o.total_amount:.2f}",
                                        key=f"order_select_{customer.id}"
                                    )
                                    if st.button("Send Order Confirmation", key=f"send_order_{customer.id}"):
                                        order_items = [
                                            {
                                                'product_name': item.product_name,
                                                'quantity': item.quantity,
                                                'unit_price': item.unit_price
                                            }
                                            for item in order_select.order_items
                                        ]
                                        delivery_date_str = order_select.delivery_date.strftime('%B %d, %Y')
                                        success, msg = whatsapp_service.send_order_confirmation(
                                            customer_name=customer.name or customer.contact_person or "Customer",
                                            customer_phone=customer.phone,
                                            order_id=order_select.id,
                                            order_items=order_items,
                                            delivery_date=delivery_date_str,
                                            total_amount=order_select.total_amount,
                                            delivery_address=customer.address
                                        )
                                        if success:
                                            st.success(f"✅ {msg}")
                                        else:
                                            st.error(f"❌ {msg}")
                                else:
                                    st.info("No orders found for this customer")
                            
                            elif message_type == "Delivery Notification":
                                orders = customer_service.get_customer_orders(customer.id)
                                if orders:
                                    order_select = st.selectbox(
                                        "Select Order",
                                        orders,
                                        format_func=lambda o: f"Order #{o.id} - {o.delivery_date.strftime('%B %d, %Y')}",
                                        key=f"delivery_order_{customer.id}"
                                    )
                                    time_window = st.text_input("Time Window", value="9 AM - 12 PM", key=f"time_window_{customer.id}")
                                    if st.button("Send Delivery Notification", key=f"send_delivery_{customer.id}"):
                                        delivery_date_str = order_select.delivery_date.strftime('%B %d, %Y')
                                        success, msg = whatsapp_service.send_delivery_notification(
                                            customer_name=customer.name or customer.contact_person or "Customer",
                                            customer_phone=customer.phone,
                                            order_id=order_select.id,
                                            delivery_date=delivery_date_str,
                                            time_window=time_window
                                        )
                                        if success:
                                            st.success(f"✅ {msg}")
                                        else:
                                            st.error(f"❌ {msg}")
                                else:
                                    st.info("No orders found for this customer")
                            
                            elif message_type == "Payment Reminder":
                                from app.services.financial_service import FinancialService
                                financial_service = FinancialService()
                                invoices = financial_service.get_invoices_by_customer(customer.id)
                                if invoices:
                                    invoice_select = st.selectbox(
                                        "Select Invoice",
                                        invoices,
                                        format_func=lambda i: f"Invoice #{i.id} - ${i.total_amount:.2f} (Due: {i.due_date.strftime('%B %d, %Y')})",
                                        key=f"invoice_select_{customer.id}"
                                    )
                                    if st.button("Send Payment Reminder", key=f"send_payment_{customer.id}"):
                                        due_date_str = invoice_select.due_date.strftime('%B %d, %Y')
                                        success, msg = whatsapp_service.send_payment_reminder(
                                            customer_name=customer.name or customer.contact_person or "Customer",
                                            customer_phone=customer.phone,
                                            invoice_id=invoice_select.id,
                                            amount=invoice_select.total_amount,
                                            due_date=due_date_str
                                        )
                                        if success:
                                            st.success(f"✅ {msg}")
                                        else:
                                            st.error(f"❌ {msg}")
                                else:
                                    st.info("No invoices found for this customer")
                            
                            if st.button("Close", key=f"close_whatsapp_{customer.id}"):
                                st.session_state.whatsapp_customer_id = None
                                st.rerun()
            else:
                st.info("No customers found. Add your first customer using the 'Add Customer' tab!")
        
        except Exception as e:
            st.error(f"Error loading customers: {str(e)}")
    
    with tab2:
        st.subheader("Add New Customer")
        
        with st.form("add_customer_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Business Name *", placeholder="e.g., Sunset Resort")
                contact_person = st.text_input("Contact Person", placeholder="e.g., John Smith")
                phone = st.text_input("Phone Number", placeholder="e.g., +1-876-555-0123")
            
            with col2:
                email = st.text_input("Email Address", placeholder="e.g., manager@sunsetresort.com")
                address = st.text_area("Address", placeholder="e.g., Blue Mountain Road, Port Antonio")
            
            st.subheader("Preferences")
            col1, col2 = st.columns(2)
            
            with col1:
                delivery_days = st.multiselect(
                    "Preferred Delivery Days",
                    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                )
                delivery_time = st.selectbox(
                    "Preferred Delivery Time",
                    ["Early Morning (6-9 AM)", "Morning (9-12 PM)", "Afternoon (12-3 PM)", "Late Afternoon (3-6 PM)"]
                )
            
            with col2:
                product_types = st.multiselect(
                    "Product Interests",
                    ["Vegetables", "Fruits", "Herbs", "Root Vegetables", "Leafy Greens", "Exotic Fruits"]
                )
                special_requirements = st.text_area("Special Requirements", placeholder="e.g., Organic only, specific packaging")
            
            submitted = st.form_submit_button("Add Customer", type="primary")
            
            if submitted:
                if name:
                    try:
                        # Get selected business from session state
                        selected_business = st.session_state.get('selected_business', 'island_harvest')
                        
                        preferences = {
                            "delivery_days": delivery_days,
                            "delivery_time": delivery_time,
                            "product_types": product_types,
                            "special_requirements": special_requirements
                        }
                        
                        customer = customer_service.create_customer(
                            name=name,
                            business_id=selected_business,
                            contact_person=contact_person,
                            phone=phone,
                            email=email,
                            address=address,
                            preferences=preferences
                        )
                        
                        st.success(f"✅ Customer '{name}' added successfully!")
                        st.balloons()
                        st.rerun()  # Refresh to show new customer
                        
                    except ValueError as e:
                        # Handle duplicate name or validation errors
                        st.error(f"❌ {str(e)}")
                    except Exception as e:
                        st.error(f"Error adding customer: {str(e)}")
                        st.exception(e)  # Show full traceback for debugging
                else:
                    st.error("⚠️ Business name is required!")
    
    with tab3:
        st.subheader("Customer Analytics")
        
        try:
            # Get selected business from session state
            selected_business = st.session_state.get('selected_business', 'island_harvest')
            analytics = customer_service.get_all_customers_analytics(business_id=selected_business)
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Customers", analytics.get('total_customers', 0))
            with col2:
                st.metric("Total Orders", analytics.get('total_orders', 0))
            with col3:
                st.metric("Total Revenue", f"${analytics.get('total_revenue', 0):,.2f}")
            with col4:
                st.metric("Avg Satisfaction", f"{analytics.get('average_satisfaction_score', 0):.1f}/5")
            
            # Top customers
            st.subheader("🏆 Top Customers by Revenue")
            top_customers = analytics.get('top_customers', [])
            
            if top_customers:
                for i, customer in enumerate(top_customers, 1):
                    st.write(f"{i}. **{customer['name']}** - ${customer['revenue']:,.2f}")
            else:
                st.info("No customer revenue data available yet.")
        
        except Exception as e:
            st.error(f"Error loading analytics: {str(e)}")
    
    with tab4:
        st.subheader("Order Management")
        st.info("Order management functionality will be expanded here. For now, use the customer list to add orders.")

def show_supplier_management():
    """Display supplier management interface."""
    st.header("🚜 Supplier Management")
    
    # Initialize service
    supplier_service = SupplierService()
    
    # Tabs for different supplier operations
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Supplier List", "➕ Add Supplier", "📊 Analytics", "💰 Payments"])
    
    with tab1:
        st.subheader("Supplier Directory")
        
        try:
            # Get selected business from session state
            selected_business = st.session_state.get('selected_business', 'island_harvest')
            farmers = supplier_service.get_all_farmers(business_id=selected_business)
            
            if farmers:
                for farmer in farmers:
                    with st.expander(f"🚜 {farmer.name}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Contact Person:** {farmer.contact_person or 'N/A'}")
                            st.write(f"**Phone:** {farmer.phone or 'N/A'}")
                            st.write(f"**Email:** {farmer.email or 'N/A'}")
                            
                            # Show specialties
                            specialties = supplier_service.get_farmer_specialties(farmer.id)
                            if specialties:
                                st.write(f"**Specialties:** {', '.join(specialties)}")
                        
                        with col2:
                            st.write(f"**Address:** {farmer.address or 'N/A'}")
                            st.write(f"**Added:** {farmer.created_at.strftime('%Y-%m-%d') if farmer.created_at else 'N/A'}")
                            
                            # Show recent quality records
                            quality_records = supplier_service.get_farmer_quality_records(farmer.id)
                            if quality_records:
                                latest_quality = quality_records[-1]
                                st.write(f"**Latest Quality:** {latest_quality.get('quality_score', 'N/A')}/5 ⭐")
                        
                        # Action buttons
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if st.button(f"📊 Analytics", key=f"farmer_analytics_{farmer.id}"):
                                st.session_state.selected_farmer_id = farmer.id
                        with col2:
                            if st.button(f"💰 Add Payment", key=f"farmer_payment_{farmer.id}"):
                                st.session_state.selected_farmer_id = farmer.id
                        with col3:
                            if st.button(f"⭐ Quality Check", key=f"farmer_quality_{farmer.id}"):
                                st.session_state.selected_farmer_id = farmer.id
            else:
                st.info("No suppliers found. Add your first supplier using the 'Add Supplier' tab!")
        
        except Exception as e:
            st.error(f"Error loading suppliers: {str(e)}")
    
    with tab2:
        st.subheader("Add New Supplier")
        
        with st.form("add_supplier_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Farm/Supplier Name *", placeholder="e.g., Green Valley Farm")
                contact_person = st.text_input("Contact Person", placeholder="e.g., John Brown")
                phone = st.text_input("Phone Number", placeholder="e.g., +1-876-555-0456")
            
            with col2:
                email = st.text_input("Email Address", placeholder="e.g., john@greenvalley.com")
                address = st.text_area("Farm Address", placeholder="e.g., Blue Mountain Valley, Portland")
            
            st.subheader("Farm Specialties")
            col1, col2 = st.columns(2)
            
            with col1:
                product_specialties = st.multiselect(
                    "Product Specialties",
                    ["Yam", "Sweet Potato", "Callaloo", "Scotch Bonnet Peppers", "Ackee", 
                     "Breadfruit", "Plantain", "Banana", "Mango", "Coconut", "Pineapple",
                     "Tomatoes", "Onions", "Carrots", "Cabbage", "Lettuce", "Herbs"]
                )
            
            with col2:
                pickup_days = st.multiselect(
                    "Available Pickup Days",
                    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                )
                pickup_time = st.selectbox(
                    "Preferred Pickup Time",
                    ["Early Morning (5-8 AM)", "Morning (8-11 AM)", "Afternoon (11-2 PM)", "Late Afternoon (2-5 PM)"]
                )
            
            notes = st.text_area("Additional Notes", placeholder="e.g., Organic certification, special handling requirements")
            
            submitted = st.form_submit_button("Add Supplier", type="primary")
            
            if submitted:
                if name:
                    try:
                        # Get selected business from session state
                        selected_business = st.session_state.get('selected_business', 'island_harvest')
                        
                        pickup_schedule = {
                            "days": pickup_days,
                            "time": pickup_time
                        }
                        
                        farmer = supplier_service.create_farmer(
                            name=name,
                            business_id=selected_business,
                            contact_person=contact_person,
                            phone=phone,
                            email=email,
                            address=address,
                            product_specialties=product_specialties,
                            pickup_schedule=pickup_schedule
                        )
                        
                        # Add initial notes if provided
                        if notes:
                            supplier_service.add_performance_note(farmer.id, f"Initial notes: {notes}")
                        
                        st.success(f"✅ Supplier '{name}' added successfully!")
                        st.balloons()
                        st.rerun()  # Refresh to show new supplier
                        
                    except ValueError as e:
                        # Handle duplicate name or validation errors
                        st.error(f"❌ {str(e)}")
                    except Exception as e:
                        st.error(f"Error adding supplier: {str(e)}")
                        st.exception(e)  # Show full traceback for debugging
                else:
                    st.error("⚠️ Farm/Supplier name is required!")
    
    with tab3:
        st.subheader("Supplier Analytics")
        
        try:
            # Get selected business from session state
            selected_business = st.session_state.get('selected_business', 'island_harvest')
            analytics = supplier_service.get_all_farmers_analytics(business_id=selected_business)
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Suppliers", analytics.get('total_farmers', 0))
            with col2:
                st.metric("Total Payments", f"${analytics.get('total_payments_amount', 0):,.2f}")
            with col3:
                st.metric("Payment Count", analytics.get('total_payment_count', 0))
            with col4:
                st.metric("Avg Quality Score", f"{analytics.get('average_quality_score', 0):.1f}/5")
            
            # Top suppliers
            st.subheader("🏆 Top Suppliers by Payments")
            top_suppliers = analytics.get('top_farmers_by_payments', [])
            
            if top_suppliers:
                for i, supplier in enumerate(top_suppliers, 1):
                    st.write(f"{i}. **{supplier['name']}** - ${supplier['total_payments']:,.2f}")
            else:
                st.info("No supplier payment data available yet.")
        
        except Exception as e:
            st.error(f"Error loading analytics: {str(e)}")
    
    with tab4:
        st.subheader("Payment Management")
        
        # Quick payment form
        with st.form("quick_payment_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                farmers = supplier_service.get_all_farmers()
                if farmers:
                    farmer_options = {f"{farmer.name}": farmer.id for farmer in farmers}
                    selected_farmer_name = st.selectbox("Select Supplier", list(farmer_options.keys()))
                    selected_farmer_id = farmer_options.get(selected_farmer_name)
                else:
                    st.warning("No suppliers available. Add suppliers first.")
                    selected_farmer_id = None
            
            with col2:
                payment_amount = st.number_input("Payment Amount ($)", min_value=0.01, step=0.01)
            
            payment_notes = st.text_area("Payment Notes", placeholder="e.g., Payment for yam delivery on 2024-01-15")
            
            payment_submitted = st.form_submit_button("Record Payment", type="primary")
            
            if payment_submitted and selected_farmer_id:
                try:
                    payment = supplier_service.create_payment(
                        farmer_id=selected_farmer_id,
                        amount=payment_amount,
                        notes=payment_notes
                    )
                    
                    st.success(f"✅ Payment of ${payment_amount:.2f} recorded for {selected_farmer_name}!")
                    
                except Exception as e:
                    st.error(f"Error recording payment: {str(e)}")
        
        # Recent payments
        st.subheader("Recent Payments")
        try:
            farmers = supplier_service.get_all_farmers()
            all_payments = []
            
            for farmer in farmers:
                payments = supplier_service.get_farmer_payments(farmer.id)
                for payment in payments:
                    all_payments.append({
                        'Farmer': farmer.name,
                        'Amount': f"${payment.amount:.2f}",
                        'Date': payment.payment_date.strftime('%Y-%m-%d'),
                        'Notes': payment.notes or 'N/A'
                    })
            
            if all_payments:
                # Sort by date (most recent first)
                all_payments.sort(key=lambda x: x['Date'], reverse=True)
                
                # Show last 10 payments
                recent_payments = all_payments[:10]
                
                for payment in recent_payments:
                    with st.container():
                        col1, col2, col3, col4 = st.columns([2, 1, 1, 3])
                        with col1:
                            st.write(f"**{payment['Farmer']}**")
                        with col2:
                            st.write(payment['Amount'])
                        with col3:
                            st.write(payment['Date'])
                        with col4:
                            st.write(payment['Notes'])
                        st.divider()
            else:
                st.info("No payments recorded yet.")
        
        except Exception as e:
            st.error(f"Error loading payments: {str(e)}")

def show_operations_management():
    """Display operations management interface."""
    st.header("📋 Daily Operations")
    st.info("Operations management interface - Coming in next update!")

def show_financial_management():
    """Display the financial management module."""
    st.header("💰 Financial Management")
    
    # Initialize financial service
    financial_service = FinancialService()
    
    # Create tabs for different financial sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Financial Overview",
        "💵 Transactions",
        "📝 Invoices",
        "📈 Cash Flow"
    ])
    
    with tab1:
        st.subheader("Financial Overview")
        
        # Get financial summaries
        profit_loss = financial_service.get_profit_loss_summary()
        revenue = financial_service.get_revenue_summary()
        expenses = financial_service.get_expense_summary()
        
        # Display key metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Total Revenue",
                f"${profit_loss.get('total_revenue', 0):,.2f}",
                delta=f"${profit_loss.get('revenue_change', 0):,.2f}"
            )
        
        with col2:
            st.metric(
                "Total Expenses",
                f"${profit_loss.get('total_expenses', 0):,.2f}",
                delta=f"${profit_loss.get('expense_change', 0):,.2f}"
            )
        
        with col3:
            st.metric(
                "Net Profit",
                f"${profit_loss.get('net_profit', 0):,.2f}",
                delta=f"${profit_loss.get('profit_change', 0):,.2f}"
            )
        
        # Display profit margin
        profit_margin = profit_loss.get('profit_margin_percentage', 0)
        st.progress(profit_margin / 100)
        st.write(f"Profit Margin: {profit_margin:.1f}%")
        
        # Display accounts receivable
        st.subheader("Accounts Receivable")
        accounts_receivable = financial_service.get_accounts_receivable()
        st.write(f"Total Outstanding: ${accounts_receivable.get('total_outstanding', 0):,.2f}")
        st.write(f"Overdue Amount: ${accounts_receivable.get('overdue_amount', 0):,.2f}")
    
    with tab2:
        st.subheader("Transaction Management")
        
        # Add new transaction
        with st.expander("Add New Transaction"):
            with st.form("new_transaction"):
                transaction_date = st.date_input("Date")
                transaction_type = st.selectbox(
                    "Type",
                    ["Revenue", "Expense", "Payment Received", "Other"]
                )
                description = st.text_input("Description")
                amount = st.number_input("Amount", min_value=0.0, step=0.01)
                category = st.text_input("Category (optional)")
                
                if st.form_submit_button("Add Transaction"):
                    try:
                        if transaction_type == "Expense":
                            financial_service.create_expense_transaction(
                                datetime.combine(transaction_date, datetime.min.time()),
                                description,
                                amount,
                                category
                            )
                        else:
                            financial_service.create_transaction(
                                datetime.combine(transaction_date, datetime.min.time()),
                                transaction_type,
                                description,
                                amount
                            )
                        st.success("Transaction added successfully!")
                    except Exception as e:
                        st.error(f"Error adding transaction: {str(e)}")
        
        # View transactions
        st.subheader("Recent Transactions")
        transactions = financial_service.get_all_transactions()
        
        for transaction in transactions[:10]:  # Show last 10 transactions
            with st.expander(f"{transaction.date.date()} - {transaction.type}: ${abs(transaction.amount):,.2f}"):
                st.write(f"Description: {transaction.description}")
                st.write(f"Amount: ${abs(transaction.amount):,.2f}")
                st.write(f"Type: {transaction.type}")
                if transaction.related_entity_type:
                    st.write(f"Related to: {transaction.related_entity_type} #{transaction.related_entity_id}")
    
    with tab3:
        st.subheader("Invoice Management")
        
        # Add new invoice
        with st.expander("Create New Invoice"):
            with st.form("new_invoice"):
                customer_id = st.number_input("Customer ID", min_value=1)
                order_id = st.number_input("Order ID", min_value=1)
                invoice_date = st.date_input("Invoice Date")
                due_date = st.date_input("Due Date")
                total_amount = st.number_input("Total Amount", min_value=0.0, step=0.01)
                
                if st.form_submit_button("Create Invoice"):
                    try:
                        financial_service.create_invoice(
                            customer_id,
                            order_id,
                            datetime.combine(invoice_date, datetime.min.time()),
                            datetime.combine(due_date, datetime.min.time()),
                            total_amount
                        )
                        st.success("Invoice created successfully!")
                    except Exception as e:
                        st.error(f"Error creating invoice: {str(e)}")
        
        # View invoices
        st.subheader("Recent Invoices")
        invoices = financial_service.get_all_invoices()
        
        for invoice in invoices[:10]:  # Show last 10 invoices
            with st.expander(f"Invoice #{invoice.id} - ${invoice.total_amount:,.2f}"):
                st.write(f"Customer ID: {invoice.customer_id}")
                st.write(f"Order ID: {invoice.order_id}")
                st.write(f"Invoice Date: {invoice.invoice_date.date()}")
                st.write(f"Due Date: {invoice.due_date.date()}")
                st.write(f"Status: {invoice.status}")
                
                # Update invoice status
                new_status = st.selectbox(
                    f"Update Status for Invoice #{invoice.id}",
                    ["Issued", "Paid", "Overdue", "Cancelled"],
                    index=["Issued", "Paid", "Overdue", "Cancelled"].index(invoice.status)
                )
                
                if new_status != invoice.status:
                    if st.button(f"Update Status for Invoice #{invoice.id}"):
                        try:
                            financial_service.update_invoice_status(invoice.id, new_status)
                            st.success("Invoice status updated successfully!")
                        except Exception as e:
                            st.error(f"Error updating invoice status: {str(e)}")
                
                # WhatsApp payment reminder button
                st.markdown("---")
                customer = financial_service.db.query(Customer).filter(Customer.id == invoice.customer_id).first()
                if customer and customer.phone:
                    from app.services.whatsapp_automation_service import WhatsAppAutomationService
                    whatsapp_service = WhatsAppAutomationService()
                    
                    if st.button(f"💬 Send Payment Reminder via WhatsApp", key=f"whatsapp_invoice_{invoice.id}"):
                        due_date_str = invoice.due_date.strftime('%B %d, %Y')
                        success, msg = whatsapp_service.send_payment_reminder(
                            customer_name=customer.name or customer.contact_person or "Customer",
                            customer_phone=customer.phone,
                            invoice_id=invoice.id,
                            amount=invoice.total_amount,
                            due_date=due_date_str
                        )
                        if success:
                            st.success(f"✅ {msg}")
                        else:
                            st.error(f"❌ {msg}")
                else:
                    st.info("⚠️ Customer phone number not available for WhatsApp messaging")
    
    with tab4:
        st.subheader("Cash Flow Analysis")
        
        # Get cash flow data
        cash_flow = financial_service.get_cash_flow_analysis()
        
        # Display cash flow metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Opening Balance",
                f"${cash_flow.get('opening_balance', 0):,.2f}"
            )
        
        with col2:
            st.metric(
                "Net Cash Flow",
                f"${cash_flow.get('net_cash_flow', 0):,.2f}",
                delta=f"${cash_flow.get('cash_flow_change', 0):,.2f}"
            )
        
        with col3:
            st.metric(
                "Closing Balance",
                f"${cash_flow.get('closing_balance', 0):,.2f}"
            )
        
        # Display cash flow breakdown
        st.subheader("Cash Flow Breakdown")
        st.write("Cash Inflows:")
        for inflow in cash_flow.get('inflows', []):
            st.write(f"- {inflow['category']}: ${inflow['amount']:,.2f}")
        
        st.write("Cash Outflows:")
        for outflow in cash_flow.get('outflows', []):
            st.write(f"- {outflow['category']}: ${outflow['amount']:,.2f}")

def show_communication_hub():
    """Display communication hub interface."""
    st.header("📞 Communication Hub")
    
    # Import enhanced communication services
    from app.services.enhanced_communication_service import EnhancedCommunicationService
    from app.services.whatsapp_service import WhatsAppService
    from app.services.email_service import EmailService
    
    # Initialize services
    comm_service = EnhancedCommunicationService()
    whatsapp_service = WhatsAppService()
    email_service = EmailService()
    
    # Tabs for different communication features
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📱 WhatsApp", "📧 Email", "📋 Templates", "📅 Tasks", "📊 Analytics"])
    
    with tab1:
        st.subheader("WhatsApp Business")
        
        # Quick message section
        st.write("### Send Quick Message")
        with st.form("whatsapp_quick_message"):
            col1, col2 = st.columns(2)
            
            with col1:
                phone_number = st.text_input("Phone Number", placeholder="+1-876-555-0123")
                message_type = st.selectbox("Message Type", ["Quick Message", "Template Message"])
            
            with col2:
                if message_type == "Template Message":
                    templates = whatsapp_service.get_message_templates()
                    template_names = [t["name"] for t in templates]
                    selected_template = st.selectbox("Select Template", template_names)
                else:
                    selected_template = None
            
            if message_type == "Quick Message":
                message_content = st.text_area("Message", placeholder="Type your message here...")
            else:
                if selected_template:
                    template = next((t for t in templates if t["name"] == selected_template), None)
                    if template:
                        st.write(f"**Template:** {template.get('title', template['name'])}")
                        st.write(f"**Content:** {template.get('content', template.get('body', 'No content available.'))}")
                        
                        # Show parameter inputs
                        parameters = {}
                        if template.get("parameters"):
                            st.write("**Fill in parameters:**")
                            for param in template["parameters"]:
                                parameters[param] = st.text_input(f"{param.replace('_', ' ').title()}", key=f"param_{param}")
            
            send_whatsapp = st.form_submit_button("Send WhatsApp Message", type="primary")
            
            if send_whatsapp:
                if phone_number:
                    if whatsapp_service.validate_phone_number(phone_number):
                        formatted_phone = whatsapp_service.format_phone_number(phone_number)
                        
                        if message_type == "Quick Message" and message_content:
                            result = whatsapp_service.send_message(formatted_phone, message_content)
                            if result.get("success"):
                                st.success(f"✅ WhatsApp message sent successfully!")
                            else:
                                st.error("Failed to send message")
                        
                        elif message_type == "Template Message" and selected_template:
                            formatted_message = whatsapp_service.format_template_message(selected_template, parameters)
                            result = whatsapp_service.send_message(formatted_phone, formatted_message)
                            if result.get("success"):
                                st.success(f"✅ WhatsApp template message sent successfully!")
                                st.info(f"**Message sent:** {formatted_message}")
                            else:
                                st.error("Failed to send template message")
                        else:
                            st.error("Please provide message content or select a template")
                    else:
                        st.error("Invalid phone number format. Please use Jamaica format: +1-876-XXX-XXXX")
                else:
                    st.error("Phone number is required")
        
        # WhatsApp templates preview
        st.write("### Available WhatsApp Templates")
        templates = whatsapp_service.get_message_templates()
        
        for template in templates:
            with st.expander(f"📱 {template.get('title', template['name'])} ({template['category']})"):
                st.write(f"**Template Name:** {template['name']}")
                st.write(f"**Category:** {template['category']}")
                st.write(f"**Content:** {template['content']}")
                if template.get("parameters"):
                    st.write(f"**Parameters:** {', '.join(template['parameters'])}")
    
    with tab2:
        st.subheader("Email Communication")
        
        # Quick email section
        st.write("### Send Email")
        with st.form("email_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                to_emails = st.text_area("To (Email Addresses)", placeholder="customer@example.com, supplier@farm.com")
                subject = st.text_input("Subject", placeholder="Email subject")
            
            with col2:
                email_type = st.selectbox("Email Type", ["Custom Email", "Template Email"])
                if email_type == "Template Email":
                    email_templates = email_service.get_email_templates()
                    template_names = [t["name"] for t in email_templates]
                    selected_email_template = st.selectbox("Select Template", template_names)
                else:
                    selected_email_template = None
            
            if email_type == "Custom Email":
                email_body = st.text_area("Email Body", height=200, placeholder="Type your email content here...")
            else:
                if selected_email_template:
                    template = next((t for t in email_templates if t["name"] == selected_email_template), None)
                    if template:
                        st.write(f"**Template:** {template['name']}")
                        st.write(f"**Category:** {template['category']}")
                        
                        # Show parameter inputs
                        email_parameters = {}
                        if template.get("parameters"):
                            st.write("**Fill in parameters:**")
                            for param in template["parameters"]:
                                email_parameters[param] = st.text_input(f"{param.replace('_', ' ').title()}", key=f"email_param_{param}")
            
            send_email = st.form_submit_button("Send Email", type="primary")
            
            if send_email:
                if to_emails and subject:
                    email_list = [email.strip() for email in to_emails.split(",")]
                    valid_emails = [email for email in email_list if email_service.validate_email(email)]
                    
                    if valid_emails:
                        if email_type == "Custom Email" and email_body:
                            result = email_service.send_email(valid_emails, subject, email_body)
                            if result.get("success"):
                                st.success(f"✅ Email sent to {len(valid_emails)} recipients!")
                            else:
                                st.error("Failed to send email")
                        
                        elif email_type == "Template Email" and selected_email_template:
                            formatted_email = email_service.format_template_email(selected_email_template, email_parameters)
                            if not formatted_email.get("error"):
                                result = email_service.send_email(
                                    valid_emails, 
                                    formatted_email["subject"], 
                                    formatted_email["body"]
                                )
                                if result.get("success"):
                                    st.success(f"✅ Template email sent to {len(valid_emails)} recipients!")
                                else:
                                    st.error("Failed to send template email")
                            else:
                                st.error(formatted_email["error"])
                        else:
                            st.error("Please provide email content or select a template")
                    else:
                        st.error("No valid email addresses found")
                else:
                    st.error("Email addresses and subject are required")
        
        # Email templates preview
        st.write("### Available Email Templates")
        email_templates = email_service.get_email_templates()
        
        for template in email_templates:
            with st.expander(f"📧 {template.get('title', template['name'])} ({template['category']})"):
                st.write(f"**Subject:** {template['subject']}")
                st.write(f"**Category:** {template['category']}")
                with st.container():
                    st.text_area("Body Preview", value=template['body'][:500] + "...", height=150, disabled=True, key=f"preview_{template['name']}")
                if template.get("parameters"):
                    st.write(f"**Parameters:** {', '.join(template['parameters'])}")
    
    with tab3:
        st.subheader("Message Templates")
        
        # Template management
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write("### All Templates")
            all_templates = comm_service.get_message_templates()
            
            if all_templates:
                for template in all_templates:
                    with st.expander(f"{template['channel'].upper()}: {template.get('title', template['name'])}"):
                        st.write(f"**Channel:** {template['channel']}")
                        st.write(f"**Category:** {template['category']}")
                        st.write(f"**Content:** {template['content']}")
                        if template.get("parameters"):
                            st.write(f"**Parameters:** {', '.join(template['parameters'])}")
            else:
                st.info("No templates available")
        
        with col2:
            st.write("### Quick Actions")
            
            if st.button("📱 View WhatsApp Templates"):
                st.session_state.template_filter = "whatsapp"
            
            if st.button("📧 View Email Templates"):
                st.session_state.template_filter = "email"
            
            if st.button("🔄 Refresh Templates"):
                st.rerun()
    
    with tab4:
        st.subheader("Follow-up Tasks")
        
        # Task management
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write("### Pending Tasks")
            pending_tasks = comm_service.get_pending_tasks()
            
            if pending_tasks:
                for task in pending_tasks:
                    with st.container():
                        col1, col2, col3 = st.columns([3, 1, 1])
                        
                        with col1:
                            st.write(f"**{task['description']}**")
                            st.write(f"Type: {task['type']} | Due: {task['due_date'][:10]} | Priority: {task.get('priority', 'medium')}")
                        
                        with col2:
                            if st.button("✅ Complete", key=f"complete_{task['id']}"):
                                result = comm_service.mark_task_complete(task['id'])
                                if result.get("success"):
                                    st.success("Task completed!")
                                    st.rerun()
                        
                        with col3:
                            st.write(f"👤 {task['assigned_to']}")
                        
                        st.divider()
            else:
                st.info("No pending tasks")
        
        with col2:
            st.write("### Add New Task")
            
            with st.form("new_task_form"):
                task_description = st.text_area("Description", placeholder="Follow up with customer about...")
                task_type = st.selectbox("Type", ["customer_follow_up", "supplier_check", "quality_review", "payment_follow_up", "general"])
                due_date = st.date_input("Due Date")
                assigned_to = st.text_input("Assigned To", value="Brian Miller")
                
                create_task = st.form_submit_button("Create Task")
                
                if create_task and task_description:
                    task = comm_service.create_follow_up_task(
                        task_type=task_type,
                        description=task_description,
                        due_date=datetime.combine(due_date, datetime.min.time()),
                        assigned_to=assigned_to
                    )
                    st.success("✅ Task created successfully!")
                    st.rerun()
    
    with tab5:
        st.subheader("Communication Analytics")
        
        # Mock analytics data
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("WhatsApp Messages", "156", delta="12 this week")
        
        with col2:
            st.metric("Emails Sent", "89", delta="8 this week")
        
        with col3:
            st.metric("Pending Tasks", len(comm_service.get_pending_tasks()), delta="-3 completed")
        
        with col4:
            st.metric("Templates Used", "23", delta="2 new")
        
        # Communication activity
        st.write("### Recent Communication Activity")
        
        activity_data = [
            {"Date": "2024-01-15", "Type": "WhatsApp", "Recipient": "Blue Mountain Resort", "Template": "Order Confirmation", "Status": "Delivered"},
            {"Date": "2024-01-15", "Type": "Email", "Recipient": "Green Valley Farm", "Template": "Quality Report", "Status": "Opened"},
            {"Date": "2024-01-14", "Type": "WhatsApp", "Recipient": "Sunset Hotel", "Template": "Delivery Reminder", "Status": "Read"},
            {"Date": "2024-01-14", "Type": "Email", "Recipient": "Mountain View Farm", "Template": "Payment Confirmation", "Status": "Delivered"},
        ]
        
        for activity in activity_data:
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([2, 1, 2, 2, 1])
                
                with col1:
                    st.write(activity["Date"])
                with col2:
                    st.write(f"📱" if activity["Type"] == "WhatsApp" else "📧")
                with col3:
                    st.write(activity["Recipient"])
                with col4:
                    st.write(activity["Template"])
                with col5:
                    status_color = "🟢" if activity["Status"] in ["Delivered", "Read", "Opened"] else "🟡"
                    st.write(f"{status_color} {activity['Status']}")
                
                st.divider()

def show_document_center():
    """Display document center interface."""
    st.header("📄 Document Center")
    
    # Import document services
    from app.services.document_generation_service import DocumentGenerationService
    
    # Initialize service
    doc_service = DocumentGenerationService()
    
    # Tabs for different document operations
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Document Library", "📝 Generate Documents", "📊 Templates", "⚙️ Settings"])
    
    with tab1:
        st.subheader("Document Library")
        
        # List generated documents
        documents = doc_service.list_generated_documents()
        
        if documents:
            st.write(f"**Total Documents:** {len(documents)}")
            
            # Filter options
            col1, col2, col3 = st.columns(3)
            
            with col1:
                doc_type_filter = st.selectbox("Filter by Type", ["All", "Markdown", "PDF"])
            
            with col2:
                sort_by = st.selectbox("Sort by", ["Modified Date", "Created Date", "Name", "Size"])
            
            with col3:
                if st.button("🔄 Refresh"):
                    st.rerun()
            
            # Apply filters
            filtered_docs = documents
            if doc_type_filter != "All":
                filtered_docs = [doc for doc in documents if doc["type"] == doc_type_filter]
            
            # Display documents
            for doc in filtered_docs:
                with st.expander(f"📄 {doc['filename']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Type:** {doc['type']}")
                        st.write(f"**Size:** {doc['size']:,} bytes")
                        st.write(f"**Created:** {doc['created'].strftime('%Y-%m-%d %H:%M')}")
                        st.write(f"**Modified:** {doc['modified'].strftime('%Y-%m-%d %H:%M')}")
                    
                    with col2:
                        # Action buttons
                        if st.button(f"📥 Download", key=f"download_{doc['filename']}"):
                            # In a real implementation, this would trigger a download
                            st.info(f"Download would start for {doc['filename']}")
                        
                        if doc['type'] == "Markdown":
                            if st.button(f"📄 Convert to PDF", key=f"convert_{doc['filename']}"):
                                try:
                                    pdf_path = doc_service.convert_to_pdf(doc['filepath'])
                                    st.success(f"✅ Converted to PDF: {os.path.basename(pdf_path)}")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error converting to PDF: {str(e)}")
                        
                        if st.button(f"🗑️ Delete", key=f"delete_{doc['filename']}"):
                            try:
                                os.remove(doc['filepath'])
                                st.success(f"✅ Deleted {doc['filename']}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error deleting file: {str(e)}")
        else:
            st.info("No documents found. Generate your first document using the 'Generate Documents' tab!")
    
    with tab2:
        st.subheader("Generate Documents")
        
        # Document generation options
        templates = doc_service.get_document_templates()
        
        template_names = [t["title"] for t in templates]
        selected_template = st.selectbox("Select Document Type", template_names)
        
        if selected_template:
            template = next((t for t in templates if t["title"] == selected_template), None)
            
            if template:
                st.write(f"**Description:** {template['description']}")
                st.write(f"**Required Data:** {', '.join(template['required_data'])}")
                
                # Generate document based on template type
                if template["name"] == "invoice":
                    st.write("### Invoice Generation")
                    
                    with st.form("invoice_form"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**Customer Information**")
                            customer_name = st.text_input("Customer Name", value="Blue Mountain Resort")
                            customer_address = st.text_area("Customer Address", value="Blue Mountain Road, Port Antonio")
                            contact_person = st.text_input("Contact Person", value="John Smith")
                            customer_phone = st.text_input("Customer Phone", value="+1-876-555-0123")
                            customer_email = st.text_input("Customer Email", value="john@bluemountain.com")
                        
                        with col2:
                            st.write("**Order Information**")
                            # Generate invoice ID with current date
                            current_date_str = datetime.now().strftime('%Y%m%d')
                            invoice_id = st.text_input("Invoice ID", value=f"INV-{current_date_str}-001")
                            delivery_date = st.date_input("Delivery Date")
                            delivery_time = st.text_input("Delivery Time", value="9:00 AM - 11:00 AM")
                            payment_terms = st.text_input("Payment Terms", value="Net 30 days")
                        
                        st.write("**Order Items**")
                        
                        # Simple item entry (in production, this would be more sophisticated)
                        item1_name = st.text_input("Item 1 Name", value="Fresh Yam")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            item1_qty = st.number_input("Quantity", value=50, min_value=0, key="item1_qty")
                        with col2:
                            item1_unit = st.text_input("Unit", value="lbs", key="item1_unit")
                        with col3:
                            item1_price = st.number_input("Unit Price ($)", value=2.50, min_value=0.0, step=0.01, key="item1_price")
                        
                        delivery_fee = st.number_input("Delivery Fee ($)", value=15.00, min_value=0.0, step=0.01)
                        tax = st.number_input("Tax ($)", value=0.00, min_value=0.0, step=0.01)
                        notes = st.text_area("Notes", value="Thank you for supporting local farmers!")
                        
                        generate_invoice = st.form_submit_button("Generate Invoice", type="primary")
                        
                        if generate_invoice:
                            # Prepare data
                            customer_data = {
                                "name": customer_name,
                                "address": customer_address,
                                "contact_person": contact_person,
                                "phone": customer_phone,
                                "email": customer_email
                            }
                            
                            order_data = {
                                "delivery_date": delivery_date.strftime('%B %d, %Y'),
                                "delivery_time": delivery_time,
                                "payment_terms": payment_terms,
                                "items": [
                                    {
                                        "name": item1_name,
                                        "quantity": item1_qty,
                                        "unit": item1_unit,
                                        "unit_price": item1_price
                                    }
                                ],
                                "delivery_fee": delivery_fee,
                                "tax": tax,
                                "notes": notes
                            }
                            
                            try:
                                invoice_path = doc_service.generate_invoice(customer_data, order_data, invoice_id)
                                st.success(f"✅ Invoice generated successfully!")
                                st.info(f"**File:** {os.path.basename(invoice_path)}")
                                
                                # Option to convert to PDF
                                if st.button("📄 Convert to PDF"):
                                    pdf_path = doc_service.convert_to_pdf(invoice_path)
                                    st.success(f"✅ PDF generated: {os.path.basename(pdf_path)}")
                                
                            except Exception as e:
                                st.error(f"Error generating invoice: {str(e)}")
                
                elif template["name"] == "business_summary":
                    st.write("### Business Summary Report")
                    
                    with st.form("business_summary_form"):
                        st.write("**Report Parameters**")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            report_period = st.text_input("Report Period", value="January 2024")
                            total_customers = st.number_input("Total Customers", value=25, min_value=0)
                            total_suppliers = st.number_input("Total Suppliers", value=15, min_value=0)
                            total_revenue = st.number_input("Total Revenue ($)", value=45000.0, min_value=0.0)
                        
                        with col2:
                            total_expenses = st.number_input("Total Expenses ($)", value=32000.0, min_value=0.0)
                            total_orders = st.number_input("Total Orders", value=180, min_value=0)
                            fulfillment_rate = st.number_input("Fulfillment Rate (%)", value=95.5, min_value=0.0, max_value=100.0)
                            avg_quality_score = st.number_input("Avg Quality Score", value=4.2, min_value=0.0, max_value=5.0)
                        
                        challenges = st.text_area("Current Challenges", value="- Seasonal produce availability\n- Weather-dependent deliveries")
                        opportunities = st.text_area("Growth Opportunities", value="- Expand to new parishes\n- Add organic certification")
                        
                        generate_summary = st.form_submit_button("Generate Business Summary", type="primary")
                        
                        if generate_summary:
                            # Calculate derived metrics
                            net_profit = total_revenue - total_expenses
                            profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
                            
                            business_data = {
                                "period": report_period,
                                "total_customers": total_customers,
                                "total_suppliers": total_suppliers,
                                "total_revenue": total_revenue,
                                "total_expenses": total_expenses,
                                "net_profit": net_profit,
                                "profit_margin": profit_margin,
                                "total_orders": total_orders,
                                "fulfillment_rate": fulfillment_rate,
                                "avg_quality_score": avg_quality_score,
                                "challenges": challenges,
                                "opportunities": opportunities
                            }
                            
                            try:
                                report_path = doc_service.generate_business_summary(business_data)
                                st.success(f"✅ Business summary generated successfully!")
                                st.info(f"**File:** {os.path.basename(report_path)}")
                                
                                # Option to convert to PDF
                                if st.button("📄 Convert to PDF"):
                                    pdf_path = doc_service.convert_to_pdf(report_path)
                                    st.success(f"✅ PDF generated: {os.path.basename(pdf_path)}")
                                
                            except Exception as e:
                                st.error(f"Error generating report: {str(e)}")
                
                else:
                    st.info(f"Document generation for '{template['name']}' will be implemented based on available data.")
    
    with tab3:
        st.subheader("Document Templates")
        
        # Display available templates
        templates = doc_service.get_document_templates()
        
        for template in templates:
            with st.expander(f"📄 {template.get('title', template['name'])}"):
                st.write(f"**Name:** {template['name']}")
                st.write(f"**Description:** {template.get('description', 'No description available')}")
                st.write(f"**Required Data:** {', '.join(template.get('required_data', []))}")
                
                # Template actions
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button(f"📝 Use Template", key=f"use_{template['name']}"):
                        st.session_state.selected_template = template['name']
                        st.info(f"Switch to 'Generate Documents' tab to use {template.get('title', template['name'])}")
                
                with col2:
                    if st.button(f"📋 Preview", key=f"preview_{template['name']}"):
                        st.info("Template preview would show sample output here")
                
                with col3:
                    if st.button(f"📥 Export Template", key=f"export_{template['name']}"):
                        st.info("Template export functionality")
    
    with tab4:
        st.subheader("Document Settings")
        
        # Document settings and preferences
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### Output Settings")
            
            output_format = st.selectbox("Default Output Format", ["Markdown", "PDF", "Both"])
            auto_convert_pdf = st.checkbox("Auto-convert to PDF", value=True)
            include_timestamp = st.checkbox("Include timestamp in filenames", value=True)
            
            st.write("### File Organization")
            
            organize_by_type = st.checkbox("Organize files by type", value=True)
            organize_by_date = st.checkbox("Organize files by date", value=False)
            auto_cleanup = st.checkbox("Auto-cleanup old files (30+ days)", value=False)
        
        with col2:
            st.write("### Business Information")
            
            business_name = st.text_input("Business Name", value="Island Harvest Hub")
            business_address = st.text_area("Business Address", value="Port Antonio, Portland Parish, Jamaica")
            business_phone = st.text_input("Business Phone", value="+1-876-555-FARM")
            business_email = st.text_input("Business Email", value="info@islandharvesthub.com")
            
            st.write("### Document Branding")
            
            include_logo = st.checkbox("Include logo in documents", value=False)
            custom_footer = st.text_area("Custom Footer", value="Generated by Island Harvest Hub AI Assistant")
        
        # Save settings
        if st.button("💾 Save Settings", type="primary"):
            # In a real implementation, these would be saved to a config file
            st.success("✅ Settings saved successfully!")
        
        # Document statistics
        st.write("### Document Statistics")
        
        documents = doc_service.list_generated_documents()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Documents", len(documents))
        
        with col2:
            markdown_docs = len([d for d in documents if d["type"] == "Markdown"])
            st.metric("Markdown Files", markdown_docs)
        
        with col3:
            pdf_docs = len([d for d in documents if d["type"] == "PDF"])
            st.metric("PDF Files", pdf_docs)
        
        with col4:
            total_size = sum(d["size"] for d in documents)
            st.metric("Total Size", f"{total_size:,} bytes")

def show_strategic_planning():
    """Display the strategic planning module."""
    st.header("🎯 Strategic Planning")
    
    # Initialize strategic service
    strategic_service = StrategicPlanningService()
    
    # Create tabs for different strategic sections
    tab1, tab2, tab3 = st.tabs([
        "🎯 Goals & Objectives",
        "📊 Performance Metrics",
        "🤝 Partnerships"
    ])
    
    with tab1:
        st.subheader("Business Goals")
        
        # Add new goal
        with st.expander("Add New Goal"):
            with st.form("new_goal"):
                goal_name = st.text_input("Goal Name")
                goal_description = st.text_area("Description")
                target_value = st.number_input("Target Value", min_value=0.0, step=0.01)
                start_date = st.date_input("Start Date")
                end_date = st.date_input("End Date")
                
                if st.form_submit_button("Add Goal"):
                    try:
                        strategic_service.create_goal(
                            goal_name,
                            goal_description,
                            target_value,
                            start_date,
                            end_date
                        )
                        st.success("Goal added successfully!")
                    except Exception as e:
                        st.error(f"Error adding goal: {str(e)}")
        
        # View goals
        st.subheader("Current Goals")
        goals = strategic_service.get_all_goals()
        
        for goal in goals:
            with st.expander(f"{goal.name} - {goal.status}"):
                st.write(f"Description: {goal.description}")
                st.write(f"Target Value: {goal.target_value}")
                st.write(f"Current Value: {goal.current_value}")
                st.write(f"Start Date: {goal.start_date.date()}")
                st.write(f"End Date: {goal.end_date.date()}")
                
                # Update goal progress
                new_value = st.number_input(
                    f"Update Progress for {goal.name}",
                    min_value=0.0,
                    value=goal.current_value,
                    step=0.01
                )
                
                if new_value != goal.current_value:
                    if st.button(f"Update Progress for {goal.name}"):
                        try:
                            strategic_service.update_goal_progress(goal.id, new_value)
                            st.success("Goal progress updated successfully!")
                        except Exception as e:
                            st.error(f"Error updating goal progress: {str(e)}")
                
                # Display progress bar
                progress = strategic_service.get_goal_progress_percentage(goal.id)
                st.progress(progress / 100)
                st.write(f"Progress: {progress:.1f}%")
    
    with tab2:
        st.subheader("Performance Metrics")
        
        # Add new metric
        with st.expander("Record New Metric"):
            with st.form("new_metric"):
                metric_name = st.text_input("Metric Name")
                metric_value = st.number_input("Value", min_value=0.0, step=0.01)
                metric_date = st.date_input("Date")
                metric_notes = st.text_area("Notes")
                
                if st.form_submit_button("Record Metric"):
                    try:
                        strategic_service.record_performance_metric(
                            metric_name,
                            metric_value,
                            metric_date,
                            metric_notes
                        )
                        st.success("Metric recorded successfully!")
                    except Exception as e:
                        st.error(f"Error recording metric: {str(e)}")
        
        # View metrics
        st.subheader("Recent Metrics")
        metrics = strategic_service.get_all_performance_metrics()
        
        # Group metrics by name
        metric_groups = {}
        for metric in metrics:
            if metric.name not in metric_groups:
                metric_groups[metric.name] = []
            metric_groups[metric.name].append(metric)
        
        # Display metrics by group
        for name, group_metrics in metric_groups.items():
            with st.expander(f"{name} Metrics"):
                for metric in group_metrics[:5]:  # Show last 5 metrics for each group
                    st.write(f"Date: {metric.date.date()}")
                    st.write(f"Value: {metric.value}")
                    if metric.notes:
                        st.write(f"Notes: {metric.notes}")
                    st.write("---")
        
        # Display business health score
        st.subheader("Business Health Score")
        health_score = strategic_service.calculate_business_health_score()
        
        # Display overall score
        st.metric(
            "Overall Health Score",
            f"{health_score.get('overall_score', 0):.1f}/100"
        )
        
        # Display component scores
        for component, score in health_score.get('component_scores', {}).items():
            st.write(f"{component}: {score:.1f}/100")
            st.progress(score / 100)
    
    with tab3:
        st.subheader("Partnership Management")
        
        # Add new partnership
        with st.expander("Add New Partnership"):
            with st.form("new_partnership"):
                partner_name = st.text_input("Partner Name")
                partnership_type = st.selectbox(
                    "Type",
                    ["Supplier", "Customer", "Service Provider", "Other"]
                )
                contact_person = st.text_input("Contact Person")
                status = st.selectbox(
                    "Status",
                    ["Prospect", "Active", "Inactive", "Terminated"]
                )
                notes = st.text_area("Notes")
                
                if st.form_submit_button("Add Partnership"):
                    try:
                        strategic_service.create_partnership(
                            partner_name,
                            partnership_type,
                            contact_person,
                            status,
                            notes
                        )
                        st.success("Partnership added successfully!")
                    except Exception as e:
                        st.error(f"Error adding partnership: {str(e)}")
        
        # View partnerships
        st.subheader("Current Partnerships")
        partnerships = strategic_service.get_all_partnerships()
        
        for partnership in partnerships:
            with st.expander(f"{partnership.name} - {partnership.status}"):
                st.write(f"Type: {partnership.type}")
                st.write(f"Contact Person: {partnership.contact_person}")
                st.write(f"Notes: {partnership.notes}")
                
                # Update partnership status
                new_status = st.selectbox(
                    f"Update Status for {partnership.name}",
                    ["Prospect", "Active", "Inactive", "Terminated"],
                    index=["Prospect", "Active", "Inactive", "Terminated"].index(partnership.status)
                )
                
                if new_status != partnership.status:
                    if st.button(f"Update Status for {partnership.name}"):
                        try:
                            strategic_service.update_partnership_status(
                                partnership.id,
                                new_status,
                                f"Status updated to {new_status}"
                            )
                            st.success("Partnership status updated successfully!")
                        except Exception as e:
                            st.error(f"Error updating partnership status: {str(e)}")

if __name__ == "__main__":
    main()

