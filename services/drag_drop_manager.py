#!/usr/bin/env python3
"""
Drag and Drop Manager for Task Planner
Provides drag and drop functionality for tasks and categories
"""

import tkinter as tk
from typing import Optional, Callable, Any
from models.task import Task
from models.category import Category

class DragDropManager:
    """Manages drag and drop operations for tasks"""
    
    def __init__(self):
        self.drag_data = {}
        self.drop_targets = {}
        self.drag_callbacks = {}
        
    def make_draggable(self, widget, data_type: str, data_id: int, 
                      drag_start_callback: Optional[Callable] = None,
                      drag_end_callback: Optional[Callable] = None):
        """Make a widget draggable"""
        
        def start_drag(event):
            """Start drag operation"""
            self.drag_data = {
                'type': data_type,
                'id': data_id,
                'widget': widget,
                'start_x': event.x_root,
                'start_y': event.y_root
            }
            
            # Change cursor to indicate dragging
            widget.configure(cursor="hand2")
            
            # Add visual feedback
            self.add_drag_visual_feedback(widget)
            
            if drag_start_callback:
                drag_start_callback(data_type, data_id)
            
            print(f"🖱️ Started dragging {data_type} ID: {data_id}")
        
        def drag_motion(event):
            """Handle drag motion"""
            if not self.drag_data:
                return
            
            # Update visual feedback position
            self.update_drag_visual_feedback(event.x_root, event.y_root)
        
        def end_drag(event):
            """End drag operation"""
            if not self.drag_data:
                return
            
            # Reset cursor
            widget.configure(cursor="")
            
            # Remove visual feedback
            self.remove_drag_visual_feedback()
            
            # Find drop target
            drop_target = self.find_drop_target(event.x_root, event.y_root)
            
            if drop_target:
                self.handle_drop(drop_target, event.x_root, event.y_root)
            
            if drag_end_callback:
                drag_end_callback(data_type, data_id)
            
            # Clear drag data
            self.drag_data = {}
            
            print(f"🖱️ Ended dragging {data_type} ID: {data_id}")
        
        # Bind drag events
        widget.bind("<Button-1>", start_drag)
        widget.bind("<B1-Motion>", drag_motion)
        widget.bind("<ButtonRelease-1>", end_drag)
    
    def make_drop_target(self, widget, target_type: str, target_id: Optional[int] = None,
                        drop_callback: Optional[Callable] = None,
                        hover_callback: Optional[Callable] = None):
        """Make a widget a drop target"""
        
        target_info = {
            'widget': widget,
            'type': target_type,
            'id': target_id,
            'drop_callback': drop_callback,
            'hover_callback': hover_callback
        }
        
        # Store target info using widget as key
        self.drop_targets[widget] = target_info
        
        def on_enter(event):
            """Handle mouse enter for drop target"""
            if self.drag_data and hover_callback:
                hover_callback(True, target_type, target_id)
            
            # Add visual feedback for valid drop target
            if self.is_valid_drop_target(target_type, target_id):
                self.add_drop_target_feedback(widget, True)
        
        def on_leave(event):
            """Handle mouse leave for drop target"""
            if self.drag_data and hover_callback:
                hover_callback(False, target_type, target_id)
            
            # Remove visual feedback
            self.add_drop_target_feedback(widget, False)
        
        # Bind hover events
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def add_drag_visual_feedback(self, widget):
        """Add visual feedback during drag"""
        try:
            # Make widget slightly transparent and add border
            widget.configure(
                fg_color=("gray80", "gray30"),
                border_width=2,
                border_color=("#3b82f6", "#60a5fa")
            )
        except:
            pass  # Ignore if widget doesn't support these properties
    
    def update_drag_visual_feedback(self, x: int, y: int):
        """Update drag visual feedback position"""
        # Could add a floating preview widget here
        pass
    
    def remove_drag_visual_feedback(self):
        """Remove drag visual feedback"""
        if 'widget' in self.drag_data:
            widget = self.drag_data['widget']
            try:
                # Reset widget appearance
                widget.configure(
                    fg_color=("gray90", "gray20"),
                    border_width=0
                )
            except:
                pass
    
    def add_drop_target_feedback(self, widget, is_valid: bool):
        """Add visual feedback for drop targets"""
        try:
            if is_valid and self.drag_data:
                # Highlight valid drop target
                widget.configure(
                    fg_color=("#e0f2fe", "#1e3a8a"),
                    border_width=2,
                    border_color=("#10b981", "#34d399")
                )
            else:
                # Reset appearance
                widget.configure(
                    fg_color=("gray90", "gray20"),
                    border_width=0
                )
        except:
            pass
    
    def find_drop_target(self, x: int, y: int):
        """Find drop target at given coordinates"""
        for widget, target_info in self.drop_targets.items():
            try:
                # Get widget coordinates
                widget_x = widget.winfo_rootx()
                widget_y = widget.winfo_rooty()
                widget_width = widget.winfo_width()
                widget_height = widget.winfo_height()
                
                # Check if coordinates are within widget bounds
                if (widget_x <= x <= widget_x + widget_width and
                    widget_y <= y <= widget_y + widget_height):
                    return target_info
            except:
                continue
        
        return None
    
    def is_valid_drop_target(self, target_type: str, target_id: Optional[int]) -> bool:
        """Check if current drag data can be dropped on target"""
        if not self.drag_data:
            return False
        
        drag_type = self.drag_data['type']
        drag_id = self.drag_data['id']
        
        # Define valid drop combinations
        valid_combinations = {
            'task': ['category', 'priority', 'status', 'task_list'],
            'category': ['category_list'],
            'goal': ['category', 'goal_list']
        }
        
        return target_type in valid_combinations.get(drag_type, [])
    
    def handle_drop(self, target_info: dict, x: int, y: int):
        """Handle drop operation"""
        if not self.drag_data:
            return
        
        drag_type = self.drag_data['type']
        drag_id = self.drag_data['id']
        target_type = target_info['type']
        target_id = target_info['id']
        
        print(f"🎯 Dropping {drag_type} {drag_id} onto {target_type} {target_id}")
        
        # Handle different drop scenarios
        if drag_type == 'task' and target_type == 'category':
            self.handle_task_to_category_drop(drag_id, target_id)
        elif drag_type == 'task' and target_type == 'priority':
            self.handle_task_to_priority_drop(drag_id, target_id)
        elif drag_type == 'task' and target_type == 'status':
            self.handle_task_to_status_drop(drag_id, target_id)
        elif drag_type == 'task' and target_type == 'task_list':
            self.handle_task_reorder_drop(drag_id, target_id, x, y)
        
        # Call custom drop callback if provided
        if target_info['drop_callback']:
            target_info['drop_callback'](drag_type, drag_id, target_type, target_id)
    
    def handle_task_to_category_drop(self, task_id: int, category_id: int):
        """Handle dropping task onto category"""
        try:
            task = Task.get_by_id(task_id)
            if task:
                task.category_id = category_id
                if task.save():
                    print(f"✅ Moved task {task_id} to category {category_id}")
                    return True
        except Exception as e:
            print(f"❌ Error moving task to category: {e}")
        return False
    
    def handle_task_to_priority_drop(self, task_id: int, priority_id: int):
        """Handle dropping task onto priority"""
        try:
            task = Task.get_by_id(task_id)
            if task:
                task.priority_id = priority_id
                if task.save():
                    print(f"✅ Changed task {task_id} priority to {priority_id}")
                    return True
        except Exception as e:
            print(f"❌ Error changing task priority: {e}")
        return False
    
    def handle_task_to_status_drop(self, task_id: int, status: str):
        """Handle dropping task onto status"""
        try:
            task = Task.get_by_id(task_id)
            if task:
                task.status = status
                if task.save():
                    print(f"✅ Changed task {task_id} status to {status}")
                    return True
        except Exception as e:
            print(f"❌ Error changing task status: {e}")
        return False
    
    def handle_task_reorder_drop(self, task_id: int, target_task_id: int, x: int, y: int):
        """Handle reordering tasks"""
        # This would require implementing task ordering in the database
        print(f"📝 Reordering task {task_id} relative to {target_task_id}")
        # TODO: Implement task reordering logic
        return True
    
    def enable_task_drag_drop(self, task_widget, task_id: int, 
                             refresh_callback: Optional[Callable] = None):
        """Enable drag and drop for a task widget"""
        
        def on_drag_start(data_type, data_id):
            print(f"🖱️ Started dragging task {data_id}")
        
        def on_drag_end(data_type, data_id):
            if refresh_callback:
                refresh_callback()
        
        self.make_draggable(
            task_widget, 
            'task', 
            task_id,
            drag_start_callback=on_drag_start,
            drag_end_callback=on_drag_end
        )
    
    def enable_category_drop_target(self, category_widget, category_id: int,
                                   refresh_callback: Optional[Callable] = None):
        """Enable category as drop target"""
        
        def on_drop(drag_type, drag_id, target_type, target_id):
            if refresh_callback:
                refresh_callback()
        
        self.make_drop_target(
            category_widget,
            'category',
            category_id,
            drop_callback=on_drop
        )

# Global drag drop manager instance
drag_drop_manager = DragDropManager()
