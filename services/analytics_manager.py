#!/usr/bin/env python3
"""
Analytics Manager for Task Planner
Provides comprehensive analytics and insights
"""

from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime, date, timedelta
from collections import defaultdict, Counter
import calendar
from models.task import Task
from models.category import Category
from models.goal import Goal
from database.settings_manager import SettingsManager

class AnalyticsManager:
    """Provides analytics and insights for task management"""
    
    def __init__(self):
        self.settings = SettingsManager()
        self.cache = {}
        self.cache_timeout = 300  # 5 minutes
    
    def get_productivity_overview(self, days: int = 30) -> Dict[str, Any]:
        """Get productivity overview for the last N days"""
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            # Get tasks in date range
            all_tasks = Task.get_all()
            period_tasks = [
                task for task in all_tasks
                if task.created_at and task.created_at.date() >= start_date
            ]
            
            # Calculate metrics
            total_tasks = len(period_tasks)
            completed_tasks = len([t for t in period_tasks if t.status == 'completed'])
            in_progress_tasks = len([t for t in period_tasks if t.status == 'in_progress'])
            pending_tasks = len([t for t in period_tasks if t.status == 'pending'])
            overdue_tasks = len([t for t in period_tasks if self.is_overdue(t)])
            
            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            # Time analysis
            total_estimated_time = sum(
                t.estimated_duration or 0 for t in period_tasks
            )
            total_actual_time = sum(
                t.actual_duration or 0 for t in period_tasks if t.status == 'completed'
            )
            
            # Daily productivity
            daily_stats = self.get_daily_productivity(start_date, end_date)
            
            return {
                'period_days': days,
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'in_progress_tasks': in_progress_tasks,
                'pending_tasks': pending_tasks,
                'overdue_tasks': overdue_tasks,
                'completion_rate': round(completion_rate, 1),
                'total_estimated_time': total_estimated_time,
                'total_actual_time': total_actual_time,
                'daily_stats': daily_stats,
                'productivity_trend': self.calculate_productivity_trend(daily_stats)
            }
            
        except Exception as e:
            print(f"Error getting productivity overview: {e}")
            return {}
    
    def get_daily_productivity(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Get daily productivity statistics"""
        daily_stats = []
        current_date = start_date
        
        while current_date <= end_date:
            # Get tasks for this day
            day_tasks = Task.get_by_date_range(current_date, current_date)
            
            completed_today = len([t for t in day_tasks if t.status == 'completed'])
            created_today = len([
                t for t in Task.get_all()
                if t.created_at and t.created_at.date() == current_date
            ])
            
            daily_stats.append({
                'date': current_date.isoformat(),
                'day_name': current_date.strftime('%A'),
                'completed_tasks': completed_today,
                'created_tasks': created_today,
                'productivity_score': self.calculate_daily_score(completed_today, created_today)
            })
            
            current_date += timedelta(days=1)
        
        return daily_stats
    
    def calculate_daily_score(self, completed: int, created: int) -> float:
        """Calculate a daily productivity score"""
        if created == 0 and completed == 0:
            return 0.0
        if created == 0:
            return min(completed * 10, 100)  # Bonus for completing without creating
        
        completion_ratio = completed / created
        base_score = completion_ratio * 50
        volume_bonus = min(completed * 5, 50)
        
        return min(base_score + volume_bonus, 100)
    
    def calculate_productivity_trend(self, daily_stats: List[Dict[str, Any]]) -> str:
        """Calculate productivity trend"""
        if len(daily_stats) < 7:
            return "insufficient_data"
        
        recent_scores = [day['productivity_score'] for day in daily_stats[-7:]]
        earlier_scores = [day['productivity_score'] for day in daily_stats[-14:-7]]
        
        recent_avg = sum(recent_scores) / len(recent_scores)
        earlier_avg = sum(earlier_scores) / len(earlier_scores)
        
        if recent_avg > earlier_avg + 10:
            return "improving"
        elif recent_avg < earlier_avg - 10:
            return "declining"
        else:
            return "stable"
    
    def get_category_analytics(self) -> Dict[str, Any]:
        """Get analytics by category"""
        try:
            categories = Category.get_all()
            category_stats = {}
            
            for category in categories:
                tasks = Task.get_by_category(category.id)
                
                total_tasks = len(tasks)
                completed_tasks = len([t for t in tasks if t.status == 'completed'])
                avg_completion_time = self.calculate_avg_completion_time(
                    [t for t in tasks if t.status == 'completed']
                )
                
                category_stats[category.name] = {
                    'total_tasks': total_tasks,
                    'completed_tasks': completed_tasks,
                    'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
                    'avg_completion_time': avg_completion_time,
                    'color': category.color
                }
            
            return category_stats
            
        except Exception as e:
            print(f"Error getting category analytics: {e}")
            return {}
    
    def get_priority_analytics(self) -> Dict[str, Any]:
        """Get analytics by priority"""
        try:
            from models.priority import Priority
            priorities = Priority.get_all()
            priority_stats = {}
            
            for priority in priorities:
                tasks = [t for t in Task.get_all() if t.priority_id == priority.id]
                
                total_tasks = len(tasks)
                completed_tasks = len([t for t in tasks if t.status == 'completed'])
                overdue_tasks = len([t for t in tasks if self.is_overdue(t)])
                
                priority_stats[priority.name] = {
                    'total_tasks': total_tasks,
                    'completed_tasks': completed_tasks,
                    'overdue_tasks': overdue_tasks,
                    'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
                    'overdue_rate': (overdue_tasks / total_tasks * 100) if total_tasks > 0 else 0
                }
            
            return priority_stats
            
        except Exception as e:
            print(f"Error getting priority analytics: {e}")
            return {}
    
    def get_time_analytics(self) -> Dict[str, Any]:
        """Get time-based analytics"""
        try:
            all_tasks = Task.get_all()
            completed_tasks = [t for t in all_tasks if t.status == 'completed']
            
            # Time estimation accuracy
            estimated_vs_actual = []
            for task in completed_tasks:
                if task.estimated_duration and task.actual_duration:
                    estimated_vs_actual.append({
                        'estimated': task.estimated_duration,
                        'actual': task.actual_duration,
                        'accuracy': abs(task.estimated_duration - task.actual_duration) / task.estimated_duration
                    })
            
            avg_estimation_accuracy = 0
            if estimated_vs_actual:
                avg_estimation_accuracy = 1 - (sum(item['accuracy'] for item in estimated_vs_actual) / len(estimated_vs_actual))
            
            # Weekly patterns
            weekly_patterns = self.get_weekly_patterns()
            
            # Monthly trends
            monthly_trends = self.get_monthly_trends()
            
            return {
                'estimation_accuracy': round(avg_estimation_accuracy * 100, 1),
                'total_time_tracked': sum(t.actual_duration or 0 for t in completed_tasks),
                'avg_task_duration': self.calculate_avg_completion_time(completed_tasks),
                'weekly_patterns': weekly_patterns,
                'monthly_trends': monthly_trends
            }
            
        except Exception as e:
            print(f"Error getting time analytics: {e}")
            return {}
    
    def get_weekly_patterns(self) -> Dict[str, Any]:
        """Get weekly productivity patterns"""
        all_tasks = Task.get_all()
        weekday_stats = defaultdict(lambda: {'completed': 0, 'created': 0})
        
        for task in all_tasks:
            if task.created_at:
                weekday = task.created_at.strftime('%A')
                weekday_stats[weekday]['created'] += 1
            
            if task.status == 'completed' and task.completed_at:
                weekday = task.completed_at.strftime('%A')
                weekday_stats[weekday]['completed'] += 1
        
        # Convert to list format
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekly_data = []
        
        for day in weekdays:
            stats = weekday_stats[day]
            weekly_data.append({
                'day': day,
                'completed': stats['completed'],
                'created': stats['created'],
                'productivity_score': self.calculate_daily_score(stats['completed'], stats['created'])
            })
        
        return {
            'daily_breakdown': weekly_data,
            'most_productive_day': max(weekly_data, key=lambda x: x['productivity_score'])['day'],
            'least_productive_day': min(weekly_data, key=lambda x: x['productivity_score'])['day']
        }
    
    def get_monthly_trends(self) -> List[Dict[str, Any]]:
        """Get monthly productivity trends"""
        all_tasks = Task.get_all()
        monthly_stats = defaultdict(lambda: {'completed': 0, 'created': 0})
        
        for task in all_tasks:
            if task.created_at:
                month_key = task.created_at.strftime('%Y-%m')
                monthly_stats[month_key]['created'] += 1
            
            if task.status == 'completed' and task.completed_at:
                month_key = task.completed_at.strftime('%Y-%m')
                monthly_stats[month_key]['completed'] += 1
        
        # Convert to sorted list
        monthly_data = []
        for month_key in sorted(monthly_stats.keys()):
            stats = monthly_stats[month_key]
            year, month = month_key.split('-')
            month_name = calendar.month_name[int(month)]
            
            monthly_data.append({
                'month': month_key,
                'month_name': f"{month_name} {year}",
                'completed': stats['completed'],
                'created': stats['created'],
                'completion_rate': (stats['completed'] / stats['created'] * 100) if stats['created'] > 0 else 0
            })
        
        return monthly_data[-12:]  # Last 12 months
    
    def calculate_avg_completion_time(self, tasks: List[Task]) -> float:
        """Calculate average completion time for tasks"""
        completion_times = []
        
        for task in tasks:
            if task.created_at and task.completed_at:
                duration = (task.completed_at - task.created_at).total_seconds() / 3600  # hours
                completion_times.append(duration)
        
        return sum(completion_times) / len(completion_times) if completion_times else 0
    
    def is_overdue(self, task: Task) -> bool:
        """Check if a task is overdue"""
        if not task.due_date or task.status == 'completed':
            return False
        
        today = date.today()
        return task.due_date < today
    
    def get_goal_progress_analytics(self) -> Dict[str, Any]:
        """Get goal progress analytics"""
        try:
            goals = Goal.get_all()
            
            total_goals = len(goals)
            completed_goals = len([g for g in goals if g.status == 'completed'])
            active_goals = len([g for g in goals if g.status == 'active'])
            
            avg_progress = sum(g.progress_percentage for g in goals) / total_goals if total_goals > 0 else 0
            
            # Goals by category
            goal_categories = defaultdict(int)
            for goal in goals:
                if goal.category_id:
                    category = Category.get_by_id(goal.category_id)
                    if category:
                        goal_categories[category.name] += 1
            
            return {
                'total_goals': total_goals,
                'completed_goals': completed_goals,
                'active_goals': active_goals,
                'completion_rate': (completed_goals / total_goals * 100) if total_goals > 0 else 0,
                'avg_progress': round(avg_progress, 1),
                'goals_by_category': dict(goal_categories)
            }
            
        except Exception as e:
            print(f"Error getting goal analytics: {e}")
            return {}

# Global analytics manager instance
analytics_manager = AnalyticsManager()
