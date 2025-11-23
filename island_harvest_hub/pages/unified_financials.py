"""
Unified Financial Dashboard

Shows financial overview across all Bornfidis businesses

"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from app.services.unified_financial_service import UnifiedFinancialService
from app.config.business_profiles import get_all_active_businesses, get_business_profile


def show_unified_financials():
    """Display unified financial dashboard"""
    
    st.markdown("# 💰 Unified Financial Dashboard")
    st.markdown("*Financial overview across all Bornfidis businesses*")
    st.markdown("---")
    
    try:
        # Initialize service
        financial_service = UnifiedFinancialService()
        
        # Get financial summary
        summary = financial_service.get_financial_summary()
    except Exception as e:
        st.error(f"❌ Error initializing financial service: {str(e)}")
        st.exception(e)
        return
    
    # Key Metrics Row
    st.markdown("### 📊 Overall Performance")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Revenue",
            f"${summary['total_revenue']:,.2f}",
            delta="All Businesses"
        )
    
    with col2:
        st.metric(
            "Total Expenses",
            f"${summary['total_expenses']:,.2f}",
            delta=None
        )
    
    with col3:
        st.metric(
            "Net Profit",
            f"${summary['net_profit']:,.2f}",
            delta=f"{summary['profit_margin']:.1f}% margin"
        )
    
    with col4:
        top_business = summary['top_performing_business']
        st.metric(
            "Top Business",
            top_business['name'] if top_business['name'] else "N/A",
            delta=f"${top_business['revenue']:,.2f}"
        )
    
    st.markdown("---")
    
    # Revenue by Business
    st.markdown("### 🏢 Revenue by Business")
    
    revenue_data = financial_service.get_revenue_by_business()
    
    # Create bar chart
    businesses = []
    revenues = []
    colors = []
    
    for business_id, revenue in revenue_data.items():
        business = get_business_profile(business_id)
        businesses.append(business['name'])
        revenues.append(revenue)
        colors.append(business['primary_color'])
    
    fig = go.Figure(data=[
        go.Bar(
            x=businesses,
            y=revenues,
            marker_color=colors,
            text=[f"${r:,.0f}" for r in revenues],
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title="Revenue Comparison",
        xaxis_title="Business",
        yaxis_title="Revenue ($)",
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Business Comparison Table
    st.markdown("### 📈 Detailed Business Comparison")
    
    try:
        comparison_data = financial_service.get_business_comparison_data()
        
        if comparison_data:
            import pandas as pd
            df = pd.DataFrame(comparison_data)
            df['revenue'] = df['revenue'].apply(lambda x: f"${x:,.2f}")
            df['profit'] = df['profit'].apply(lambda x: f"${x:,.2f}")
            df['profit_margin'] = df['profit_margin'].apply(lambda x: f"{x:.1f}%")
            
            df.columns = ['Business', 'Revenue', 'Profit', 'Profit Margin']
            st.dataframe(df, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Error loading comparison data: {str(e)}")
    
    st.markdown("---")
    
    # Revenue Distribution (Pie Chart)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🥧 Revenue Distribution")
        
        # Filter out zero revenue businesses for cleaner pie chart
        non_zero_revenue = {k: v for k, v in revenue_data.items() if v > 0}
        
        if non_zero_revenue:
            labels = [get_business_profile(bid)['name'] for bid in non_zero_revenue.keys()]
            values = list(non_zero_revenue.values())
            colors_pie = [get_business_profile(bid)['primary_color'] for bid in non_zero_revenue.keys()]
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                marker=dict(colors=colors_pie),
                hole=0.3
            )])
            
            fig_pie.update_layout(height=400)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No revenue data to display")
    
    with col2:
        st.markdown("### 🎯 Monthly Revenue Goal")
        
        # Set monthly goal (can be made dynamic later)
        monthly_goal = 17000  # Based on your projections
        
        goal_progress = financial_service.calculate_revenue_goal_progress(monthly_goal)
        
        # Progress bar
        st.metric(
            "Current Progress",
            f"${goal_progress['current']:,.2f}",
            delta=f"{goal_progress['progress_percent']:.1f}% of goal"
        )
        
        progress_bar_value = min(goal_progress['progress_percent'] / 100, 1.0)
        st.progress(progress_bar_value)
        
        st.write(f"**Goal:** ${goal_progress['goal']:,.2f}")
        st.write(f"**Remaining:** ${goal_progress['remaining']:,.2f}")
        
        if goal_progress['status'] == 'on_track':
            st.success("✅ On track to meet goal!")
        else:
            st.warning("⚠️ Needs attention to reach goal")
    
    st.markdown("---")
    
    # Monthly Trend
    st.markdown("### 📅 Monthly Revenue Trend")
    
    trend_data = financial_service.get_monthly_revenue_trend(months=6)
    
    if trend_data:
        months = [d['month'] for d in trend_data]
        revenues = [d['revenue'] for d in trend_data]
        
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=months,
            y=revenues,
            mode='lines+markers',
            name='Revenue',
            line=dict(color='#0B3D23', width=3),
            marker=dict(size=10)
        ))
        
        fig_trend.update_layout(
            title="6-Month Revenue Trend",
            xaxis_title="Month",
            yaxis_title="Revenue ($)",
            height=400
        )
        
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("Not enough historical data to show trend")
    
    # Quick Actions
    st.markdown("---")
    st.markdown("### ⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 View Detailed Reports", use_container_width=True):
            st.info("Navigate to Financial Management for detailed reports")
    
    with col2:
        if st.button("🎯 Set Revenue Goals", use_container_width=True):
            st.info("Navigate to Strategic Planning to set goals")
    
    with col3:
        if st.button("💼 Compare Businesses", use_container_width=True):
            st.info("See comparison table above")


if __name__ == "__main__":
    show_unified_financials()

