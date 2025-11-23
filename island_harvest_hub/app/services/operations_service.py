"""
Operations tracking service for Island Harvest Hub AI Assistant.
"""

import json
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models import DailyLog, Order
from app.database.config import SessionLocal

class OperationsService:
    """Service class for daily operations tracking."""
    
    def __init__(self):
        self.db: Session = SessionLocal()
    
    def __del__(self):
        """Close database session when service is destroyed."""
        if hasattr(self, 'db'):
            self.db.close()
    
    def create_daily_log(self, log_date: date, orders_fulfilled: int = 0,
                        quality_control_notes: str = None,
                        temperature_logs: List[Dict] = None,
                        delivery_route_notes: str = None,
                        issues: List[Dict] = None) -> DailyLog:
        """Create a new daily log entry."""
        try:
            # Convert date to datetime for storage
            log_datetime = datetime.combine(log_date, datetime.min.time())
            
            daily_log = DailyLog(
                log_date=log_datetime,
                orders_fulfilled=orders_fulfilled,
                quality_control_notes=quality_control_notes,
                temperature_logs=json.dumps(temperature_logs) if temperature_logs else None,
                delivery_route_notes=delivery_route_notes,
                issue_tracking=json.dumps(issues) if issues else None,
                created_at=datetime.now()
            )
            
            self.db.add(daily_log)
            self.db.commit()
            self.db.refresh(daily_log)
            return daily_log
        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_daily_log(self, log_date: date) -> Optional[DailyLog]:
        """Get daily log for a specific date."""
        log_datetime = datetime.combine(log_date, datetime.min.time())
        return self.db.query(DailyLog).filter(DailyLog.log_date == log_datetime).first()
    
    def get_daily_log_by_id(self, log_id: int) -> Optional[DailyLog]:
        """Get daily log by ID."""
        return self.db.query(DailyLog).filter(DailyLog.id == log_id).first()
    
    def get_all_daily_logs(self) -> List[DailyLog]:
        """Get all daily logs."""
        return self.db.query(DailyLog).order_by(DailyLog.log_date.desc()).all()
    
    def update_daily_log(self, log_date: date, **kwargs) -> Optional[DailyLog]:
        """Update daily log for a specific date."""
        try:
            daily_log = self.get_daily_log(log_date)
            if not daily_log:
                return None
            
            for key, value in kwargs.items():
                if hasattr(daily_log, key):
                    if key in ['temperature_logs', 'issue_tracking'] and isinstance(value, list):
                        setattr(daily_log, key, json.dumps(value))
                    else:
                        setattr(daily_log, key, value)
            
            daily_log.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(daily_log)
            return daily_log
        except Exception as e:
            self.db.rollback()
            raise e
    
    def add_temperature_log(self, log_date: date, temperature: float, 
                           location: str, time_recorded: datetime = None) -> Optional[DailyLog]:
        """Add a temperature reading to the daily log."""
        daily_log = self.get_daily_log(log_date)
        if not daily_log:
            # Create a new daily log if it doesn't exist
            daily_log = self.create_daily_log(log_date)
        
        temperature_logs = []
        if daily_log.temperature_logs:
            try:
                temperature_logs = json.loads(daily_log.temperature_logs)
            except json.JSONDecodeError:
                temperature_logs = []
        
        new_temp_log = {
            'temperature': temperature,
            'location': location,
            'time_recorded': (time_recorded or datetime.now()).isoformat()
        }
        temperature_logs.append(new_temp_log)
        
        return self.update_daily_log(log_date, temperature_logs=temperature_logs)
    
    def get_temperature_logs(self, log_date: date) -> List[Dict]:
        """Get temperature logs for a specific date."""
        daily_log = self.get_daily_log(log_date)
        if not daily_log or not daily_log.temperature_logs:
            return []
        
        try:
            return json.loads(daily_log.temperature_logs)
        except json.JSONDecodeError:
            return []
    
    def add_issue(self, log_date: date, issue_description: str, 
                 severity: str = "Medium", status: str = "Open",
                 resolution: str = None) -> Optional[DailyLog]:
        """Add an issue to the daily log."""
        daily_log = self.get_daily_log(log_date)
        if not daily_log:
            # Create a new daily log if it doesn't exist
            daily_log = self.create_daily_log(log_date)
        
        issues = []
        if daily_log.issue_tracking:
            try:
                issues = json.loads(daily_log.issue_tracking)
            except json.JSONDecodeError:
                issues = []
        
        new_issue = {
            'id': len(issues) + 1,
            'description': issue_description,
            'severity': severity,
            'status': status,
            'resolution': resolution,
            'reported_at': datetime.now().isoformat(),
            'resolved_at': None
        }
        issues.append(new_issue)
        
        return self.update_daily_log(log_date, issue_tracking=issues)
    
    def resolve_issue(self, log_date: date, issue_id: int, resolution: str) -> Optional[DailyLog]:
        """Resolve an issue in the daily log."""
        daily_log = self.get_daily_log(log_date)
        if not daily_log or not daily_log.issue_tracking:
            return None
        
        try:
            issues = json.loads(daily_log.issue_tracking)
        except json.JSONDecodeError:
            return None
        
        for issue in issues:
            if issue.get('id') == issue_id:
                issue['status'] = 'Resolved'
                issue['resolution'] = resolution
                issue['resolved_at'] = datetime.now().isoformat()
                break
        
        return self.update_daily_log(log_date, issue_tracking=issues)
    
    def get_issues(self, log_date: date) -> List[Dict]:
        """Get issues for a specific date."""
        daily_log = self.get_daily_log(log_date)
        if not daily_log or not daily_log.issue_tracking:
            return []
        
        try:
            return json.loads(daily_log.issue_tracking)
        except json.JSONDecodeError:
            return []
    
    def get_open_issues(self) -> List[Dict]:
        """Get all open issues across all daily logs."""
        daily_logs = self.get_all_daily_logs()
        open_issues = []
        
        for log in daily_logs:
            if log.issue_tracking:
                try:
                    issues = json.loads(log.issue_tracking)
                    for issue in issues:
                        if issue.get('status') == 'Open':
                            issue['log_date'] = log.log_date.date().isoformat()
                            open_issues.append(issue)
                except json.JSONDecodeError:
                    continue
        
        return open_issues
    
    def update_orders_fulfilled(self, log_date: date, orders_fulfilled: int) -> Optional[DailyLog]:
        """Update the number of orders fulfilled for a specific date."""
        daily_log = self.get_daily_log(log_date)
        if not daily_log:
            # Create a new daily log if it doesn't exist
            daily_log = self.create_daily_log(log_date, orders_fulfilled=orders_fulfilled)
            return daily_log
        
        return self.update_daily_log(log_date, orders_fulfilled=orders_fulfilled)
    
    def get_operations_analytics(self, start_date: date = None, end_date: date = None) -> Dict[str, Any]:
        """Get operations analytics for a date range."""
        query = self.db.query(DailyLog)
        
        if start_date:
            start_datetime = datetime.combine(start_date, datetime.min.time())
            query = query.filter(DailyLog.log_date >= start_datetime)
        
        if end_date:
            end_datetime = datetime.combine(end_date, datetime.max.time())
            query = query.filter(DailyLog.log_date <= end_datetime)
        
        daily_logs = query.all()
        
        if not daily_logs:
            return {
                'total_days_logged': 0,
                'total_orders_fulfilled': 0,
                'average_orders_per_day': 0,
                'total_issues': 0,
                'open_issues': 0,
                'resolved_issues': 0,
                'average_temperature': 0,
                'temperature_readings_count': 0
            }
        
        total_orders = sum(log.orders_fulfilled or 0 for log in daily_logs)
        total_days = len(daily_logs)
        avg_orders_per_day = total_orders / total_days if total_days > 0 else 0
        
        # Count issues
        total_issues = 0
        open_issues = 0
        resolved_issues = 0
        
        # Collect temperature data
        all_temperatures = []
        
        for log in daily_logs:
            if log.issue_tracking:
                try:
                    issues = json.loads(log.issue_tracking)
                    total_issues += len(issues)
                    for issue in issues:
                        if issue.get('status') == 'Open':
                            open_issues += 1
                        elif issue.get('status') == 'Resolved':
                            resolved_issues += 1
                except json.JSONDecodeError:
                    pass
            
            if log.temperature_logs:
                try:
                    temp_logs = json.loads(log.temperature_logs)
                    for temp_log in temp_logs:
                        if 'temperature' in temp_log:
                            all_temperatures.append(temp_log['temperature'])
                except json.JSONDecodeError:
                    pass
        
        avg_temperature = sum(all_temperatures) / len(all_temperatures) if all_temperatures else 0
        
        return {
            'total_days_logged': total_days,
            'total_orders_fulfilled': total_orders,
            'average_orders_per_day': avg_orders_per_day,
            'total_issues': total_issues,
            'open_issues': open_issues,
            'resolved_issues': resolved_issues,
            'average_temperature': avg_temperature,
            'temperature_readings_count': len(all_temperatures)
        }
    
    def get_delivery_route_optimization_suggestions(self, log_date: date) -> List[str]:
        """Get delivery route optimization suggestions based on historical data."""
        # This is a placeholder for more sophisticated route optimization
        # In a real implementation, this could integrate with mapping APIs
        
        daily_log = self.get_daily_log(log_date)
        suggestions = []
        
        # Basic suggestions based on orders fulfilled
        orders_fulfilled = daily_log.orders_fulfilled if daily_log else 0
        
        if orders_fulfilled > 20:
            suggestions.append("Consider splitting deliveries into morning and afternoon routes")
            suggestions.append("Group deliveries by geographic area to reduce travel time")
        elif orders_fulfilled > 10:
            suggestions.append("Plan route to minimize backtracking between delivery points")
        else:
            suggestions.append("Consider combining with pickup routes to maximize efficiency")
        
        # Add general suggestions
        suggestions.extend([
            "Use GPS tracking to monitor actual vs. planned routes",
            "Consider traffic patterns when planning delivery times",
            "Maintain buffer time for unexpected delays"
        ])
        
        return suggestions

