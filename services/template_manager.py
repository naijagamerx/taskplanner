#!/usr/bin/env python3
"""
Task Template Manager for Task Planner
Provides task templates and smart task creation
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime, date, timedelta
from models.task import Task
from models.category import Category
from models.priority import Priority
from database.settings_manager import SettingsManager

class TaskTemplate:
    """Represents a task template"""
    
    def __init__(self, template_id: str = None, name: str = "", description: str = "",
                 category_name: str = "", priority_name: str = "medium",
                 estimated_duration: int = None, tags: List[str] = None,
                 checklist: List[str] = None, default_due_offset: int = 1):
        self.template_id = template_id or f"template_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.name = name
        self.description = description
        self.category_name = category_name
        self.priority_name = priority_name
        self.estimated_duration = estimated_duration
        self.tags = tags or []
        self.checklist = checklist or []
        self.default_due_offset = default_due_offset  # Days from now
        self.created_at = datetime.now()
        self.usage_count = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary"""
        return {
            'template_id': self.template_id,
            'name': self.name,
            'description': self.description,
            'category_name': self.category_name,
            'priority_name': self.priority_name,
            'estimated_duration': self.estimated_duration,
            'tags': self.tags,
            'checklist': self.checklist,
            'default_due_offset': self.default_due_offset,
            'created_at': self.created_at.isoformat(),
            'usage_count': self.usage_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskTemplate':
        """Create template from dictionary"""
        template = cls(
            template_id=data.get('template_id'),
            name=data.get('name', ''),
            description=data.get('description', ''),
            category_name=data.get('category_name', ''),
            priority_name=data.get('priority_name', 'medium'),
            estimated_duration=data.get('estimated_duration'),
            tags=data.get('tags', []),
            checklist=data.get('checklist', []),
            default_due_offset=data.get('default_due_offset', 1)
        )
        
        # Parse created_at
        if 'created_at' in data:
            try:
                template.created_at = datetime.fromisoformat(data['created_at'])
            except:
                template.created_at = datetime.now()
        
        template.usage_count = data.get('usage_count', 0)
        return template

class TemplateManager:
    """Manages task templates and smart task creation"""
    
    def __init__(self):
        self.settings = SettingsManager()
        self.templates = {}
        self.load_templates()
        self.create_default_templates()
    
    def load_templates(self):
        """Load templates from settings"""
        try:
            template_data = self.settings.get('task_templates', {})
            self.templates = {}
            
            for template_id, data in template_data.items():
                self.templates[template_id] = TaskTemplate.from_dict(data)
            
            print(f"✅ Loaded {len(self.templates)} task templates")
            
        except Exception as e:
            print(f"Error loading templates: {e}")
            self.templates = {}
    
    def save_templates(self):
        """Save templates to settings"""
        try:
            template_data = {}
            for template_id, template in self.templates.items():
                template_data[template_id] = template.to_dict()
            
            self.settings.set('task_templates', template_data)
            self.settings.save()
            
        except Exception as e:
            print(f"Error saving templates: {e}")
    
    def create_default_templates(self):
        """Create default task templates if none exist"""
        if self.templates:
            return  # Already have templates
        
        default_templates = [
            TaskTemplate(
                name="📧 Email Task",
                description="Send email to {recipient} about {subject}",
                category_name="Work",
                priority_name="medium",
                estimated_duration=15,
                tags=["email", "communication"],
                checklist=["Draft email", "Review content", "Send email", "Follow up if needed"]
            ),
            TaskTemplate(
                name="📞 Phone Call",
                description="Call {contact} regarding {topic}",
                category_name="Work",
                priority_name="medium",
                estimated_duration=30,
                tags=["call", "communication"],
                checklist=["Prepare talking points", "Make the call", "Take notes", "Schedule follow-up if needed"]
            ),
            TaskTemplate(
                name="📝 Meeting Preparation",
                description="Prepare for meeting: {meeting_title}",
                category_name="Work",
                priority_name="high",
                estimated_duration=45,
                tags=["meeting", "preparation"],
                checklist=["Review agenda", "Prepare materials", "Research attendees", "Set up meeting room/tech"]
            ),
            TaskTemplate(
                name="🛒 Shopping List",
                description="Buy items: {items}",
                category_name="Personal",
                priority_name="low",
                estimated_duration=60,
                tags=["shopping", "errands"],
                checklist=["Make shopping list", "Check for coupons", "Go shopping", "Put items away"]
            ),
            TaskTemplate(
                name="💪 Workout Session",
                description="{workout_type} workout session",
                category_name="Health",
                priority_name="medium",
                estimated_duration=60,
                tags=["exercise", "health"],
                checklist=["Warm up", "Main workout", "Cool down", "Log progress"]
            ),
            TaskTemplate(
                name="📚 Study Session",
                description="Study {subject} - {topic}",
                category_name="Learning",
                priority_name="high",
                estimated_duration=90,
                tags=["study", "learning"],
                checklist=["Review previous notes", "Read new material", "Take notes", "Practice exercises", "Review and summarize"]
            ),
            TaskTemplate(
                name="🏠 Home Maintenance",
                description="Home maintenance: {task_description}",
                category_name="Home",
                priority_name="medium",
                estimated_duration=120,
                tags=["maintenance", "home"],
                checklist=["Gather tools/materials", "Complete task", "Clean up", "Schedule next maintenance"]
            ),
            TaskTemplate(
                name="💰 Financial Review",
                description="Review and update {financial_area}",
                category_name="Finance",
                priority_name="high",
                estimated_duration=45,
                tags=["finance", "review"],
                checklist=["Gather documents", "Review current status", "Update records", "Plan next steps"]
            ),
            TaskTemplate(
                name="🎯 Project Planning",
                description="Plan project: {project_name}",
                category_name="Work",
                priority_name="high",
                estimated_duration=120,
                tags=["planning", "project"],
                checklist=["Define objectives", "Break down tasks", "Set timeline", "Assign resources", "Create milestones"]
            ),
            TaskTemplate(
                name="🔄 Weekly Review",
                description="Weekly review and planning session",
                category_name="Personal",
                priority_name="medium",
                estimated_duration=30,
                tags=["review", "planning"],
                checklist=["Review completed tasks", "Assess progress", "Plan next week", "Update goals"]
            )
        ]
        
        for template in default_templates:
            self.templates[template.template_id] = template
        
        self.save_templates()
        print(f"✅ Created {len(default_templates)} default templates")
    
    def get_all_templates(self) -> List[TaskTemplate]:
        """Get all available templates"""
        return list(self.templates.values())
    
    def get_template(self, template_id: str) -> Optional[TaskTemplate]:
        """Get specific template by ID"""
        return self.templates.get(template_id)
    
    def create_template(self, name: str, description: str = "", category_name: str = "",
                       priority_name: str = "medium", estimated_duration: int = None,
                       tags: List[str] = None, checklist: List[str] = None) -> TaskTemplate:
        """Create a new template"""
        template = TaskTemplate(
            name=name,
            description=description,
            category_name=category_name,
            priority_name=priority_name,
            estimated_duration=estimated_duration,
            tags=tags or [],
            checklist=checklist or []
        )
        
        self.templates[template.template_id] = template
        self.save_templates()
        
        print(f"✅ Created template: {name}")
        return template
    
    def create_template_from_task(self, task: Task) -> TaskTemplate:
        """Create a template from an existing task"""
        try:
            # Get category and priority names
            category_name = ""
            if task.category_id:
                category = Category.get_by_id(task.category_id)
                if category:
                    category_name = category.name
            
            priority_name = "medium"
            if task.priority_id:
                priority = Priority.get_by_id(task.priority_id)
                if priority:
                    priority_name = priority.name
            
            template = TaskTemplate(
                name=f"Template: {task.title}",
                description=task.description or "",
                category_name=category_name,
                priority_name=priority_name,
                estimated_duration=task.estimated_duration,
                tags=[],  # Could extract from description
                checklist=[]  # Could parse from description
            )
            
            self.templates[template.template_id] = template
            self.save_templates()
            
            print(f"✅ Created template from task: {task.title}")
            return template
            
        except Exception as e:
            print(f"Error creating template from task: {e}")
            return None
    
    def create_task_from_template(self, template_id: str, 
                                 custom_values: Dict[str, str] = None) -> Optional[Task]:
        """Create a task from a template"""
        try:
            template = self.get_template(template_id)
            if not template:
                print(f"Template not found: {template_id}")
                return None
            
            custom_values = custom_values or {}
            
            # Replace placeholders in description
            description = template.description
            for placeholder, value in custom_values.items():
                description = description.replace(f"{{{placeholder}}}", value)
            
            # Get category ID
            category_id = None
            if template.category_name:
                categories = Category.get_all()
                for cat in categories:
                    if cat.name == template.category_name:
                        category_id = cat.id
                        break
            
            # Get priority ID
            priority_id = 2  # Default medium
            if template.priority_name:
                priorities = Priority.get_all()
                for pri in priorities:
                    if pri.name.lower() == template.priority_name.lower():
                        priority_id = pri.id
                        break
            
            # Calculate due date
            due_date = None
            if template.default_due_offset > 0:
                due_date = date.today() + timedelta(days=template.default_due_offset)
            
            # Create task
            task = Task(
                title=custom_values.get('title', template.name),
                description=description,
                category_id=category_id,
                priority_id=priority_id,
                due_date=due_date,
                estimated_duration=template.estimated_duration
            )
            
            # Save task
            if task.save():
                # Update template usage count
                template.usage_count += 1
                self.save_templates()
                
                print(f"✅ Created task from template: {template.name}")
                return task
            else:
                print(f"Failed to save task from template: {template.name}")
                return None
                
        except Exception as e:
            print(f"Error creating task from template: {e}")
            return None
    
    def delete_template(self, template_id: str) -> bool:
        """Delete a template"""
        try:
            if template_id in self.templates:
                del self.templates[template_id]
                self.save_templates()
                print(f"✅ Deleted template: {template_id}")
                return True
            return False
        except Exception as e:
            print(f"Error deleting template: {e}")
            return False
    
    def get_popular_templates(self, limit: int = 5) -> List[TaskTemplate]:
        """Get most used templates"""
        templates = list(self.templates.values())
        templates.sort(key=lambda t: t.usage_count, reverse=True)
        return templates[:limit]
    
    def search_templates(self, query: str) -> List[TaskTemplate]:
        """Search templates by name or description"""
        query_lower = query.lower()
        results = []
        
        for template in self.templates.values():
            if (query_lower in template.name.lower() or 
                query_lower in template.description.lower() or
                any(query_lower in tag.lower() for tag in template.tags)):
                results.append(template)
        
        return results

# Global template manager instance
template_manager = TemplateManager()
