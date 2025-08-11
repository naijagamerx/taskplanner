"""
Category model for Task Planner application
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import db_manager

class Category:
    """Category model class"""
    
    def __init__(self, category_id: Optional[int] = None, user_id: int = 1, name: str = "",
                 color: str = "#3498db", description: str = "", created_at: Optional[datetime] = None,
                 updated_at: Optional[datetime] = None):
        
        self.id = category_id
        self.user_id = user_id
        self.name = name
        self.color = color
        self.description = description
        self.created_at = created_at
        self.updated_at = updated_at
    
    def save(self) -> bool:
        """Save category to database"""
        try:
            if self.id is None:
                # Insert new category
                query = """
                INSERT INTO categories (user_id, name, color, description)
                VALUES (%s, %s, %s, %s)
                """
                params = (self.user_id, self.name, self.color, self.description)
                
                self.id = db_manager.execute_insert(query, params)
                return self.id is not None
            else:
                # Update existing category
                query = """
                UPDATE categories SET name=%s, color=%s, description=%s, updated_at=CURRENT_TIMESTAMP
                WHERE id=%s
                """
                params = (self.name, self.color, self.description, self.id)
                
                return db_manager.execute_update(query, params) > 0
                
        except Exception as e:
            print(f"Error saving category: {e}")
            return False
    
    def delete(self) -> bool:
        """Delete category from database"""
        if self.id is None:
            return False
        
        try:
            query = "DELETE FROM categories WHERE id = %s"
            return db_manager.execute_update(query, (self.id,)) > 0
        except Exception as e:
            print(f"Error deleting category: {e}")
            return False
    
    @classmethod
    def get_by_id(cls, category_id: int) -> Optional['Category']:
        """Get category by ID"""
        try:
            query = "SELECT * FROM categories WHERE id = %s"
            results = db_manager.execute_query(query, (category_id,))
            
            if results:
                return cls._from_dict(results[0])
            return None
            
        except Exception as e:
            print(f"Error getting category by ID: {e}")
            return None
    
    @classmethod
    def get_all(cls, user_id: int = 1) -> List['Category']:
        """Get all categories for a user"""
        try:
            query = "SELECT * FROM categories WHERE user_id = %s ORDER BY name"
            results = db_manager.execute_query(query, (user_id,))
            
            return [cls._from_dict(row) for row in results]
            
        except Exception as e:
            print(f"Error getting all categories: {e}")
            return []
    
    @classmethod
    def get_by_name(cls, name: str, user_id: int = 1) -> Optional['Category']:
        """Get category by name"""
        try:
            query = "SELECT * FROM categories WHERE user_id = %s AND name = %s"
            results = db_manager.execute_query(query, (user_id, name))
            
            if results:
                return cls._from_dict(results[0])
            return None
            
        except Exception as e:
            print(f"Error getting category by name: {e}")
            return None
    
    @classmethod
    def _from_dict(cls, data: Dict[str, Any]) -> 'Category':
        """Create Category instance from dictionary"""
        return cls(
            category_id=data.get('id'),
            user_id=data.get('user_id'),
            name=data.get('name', ''),
            color=data.get('color', '#3498db'),
            description=data.get('description', ''),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert category to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'color': self.color,
            'description': self.description,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

class Priority:
    """Priority level model class"""
    
    def __init__(self, priority_id: Optional[int] = None, name: str = "", level: int = 1,
                 color: str = "#95a5a6", description: str = ""):
        
        self.id = priority_id
        self.name = name
        self.level = level
        self.color = color
        self.description = description
    
    @classmethod
    def get_all(cls) -> List['Priority']:
        """Get all priority levels"""
        try:
            query = "SELECT * FROM priority_levels ORDER BY level"
            results = db_manager.execute_query(query)
            
            return [cls._from_dict(row) for row in results]
            
        except Exception as e:
            print(f"Error getting all priorities: {e}")
            return []
    
    @classmethod
    def get_by_id(cls, priority_id: int) -> Optional['Priority']:
        """Get priority by ID"""
        try:
            query = "SELECT * FROM priority_levels WHERE id = %s"
            results = db_manager.execute_query(query, (priority_id,))
            
            if results:
                return cls._from_dict(results[0])
            return None
            
        except Exception as e:
            print(f"Error getting priority by ID: {e}")
            return None
    
    @classmethod
    def _from_dict(cls, data: Dict[str, Any]) -> 'Priority':
        """Create Priority instance from dictionary"""
        return cls(
            priority_id=data.get('id'),
            name=data.get('name', ''),
            level=data.get('level', 1),
            color=data.get('color', '#95a5a6'),
            description=data.get('description', '')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert priority to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'level': self.level,
            'color': self.color,
            'description': self.description
        }
