"""
Strategic planning service for Island Harvest Hub AI Assistant.
"""

from datetime import datetime, date
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models import Goal, PerformanceMetric, Partnership
from app.database.config import SessionLocal

class StrategicPlanningService:
    """Service class for strategic planning operations."""
    
    def __init__(self):
        self.db: Session = SessionLocal()
    
    def __del__(self):
        """Close database session when service is destroyed."""
        if hasattr(self, 'db'):
            self.db.close()
    
    # Goal Management
    def create_goal(self, name: str, description: str = None, 
                   target_value: float = None, start_date: date = None,
                   end_date: date = None, status: str = "In Progress") -> Goal:
        """Create a new business goal."""
        try:
            goal = Goal(
                name=name,
                description=description,
                target_value=target_value,
                current_value=0.0,
                start_date=datetime.combine(start_date, datetime.min.time()) if start_date else None,
                end_date=datetime.combine(end_date, datetime.min.time()) if end_date else None,
                status=status,
                created_at=datetime.now()
            )
            
            self.db.add(goal)
            self.db.commit()
            self.db.refresh(goal)
            return goal
        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_goal(self, goal_id: int) -> Optional[Goal]:
        """Get a goal by ID."""
        return self.db.query(Goal).filter(Goal.id == goal_id).first()
    
    def get_all_goals(self) -> List[Goal]:
        """Get all goals."""
        return self.db.query(Goal).order_by(Goal.created_at.desc()).all()
    
    def get_goals_by_status(self, status: str) -> List[Goal]:
        """Get goals by status."""
        return self.db.query(Goal).filter(Goal.status == status).all()
    
    def update_goal_progress(self, goal_id: int, current_value: float) -> Optional[Goal]:
        """Update goal progress."""
        try:
            goal = self.get_goal(goal_id)
            if not goal:
                return None
            
            goal.current_value = current_value
            goal.updated_at = datetime.now()
            
            # Auto-update status based on progress
            if goal.target_value and current_value >= goal.target_value:
                goal.status = "Achieved"
            elif goal.end_date and datetime.now().date() > goal.end_date.date():
                goal.status = "Overdue"
            
            self.db.commit()
            self.db.refresh(goal)
            return goal
        except Exception as e:
            self.db.rollback()
            raise e
    
    def update_goal(self, goal_id: int, **kwargs) -> Optional[Goal]:
        """Update goal information."""
        try:
            goal = self.get_goal(goal_id)
            if not goal:
                return None
            
            for key, value in kwargs.items():
                if hasattr(goal, key):
                    if key in ['start_date', 'end_date'] and isinstance(value, date):
                        setattr(goal, key, datetime.combine(value, datetime.min.time()))
                    else:
                        setattr(goal, key, value)
            
            goal.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(goal)
            return goal
        except Exception as e:
            self.db.rollback()
            raise e
    
    def delete_goal(self, goal_id: int) -> bool:
        """Delete a goal."""
        try:
            goal = self.get_goal(goal_id)
            if not goal:
                return False
            
            self.db.delete(goal)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_goal_progress_percentage(self, goal_id: int) -> float:
        """Get goal progress as a percentage."""
        goal = self.get_goal(goal_id)
        if not goal or not goal.target_value or goal.target_value == 0:
            return 0.0
        
        return min((goal.current_value / goal.target_value) * 100, 100.0)
    
    # Performance Metrics Management
    def record_performance_metric(self, name: str, value: float, 
                                 date: date = None, notes: str = None) -> PerformanceMetric:
        """Record a performance metric."""
        try:
            metric_date = datetime.combine(date or datetime.now().date(), datetime.min.time())
            
            metric = PerformanceMetric(
                name=name,
                value=value,
                date=metric_date,
                notes=notes,
                created_at=datetime.now()
            )
            
            self.db.add(metric)
            self.db.commit()
            self.db.refresh(metric)
            return metric
        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_performance_metric(self, metric_id: int) -> Optional[PerformanceMetric]:
        """Get a performance metric by ID."""
        return self.db.query(PerformanceMetric).filter(PerformanceMetric.id == metric_id).first()
    
    def get_all_performance_metrics(self) -> List[PerformanceMetric]:
        """Get all performance metrics."""
        return self.db.query(PerformanceMetric).order_by(PerformanceMetric.date.desc()).all()
    
    def get_performance_metrics_by_name(self, name: str) -> List[PerformanceMetric]:
        """Get performance metrics by name."""
        return self.db.query(PerformanceMetric).filter(
            PerformanceMetric.name == name
        ).order_by(PerformanceMetric.date.desc()).all()
    
    def get_latest_metric_value(self, name: str) -> Optional[float]:
        """Get the latest value for a specific metric."""
        metric = self.db.query(PerformanceMetric).filter(
            PerformanceMetric.name == name
        ).order_by(PerformanceMetric.date.desc()).first()
        
        return metric.value if metric else None
    
    def get_metric_trend(self, name: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get metric trend over the last N days."""
        end_date = datetime.now()
        start_date = end_date - datetime.timedelta(days=days)
        
        metrics = self.db.query(PerformanceMetric).filter(
            PerformanceMetric.name == name,
            PerformanceMetric.date >= start_date,
            PerformanceMetric.date <= end_date
        ).order_by(PerformanceMetric.date.asc()).all()
        
        return [
            {
                'date': metric.date.date().isoformat(),
                'value': metric.value,
                'notes': metric.notes
            }
            for metric in metrics
        ]
    
    # Partnership Management
    def create_partnership(self, name: str, partnership_type: str = None,
                          contact_person: str = None, status: str = "Prospect",
                          notes: str = None) -> Partnership:
        """Create a new partnership record."""
        try:
            partnership = Partnership(
                name=name,
                type=partnership_type,
                contact_person=contact_person,
                status=status,
                notes=notes,
                created_at=datetime.now()
            )
            
            self.db.add(partnership)
            self.db.commit()
            self.db.refresh(partnership)
            return partnership
        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_partnership(self, partnership_id: int) -> Optional[Partnership]:
        """Get a partnership by ID."""
        return self.db.query(Partnership).filter(Partnership.id == partnership_id).first()
    
    def get_all_partnerships(self) -> List[Partnership]:
        """Get all partnerships."""
        return self.db.query(Partnership).order_by(Partnership.created_at.desc()).all()
    
    def get_partnerships_by_status(self, status: str) -> List[Partnership]:
        """Get partnerships by status."""
        return self.db.query(Partnership).filter(Partnership.status == status).all()
    
    def update_partnership_status(self, partnership_id: int, status: str, notes: str = None) -> Optional[Partnership]:
        """Update partnership status."""
        try:
            partnership = self.get_partnership(partnership_id)
            if not partnership:
                return None
            
            partnership.status = status
            if notes:
                existing_notes = partnership.notes or ""
                partnership.notes = f"{existing_notes}\n[{datetime.now().strftime('%Y-%m-%d %H:%M')}] Status changed to {status}: {notes}".strip()
            partnership.updated_at = datetime.now()
            
            self.db.commit()
            self.db.refresh(partnership)
            return partnership
        except Exception as e:
            self.db.rollback()
            raise e
    
    def update_partnership(self, partnership_id: int, **kwargs) -> Optional[Partnership]:
        """Update partnership information."""
        try:
            partnership = self.get_partnership(partnership_id)
            if not partnership:
                return None
            
            for key, value in kwargs.items():
                if hasattr(partnership, key):
                    setattr(partnership, key, value)
            
            partnership.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(partnership)
            return partnership
        except Exception as e:
            self.db.rollback()
            raise e
    
    def delete_partnership(self, partnership_id: int) -> bool:
        """Delete a partnership."""
        try:
            partnership = self.get_partnership(partnership_id)
            if not partnership:
                return False
            
            self.db.delete(partnership)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e
    
    # Analytics and Insights
    def get_strategic_overview(self) -> Dict[str, Any]:
        """Get strategic planning overview."""
        goals = self.get_all_goals()
        partnerships = self.get_all_partnerships()
        
        # Goal statistics
        total_goals = len(goals)
        achieved_goals = len([g for g in goals if g.status == "Achieved"])
        in_progress_goals = len([g for g in goals if g.status == "In Progress"])
        overdue_goals = len([g for g in goals if g.status == "Overdue"])
        
        # Partnership statistics
        total_partnerships = len(partnerships)
        active_partnerships = len([p for p in partnerships if p.status == "Active"])
        prospect_partnerships = len([p for p in partnerships if p.status == "Prospect"])
        
        # Calculate average goal progress
        goals_with_targets = [g for g in goals if g.target_value and g.target_value > 0]
        avg_goal_progress = 0
        if goals_with_targets:
            total_progress = sum(self.get_goal_progress_percentage(g.id) for g in goals_with_targets)
            avg_goal_progress = total_progress / len(goals_with_targets)
        
        return {
            'goals': {
                'total': total_goals,
                'achieved': achieved_goals,
                'in_progress': in_progress_goals,
                'overdue': overdue_goals,
                'average_progress_percentage': avg_goal_progress
            },
            'partnerships': {
                'total': total_partnerships,
                'active': active_partnerships,
                'prospects': prospect_partnerships
            }
        }
    
    def get_goal_recommendations(self) -> List[str]:
        """Get goal recommendations based on current business state."""
        recommendations = []
        
        goals = self.get_all_goals()
        
        # Check if basic business goals exist
        goal_names = [g.name.lower() for g in goals]
        
        if not any('farmer' in name for name in goal_names):
            recommendations.append("Set a goal to onboard a specific number of farmers (e.g., 25 farmers)")
        
        if not any('customer' in name or 'hotel' in name or 'restaurant' in name for name in goal_names):
            recommendations.append("Set a goal to acquire a specific number of customers (e.g., 25 hotels/restaurants)")
        
        if not any('revenue' in name or 'sales' in name for name in goal_names):
            recommendations.append("Set monthly or quarterly revenue targets")
        
        if not any('quality' in name for name in goal_names):
            recommendations.append("Set quality improvement goals (e.g., maintain 95% customer satisfaction)")
        
        # Check for overdue goals
        overdue_goals = [g for g in goals if g.status == "Overdue"]
        if overdue_goals:
            recommendations.append(f"Review and update {len(overdue_goals)} overdue goals")
        
        # Check for goals without target values
        goals_without_targets = [g for g in goals if not g.target_value]
        if goals_without_targets:
            recommendations.append(f"Add specific target values to {len(goals_without_targets)} goals for better tracking")
        
        return recommendations
    
    def calculate_business_health_score(self) -> Dict[str, Any]:
        """Calculate overall business health score based on various metrics."""
        # This is a simplified business health calculation
        # In a real implementation, this would be more sophisticated
        
        score = 0
        max_score = 100
        factors = []
        
        # Goal achievement factor (30 points)
        goals = self.get_all_goals()
        if goals:
            achieved_goals = len([g for g in goals if g.status == "Achieved"])
            goal_score = min((achieved_goals / len(goals)) * 30, 30)
            score += goal_score
            factors.append(f"Goal Achievement: {goal_score:.1f}/30")
        else:
            factors.append("Goal Achievement: 0/30 (No goals set)")
        
        # Partnership development factor (20 points)
        partnerships = self.get_all_partnerships()
        if partnerships:
            active_partnerships = len([p for p in partnerships if p.status == "Active"])
            partnership_score = min((active_partnerships / max(len(partnerships), 5)) * 20, 20)
            score += partnership_score
            factors.append(f"Partnership Development: {partnership_score:.1f}/20")
        else:
            factors.append("Partnership Development: 0/20 (No partnerships tracked)")
        
        # Performance metrics factor (25 points)
        recent_metrics = self.db.query(PerformanceMetric).filter(
            PerformanceMetric.date >= datetime.now() - datetime.timedelta(days=30)
        ).all()
        
        if recent_metrics:
            metrics_score = min(len(set(m.name for m in recent_metrics)) * 5, 25)
            score += metrics_score
            factors.append(f"Performance Tracking: {metrics_score:.1f}/25")
        else:
            factors.append("Performance Tracking: 0/25 (No recent metrics)")
        
        # Strategic planning activity factor (25 points)
        recent_activity_score = 0
        
        # Check for recent goal updates
        recent_goals = [g for g in goals if g.updated_at and g.updated_at >= datetime.now() - datetime.timedelta(days=30)]
        if recent_goals:
            recent_activity_score += 10
        
        # Check for goal progress updates
        goals_with_progress = [g for g in goals if g.current_value and g.current_value > 0]
        if goals_with_progress:
            recent_activity_score += 10
        
        # Check for new partnerships
        recent_partnerships = [p for p in partnerships if p.created_at >= datetime.now() - datetime.timedelta(days=30)]
        if recent_partnerships:
            recent_activity_score += 5
        
        score += recent_activity_score
        factors.append(f"Strategic Activity: {recent_activity_score}/25")
        
        # Determine health level
        if score >= 80:
            health_level = "Excellent"
        elif score >= 60:
            health_level = "Good"
        elif score >= 40:
            health_level = "Fair"
        else:
            health_level = "Needs Improvement"
        
        return {
            'score': score,
            'max_score': max_score,
            'percentage': (score / max_score) * 100,
            'health_level': health_level,
            'factors': factors
        }

