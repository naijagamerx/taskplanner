"""
Goal model for Task Planner application
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import db_manager

class Goal:
    """Goal model class"""
    
    def __init__(self, goal_id: Optional[int] = None, user_id: int = 1, category_id: Optional[int] = None,
                 title: str = "", description: str = "", target_date: Optional[date] = None,
                 status: str = "active", progress_percentage: float = 0.0,
                 created_at: Optional[datetime] = None, updated_at: Optional[datetime] = None,
                 completed_at: Optional[datetime] = None):
        
        self.id = goal_id
        self.user_id = user_id
        self.category_id = category_id
        self.title = title
        self.description = description
        self.target_date = target_date
        self.status = status
        self.progress_percentage = progress_percentage
        self.created_at = created_at
        self.updated_at = updated_at
        self.completed_at = completed_at
    
    def save(self) -> bool:
        """Save goal to database"""
        try:
            if self.id is None:
                # Insert new goal
                query = """
                INSERT INTO goals (user_id, category_id, title, description, target_date, 
                                 status, progress_percentage)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                params = (self.user_id, self.category_id, self.title, self.description,
                         self.target_date, self.status, self.progress_percentage)
                
                self.id = db_manager.execute_insert(query, params)
                return self.id is not None
            else:
                # Update existing goal
                query = """
                UPDATE goals SET category_id=%s, title=%s, description=%s, target_date=%s,
                               status=%s, progress_percentage=%s, updated_at=CURRENT_TIMESTAMP
                WHERE id=%s
                """
                params = (self.category_id, self.title, self.description, self.target_date,
                         self.status, self.progress_percentage, self.id)
                
                return db_manager.execute_update(query, params) > 0
                
        except Exception as e:
            print(f"Error saving goal: {e}")
            return False
    
    def delete(self) -> bool:
        """Delete goal from database"""
        if self.id is None:
            return False
        
        try:
            query = "DELETE FROM goals WHERE id = %s"
            return db_manager.execute_update(query, (self.id,)) > 0
        except Exception as e:
            print(f"Error deleting goal: {e}")
            return False
    
    def mark_completed(self) -> bool:
        """Mark goal as completed"""
        self.status = "completed"
        self.progress_percentage = 100.0
        self.completed_at = datetime.now()
        return self.save()
    
    def update_progress(self, percentage: float) -> bool:
        """Update goal progress percentage"""
        self.progress_percentage = max(0.0, min(100.0, percentage))
        if self.progress_percentage >= 100.0:
            self.status = "completed"
            self.completed_at = datetime.now()
        return self.save()
    
    @classmethod
    def get_by_id(cls, goal_id: int) -> Optional['Goal']:
        """Get goal by ID"""
        try:
            query = "SELECT * FROM goals WHERE id = %s"
            results = db_manager.execute_query(query, (goal_id,))
            
            if results:
                return cls._from_dict(results[0])
            return None
            
        except Exception as e:
            print(f"Error getting goal by ID: {e}")
            return None
    
    @classmethod
    def get_all(cls, user_id: int = 1) -> List['Goal']:
        """Get all goals for a user"""
        try:
            query = "SELECT * FROM goals WHERE user_id = %s ORDER BY created_at DESC"
            results = db_manager.execute_query(query, (user_id,))
            
            return [cls._from_dict(row) for row in results]
            
        except Exception as e:
            print(f"Error getting all goals: {e}")
            return []
    
    @classmethod
    def get_by_status(cls, status: str, user_id: int = 1) -> List['Goal']:
        """Get goals by status"""
        try:
            query = "SELECT * FROM goals WHERE user_id = %s AND status = %s ORDER BY created_at DESC"
            results = db_manager.execute_query(query, (user_id, status))
            
            return [cls._from_dict(row) for row in results]
            
        except Exception as e:
            print(f"Error getting goals by status: {e}")
            return []
    
    @classmethod
    def get_active(cls, user_id: int = 1) -> List['Goal']:
        """Get active goals"""
        return cls.get_by_status("active", user_id)
    
    @classmethod
    def get_completed(cls, user_id: int = 1) -> List['Goal']:
        """Get completed goals"""
        return cls.get_by_status("completed", user_id)
    
    @classmethod
    def get_by_category(cls, category_id: int, user_id: int = 1) -> List['Goal']:
        """Get goals by category"""
        try:
            query = "SELECT * FROM goals WHERE user_id = %s AND category_id = %s ORDER BY created_at DESC"
            results = db_manager.execute_query(query, (user_id, category_id))
            
            return [cls._from_dict(row) for row in results]
            
        except Exception as e:
            print(f"Error getting goals by category: {e}")
            return []
    
    def get_related_tasks(self) -> List[Dict[str, Any]]:
        """Get tasks related to this goal"""
        if self.id is None:
            return []
        
        try:
            query = """
            SELECT t.* FROM tasks t
            JOIN task_goals tg ON t.id = tg.task_id
            WHERE tg.goal_id = %s
            ORDER BY t.created_at DESC
            """
            results = db_manager.execute_query(query, (self.id,))
            return results
            
        except Exception as e:
            print(f"Error getting related tasks: {e}")
            return []
    
    def add_task(self, task_id: int) -> bool:
        """Add a task to this goal"""
        if self.id is None:
            return False
        
        try:
            query = "INSERT IGNORE INTO task_goals (task_id, goal_id) VALUES (%s, %s)"
            return db_manager.execute_insert(query, (task_id, self.id)) is not None
        except Exception as e:
            print(f"Error adding task to goal: {e}")
            return False
    
    def remove_task(self, task_id: int) -> bool:
        """Remove a task from this goal"""
        if self.id is None:
            return False
        
        try:
            query = "DELETE FROM task_goals WHERE task_id = %s AND goal_id = %s"
            return db_manager.execute_update(query, (task_id, self.id)) > 0
        except Exception as e:
            print(f"Error removing task from goal: {e}")
            return False
    
    @classmethod
    def _from_dict(cls, data: Dict[str, Any]) -> 'Goal':
        """Create Goal instance from dictionary"""
        return cls(
            goal_id=data.get('id'),
            user_id=data.get('user_id'),
            category_id=data.get('category_id'),
            title=data.get('title', ''),
            description=data.get('description', ''),
            target_date=data.get('target_date'),
            status=data.get('status', 'active'),
            progress_percentage=float(data.get('progress_percentage', 0.0)),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            completed_at=data.get('completed_at')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert goal to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'title': self.title,
            'description': self.description,
            'target_date': self.target_date,
            'status': self.status,
            'progress_percentage': self.progress_percentage,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'completed_at': self.completed_at
        }
