"""
AI Business Advisor Page

Provides AI-powered business insights and recommendations

"""

import streamlit as st
import os
import sys
from datetime import datetime
from app.services.ai_advisor_service import AIAdvisorService
from app.services.customer_service import CustomerService
from app.services.financial_service import FinancialService
from app.services.operations_service import OperationsService
from app.config.business_profiles import get_business_profile

# Load environment variables from .env file if not already set
if not os.environ.get('ANTHROPIC_API_KEY'):
    # Try multiple possible locations for .env file
    possible_paths = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'),  # From pages/ to root
        os.path.join(os.getcwd(), '.env'),  # Current working directory
        os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'),  # From pages/ to island_harvest_hub/
    ]
    
    for env_path in possible_paths:
        if os.path.exists(env_path):
            try:
                with open(env_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            if key.strip() == 'ANTHROPIC_API_KEY':
                                os.environ[key.strip()] = value.strip()
                                break
            except Exception:
                continue
            break


def get_business_context_data(business_id: str) -> dict:
    """Gather business context data for AI analysis"""
    
    customer_service = CustomerService()
    financial_service = FinancialService()
    operations_service = OperationsService()
    
    # Get key metrics
    customers = customer_service.get_all_customers()
    transactions = financial_service.get_all_transactions()
    daily_logs = operations_service.get_all_daily_logs()
    
    # Calculate summaries
    # Revenue transactions: "Revenue" or "Payment Received"
    # Expense transactions: "Expense" or "Farmer Payment" (stored as negative amounts)
    total_revenue = sum(t.amount for t in transactions if t.type in ["Revenue", "Payment Received"])
    total_expenses = sum(abs(t.amount) for t in transactions if t.type in ["Expense", "Farmer Payment"])
    customer_count = len(customers)
    avg_satisfaction = sum(c.satisfaction_score or 0 for c in customers) / max(customer_count, 1)
    
    return {
        "business_id": business_id,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "customers": {
            "total": customer_count,
            "avg_satisfaction": round(avg_satisfaction, 2),
            "list": [{"name": c.name, "satisfaction": c.satisfaction_score} for c in customers[:5]]
        },
        "financials": {
            "total_revenue": total_revenue,
            "total_expenses": total_expenses,
            "net_profit": total_revenue - total_expenses,
            "profit_margin": round((total_revenue - total_expenses) / max(total_revenue, 1) * 100, 2)
        },
        "operations": {
            "daily_logs_count": len(daily_logs),
            "recent_activities": [{"date": str(log.log_date), "activities": log.activities} for log in daily_logs[:3]]
        }
    }


def show_ai_advisor():
    """Display AI Business Advisor interface"""
    
    st.markdown("# 🤖 AI Business Advisor")
    st.markdown("*Get intelligent insights powered by Claude AI*")
    st.markdown("---")
    
    # Get current business context
    current_business_id = st.session_state.get('selected_business', 'island_harvest')
    current_business = get_business_profile(current_business_id)
    
    st.info(f"**Current Business:** {current_business['display_name']}")
    
    # Initialize AI service
    ai_advisor = AIAdvisorService()
    
    # Check API key
    if not ai_advisor.api_key:
        st.error("⚠️ **AI Advisor Not Configured**")
        st.markdown("""
        To use the AI Business Advisor, you need to set up your Anthropic API key:
        
        1. Get your API key from: https://console.anthropic.com/
        2. Set environment variable: `ANTHROPIC_API_KEY=your-key-here`
        3. Restart the application
        
        **Need help?** Contact support or check the documentation.
        """)
        return
    
    # Get business data
    business_data = get_business_context_data(current_business_id)
    
    # Quick Actions
    st.markdown("### ⚡ Quick Insights")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 Daily Priorities", use_container_width=True):
            with st.spinner("Analyzing your business..."):
                priorities = ai_advisor.get_daily_priorities(business_data, current_business['name'])
                st.session_state.ai_response = priorities
    
    with col2:
        if st.button("💰 Revenue Prediction", use_container_width=True):
            with st.spinner("Forecasting revenue..."):
                prediction = ai_advisor.predict_revenue(business_data, current_business['name'])
                st.session_state.ai_response = prediction
    
    with col3:
        if st.button("👥 Customer Trends", use_container_width=True):
            with st.spinner("Analyzing customers..."):
                trends = ai_advisor.analyze_customer_trends(business_data['customers'])
                st.session_state.ai_response = trends
    
    st.markdown("---")
    
    # Custom Question
    st.markdown("### 💬 Ask Your AI Advisor")
    
    question = st.text_area(
        "What would you like to know about your business?",
        placeholder="Example: What should I focus on to increase customer satisfaction?",
        height=100
    )
    
    if st.button("🚀 Get Answer", type="primary", use_container_width=True):
        if question:
            with st.spinner("Thinking..."):
                answer = ai_advisor.get_business_insights(business_data, question)
                st.session_state.ai_response = answer
        else:
            st.warning("Please enter a question first.")
    
    # Display Response
    if 'ai_response' in st.session_state and st.session_state.ai_response:
        st.markdown("---")
        st.markdown("### 🎯 AI Insights")
        st.markdown(st.session_state.ai_response)
        
        # Clear button
        if st.button("Clear Response"):
            st.session_state.ai_response = ""
            st.rerun()
    
    # Business Context Display
    with st.expander("📊 Current Business Data (What AI Sees)"):
        st.json(business_data)


if __name__ == "__main__":
    show_ai_advisor()

