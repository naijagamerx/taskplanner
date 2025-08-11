"""
Task model for Task Planner application
"""

from datetime import datetime, date, time
from typing import Optional, List, Dict, Any
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import db_manager

class Task:
    """Task model class"""
    
    def __init__(self, task_id: Optional[int] = None, user_id: int = 1, category_id: Optional[int] = None,
                 priority_id: int = 2, title: str = "", description: str = "", due_date: Optional[date] = None,
                 due_time: Optional[time] = None, estimated_duration: Optional[int] = None,
                 actual_duration: Optional[int] = None, status: str = "pending",
                 is_recurring: bool = False, recurrence_pattern: Optional[str] = None,
                 recurrence_interval: int = 1, recurrence_end_date: Optional[date] = None,
                 parent_task_id: Optional[int] = None, created_at: Optional[datetime] = None,
                 updated_at: Optional[datetime] = None, completed_at: Optional[datetime] = None):
        
        self.id = task_id
        self.user_id = user_id
        self.category_id = category_id
        self.priority_id = priority_id
        self.title = title
        self.description = description
        self.due_date = due_date
        self.due_time = due_time
        self.estimated_duration = estimated_duration
        self.actual_duration = actual_duration
        self.status = status
        self.is_recurring = is_recurring
        self.recurrence_pattern = recurrence_pattern
        self.recurrence_interval = recurrence_interval
        self.recurrence_end_date = recurrence_end_date
        self.parent_task_id = parent_task_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.completed_at = completed_at
    
    def save(self) -> bool:
        """Save task to database"""
        try:
            if self.id is None:
                # Insert new task
                query = """
                INSERT INTO tasks (user_id, category_id, priority_id, title, description, 
                                 due_date, due_time, estimated_duration, actual_duration, 
                                 status, is_recurring, recurrence_pattern, recurrence_interval, 
                                 recurrence_end_date, parent_task_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                params = (self.user_id, self.category_id, self.priority_id, self.title,
                         self.description, self.due_date, self.due_time, self.estimated_duration,
                         self.actual_duration, self.status, self.is_recurring,
                         self.recurrence_pattern, self.recurrence_interval,
                         self.recurrence_end_date, self.parent_task_id)
                
                self.id = db_manager.execute_insert(query, params)
                return self.id is not None
            else:
                # Update existing task
                query = """
                UPDATE tasks SET category_id=%s, priority_id=%s, title=%s, description=%s,
                               due_date=%s, due_time=%s, estimated_duration=%s, actual_duration=%s,
                               status=%s, is_recurring=%s, recurrence_pattern=%s, recurrence_interval=%s,
                               recurrence_end_date=%s, parent_task_id=%s, updated_at=CURRENT_TIMESTAMP
                WHERE id=%s
                """
                params = (self.category_id, self.priority_id, self.title, self.description,
                         self.due_date, self.due_time, self.estimated_duration, self.actual_duration,
                         self.status, self.is_recurring, self.recurrence_pattern,
                         self.recurrence_interval, self.recurrence_end_date, self.parent_task_id, self.id)
                
                return db_manager.execute_update(query, params) > 0
                
        except Exception as e:
            print(f"Error saving task: {e}")
            return False
    
    def delete(self) -> bool:
        """Delete task from database"""
        if self.id is None:
            return False
        
        try:
            query = "DELETE FROM tasks WHERE id = %s"
            return db_manager.execute_update(query, (self.id,)) > 0
        except Exception as e:
            print(f"Error deleting task: {e}")
            return False
    
    def mark_completed(self) -> bool:
        """Mark task as completed"""
        self.status = "completed"
        self.completed_at = datetime.now()
        return self.save()
    
    def mark_in_progress(self) -> bool:
        """Mark task as in progress"""
        self.status = "in_progress"
        return self.save()
    
    @classmethod
    def get_by_id(cls, task_id: int) -> Optional['Task']:
        """Get task by ID"""
        try:
            query = "SELECT * FROM tasks WHERE id = %s"
            results = db_manager.execute_query(query, (task_id,))
            
            if results:
                return cls._from_dict(results[0])
            return None
            
        except Exception as e:
            print(f"Error getting task by ID: {e}")
            return None
    
    @classmethod
    def get_all(cls, user_id: int = 1) -> List['Task']:
        """Get all tasks for a user"""
        try:
            query = "SELECT * FROM tasks WHERE user_id = %s ORDER BY created_at DESC"
            results = db_manager.execute_query(query, (user_id,))
            
            return [cls._from_dict(row) for row in results]
            
        except Exception as e:
            print(f"Error getting all tasks: {e}")
            return []
    
    @classmethod
    def get_by_status(cls, status: str, user_id: int = 1) -> List['Task']:
        """Get tasks by status"""
        try:
            query = "SELECT * FROM tasks WHERE user_id = %s AND status = %s ORDER BY created_at DESC"
            results = db_manager.execute_query(query, (user_id, status))
            
            return [cls._from_dict(row) for row in results]
            
        except Exception as e:
            print(f"Error getting tasks by status: {e}")
            return []
    
    @classmethod
    def get_by_date_range(cls, start_date: date, end_date: date, user_id: int = 1) -> List['Task']:
        """Get tasks within date range"""
        try:
            query = """
            SELECT * FROM tasks 
            WHERE user_id = %s AND due_date BETWEEN %s AND %s 
            ORDER BY due_date, due_time
            """
            results = db_manager.execute_query(query, (user_id, start_date, end_date))
            
            return [cls._from_dict(row) for row in results]
            
        except Exception as e:
            print(f"Error getting tasks by date range: {e}")
            return []
    
    @classmethod
    def get_overdue(cls, user_id: int = 1) -> List['Task']:
        """Get overdue tasks"""
        try:
            today = date.today()
            query = """
            SELECT * FROM tasks 
            WHERE user_id = %s AND due_date < %s AND status != 'completed' 
            ORDER BY due_date
            """
            results = db_manager.execute_query(query, (user_id, today))
            
            return [cls._from_dict(row) for row in results]
            
        except Exception as e:
            print(f"Error getting overdue tasks: {e}")
            return []
    
    @classmethod
    def _from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create Task instance from dictionary"""
        return cls(
            task_id=data.get('id'),
            user_id=data.get('user_id'),
            category_id=data.get('category_id'),
            priority_id=data.get('priority_id'),
            title=data.get('title', ''),
            description=data.get('description', ''),
            due_date=data.get('due_date'),
            due_time=data.get('due_time'),
            estimated_duration=data.get('estimated_duration'),
            actual_duration=data.get('actual_duration'),
            status=data.get('status', 'pending'),
            is_recurring=data.get('is_recurring', False),
            recurrence_pattern=data.get('recurrence_pattern'),
            recurrence_interval=data.get('recurrence_interval', 1),
            recurrence_end_date=data.get('recurrence_end_date'),
            parent_task_id=data.get('parent_task_id'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            completed_at=data.get('completed_at')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'priority_id': self.priority_id,
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date,
            'due_time': self.due_time,
            'estimated_duration': self.estimated_duration,
            'actual_duration': self.actual_duration,
            'status': self.status,
            'is_recurring': self.is_recurring,
            'recurrence_pattern': self.recurrence_pattern,
            'recurrence_interval': self.recurrence_interval,
            'recurrence_end_date': self.recurrence_end_date,
            'parent_task_id': self.parent_task_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'completed_at': self.completed_at
        }
