"""
Unified Financial Service

Provides cross-business financial analysis and reporting

"""

from datetime import datetime, timedelta
from typing import Dict, List, Any
from app.services.financial_service import FinancialService
from app.config.business_profiles import get_all_active_businesses, get_business_profile


class UnifiedFinancialService:
    """Service for unified financial analysis across all businesses"""
    
    def __init__(self):
        # Use existing FinancialService that already works with your data
        self.financial_service = FinancialService()
    
    def get_total_revenue_all_businesses(self) -> float:
        """Get total revenue across all businesses"""
        # Use the existing financial service method
        transactions = self.financial_service.get_all_transactions()
        
        # Sum up revenue transactions (using correct field name and values)
        total = sum(t.amount for t in transactions if t.type in ["Revenue", "Payment Received"])
        return total
    
    def get_total_expenses_all_businesses(self) -> float:
        """Get total expenses across all businesses"""
        transactions = self.financial_service.get_all_transactions()
        
        # Sum up expense transactions (using correct field name and values)
        total = sum(abs(t.amount) for t in transactions if t.type in ["Expense", "Farmer Payment"])
        return total
    
    def get_revenue_by_business(self) -> Dict[str, float]:
        """Get revenue breakdown by business"""
        businesses = get_all_active_businesses()
        revenue_by_business = {}
        
        # Get total revenue (currently all assigned to Island Harvest)
        total_revenue = self.get_total_revenue_all_businesses()
        
        # Assign all current revenue to Island Harvest Hub
        # (In future, filter by business_id when that field is added)
        revenue_by_business['island_harvest'] = total_revenue
        
        # Initialize other businesses with 0
        for business_id in businesses.keys():
            if business_id not in revenue_by_business:
                revenue_by_business[business_id] = 0.0
        
        return revenue_by_business
    
    def get_profit_by_business(self) -> Dict[str, float]:
        """Get profit breakdown by business"""
        revenue = self.get_revenue_by_business()
        total_expenses = self.get_total_expenses_all_businesses()
        
        profit_by_business = {}
        for business_id, rev in revenue.items():
            # Simple allocation - subtract proportional expenses
            # For now, Island Harvest gets all profit since it has all revenue
            if business_id == 'island_harvest':
                profit_by_business[business_id] = rev - total_expenses
            else:
                profit_by_business[business_id] = 0.0
        
        return profit_by_business
    
    def get_top_performing_business(self) -> tuple:
        """Get the top performing business by revenue"""
        revenue_by_business = self.get_revenue_by_business()
        
        if not revenue_by_business:
            return None, 0
        
        top_business = max(revenue_by_business.items(), key=lambda x: x[1])
        return top_business
    
    def get_financial_summary(self) -> Dict[str, Any]:
        """Get comprehensive financial summary"""
        total_revenue = self.get_total_revenue_all_businesses()
        total_expenses = self.get_total_expenses_all_businesses()
        net_profit = total_revenue - total_expenses
        
        profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        revenue_by_business = self.get_revenue_by_business()
        top_business_id, top_revenue = self.get_top_performing_business()
        
        return {
            "total_revenue": total_revenue,
            "total_expenses": total_expenses,
            "net_profit": net_profit,
            "profit_margin": profit_margin,
            "revenue_by_business": revenue_by_business,
            "top_performing_business": {
                "id": top_business_id,
                "name": get_business_profile(top_business_id)['name'] if top_business_id else None,
                "revenue": top_revenue
            }
        }
    
    def get_monthly_revenue_trend(self, months: int = 6) -> List[Dict[str, Any]]:
        """Get monthly revenue trend for the past N months"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months * 30)
        
        transactions = self.financial_service.get_all_transactions()
        
        # Filter revenue transactions within date range
        revenue_transactions = [
            t for t in transactions 
            if t.type in ["Revenue", "Payment Received"] and t.date >= start_date
        ]
        
        # Group by month
        monthly_data = {}
        for t in revenue_transactions:
            month_key = t.date.strftime("%Y-%m")
            if month_key not in monthly_data:
                monthly_data[month_key] = 0
            monthly_data[month_key] += t.amount
        
        # Format for chart
        trend = []
        for month_key in sorted(monthly_data.keys()):
            trend.append({
                "month": month_key,
                "revenue": monthly_data[month_key]
            })
        
        return trend
    
    def get_business_comparison_data(self) -> List[Dict[str, Any]]:
        """Get data for business comparison chart"""
        revenue_by_business = self.get_revenue_by_business()
        profit_by_business = self.get_profit_by_business()
        
        comparison_data = []
        for business_id, revenue in revenue_by_business.items():
            business = get_business_profile(business_id)
            comparison_data.append({
                "business": business['name'],
                "revenue": revenue,
                "profit": profit_by_business.get(business_id, 0),
                "profit_margin": (profit_by_business.get(business_id, 0) / revenue * 100) if revenue > 0 else 0
            })
        
        return comparison_data
    
    def calculate_revenue_goal_progress(self, monthly_goal: float) -> Dict[str, Any]:
        """Calculate progress toward monthly revenue goal"""
        current_revenue = self.get_total_revenue_all_businesses()
        progress_percent = (current_revenue / monthly_goal * 100) if monthly_goal > 0 else 0
        remaining = max(0, monthly_goal - current_revenue)
        
        return {
            "current": current_revenue,
            "goal": monthly_goal,
            "progress_percent": progress_percent,
            "remaining": remaining,
            "status": "on_track" if progress_percent >= 75 else "needs_attention"
        }
