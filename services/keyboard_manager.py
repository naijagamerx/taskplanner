#!/usr/bin/env python3
"""
Keyboard Shortcuts Manager for Task Planner
Provides comprehensive keyboard shortcut functionality
"""

import tkinter as tk
from typing import Dict, Callable, Optional, Any
from database.settings_manager import SettingsManager

class KeyboardManager:
    """Manages keyboard shortcuts and hotkeys"""
    
    def __init__(self, root_window):
        self.root = root_window
        self.settings = SettingsManager()
        self.shortcuts = {}
        self.main_window = None
        
        # Default keyboard shortcuts
        self.default_shortcuts = {
            # Task Management
            '<Control-n>': 'new_task',
            '<Control-Shift-N>': 'new_category',
            '<Control-d>': 'duplicate_task',
            '<Control-Delete>': 'delete_task',
            '<Control-e>': 'edit_task',
            '<Control-Return>': 'complete_task',
            '<Control-Shift-Return>': 'mark_in_progress',
            
            # Navigation
            '<Control-1>': 'show_tasks',
            '<Control-2>': 'show_calendar',
            '<Control-3>': 'show_goals',
            '<Control-4>': 'show_habits',
            '<Control-5>': 'show_analytics',
            '<Control-6>': 'show_settings',
            
            # Search and Filters
            '<Control-f>': 'focus_search',
            '<Control-Shift-F>': 'advanced_search',
            '<Control-r>': 'refresh_data',
            '<Control-Shift-R>': 'clear_filters',
            
            # View Controls
            '<Control-plus>': 'zoom_in',
            '<Control-minus>': 'zoom_out',
            '<Control-0>': 'reset_zoom',
            '<F5>': 'refresh_data',
            '<F11>': 'toggle_fullscreen',
            
            # Application
            '<Control-s>': 'save_all',
            '<Control-q>': 'quit_app',
            '<Control-comma>': 'show_settings',
            '<F1>': 'show_help',
            
            # Quick Actions
            '<Control-t>': 'quick_add_task',
            '<Control-Shift-T>': 'quick_add_template',
            '<Control-b>': 'toggle_sidebar',
            '<Control-Shift-D>': 'toggle_dark_mode',
            
            # Selection and Bulk Operations
            '<Control-a>': 'select_all_tasks',
            '<Control-Shift-A>': 'deselect_all',
            '<Control-i>': 'invert_selection',
            '<Delete>': 'delete_selected',
            '<Control-c>': 'copy_tasks',
            '<Control-v>': 'paste_tasks',
            
            # Priority and Status
            '<Control-Shift-1>': 'set_priority_low',
            '<Control-Shift-2>': 'set_priority_medium', 
            '<Control-Shift-3>': 'set_priority_high',
            '<Control-Shift-4>': 'set_priority_critical',
            '<Control-p>': 'toggle_priority',
            
            # Time Management
            '<Control-Shift-T>': 'start_timer',
            '<Control-Shift-S>': 'stop_timer',
            '<Control-Shift-P>': 'pause_timer',
            
            # Export and Backup
            '<Control-Shift-E>': 'export_data',
            '<Control-Shift-B>': 'backup_data',
            '<Control-Shift-I>': 'import_data'
        }
        
        self.load_custom_shortcuts()
        self.setup_shortcuts()
    
    def load_custom_shortcuts(self):
        """Load custom shortcuts from settings"""
        try:
            custom_shortcuts = self.settings.get('keyboard_shortcuts', {})
            # Merge with defaults, custom shortcuts override defaults
            self.shortcuts = {**self.default_shortcuts, **custom_shortcuts}
        except Exception as e:
            print(f"Error loading custom shortcuts: {e}")
            self.shortcuts = self.default_shortcuts.copy()
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts on the root window"""
        try:
            for key_combo, action in self.shortcuts.items():
                self.root.bind(key_combo, lambda event, a=action: self.handle_shortcut(a, event))
            
            print(f"✅ Loaded {len(self.shortcuts)} keyboard shortcuts")
        except Exception as e:
            print(f"Error setting up shortcuts: {e}")
    
    def handle_shortcut(self, action: str, event=None):
        """Handle keyboard shortcut action"""
        try:
            if not self.main_window:
                return
            
            # Task Management Actions
            if action == 'new_task':
                self.main_window.show_add_task_dialog()
            elif action == 'new_category':
                self.main_window.show_add_category_dialog()
            elif action == 'duplicate_task':
                self.duplicate_selected_task()
            elif action == 'delete_task':
                self.delete_selected_task()
            elif action == 'edit_task':
                self.edit_selected_task()
            elif action == 'complete_task':
                self.complete_selected_task()
            elif action == 'mark_in_progress':
                self.mark_task_in_progress()
            
            # Navigation Actions
            elif action == 'show_tasks':
                self.main_window.show_tasks()
            elif action == 'show_calendar':
                self.main_window.show_calendar()
            elif action == 'show_goals':
                self.main_window.show_goals()
            elif action == 'show_habits':
                self.main_window.show_habits()
            elif action == 'show_analytics':
                self.main_window.show_analytics()
            elif action == 'show_settings':
                self.main_window.show_settings()
            
            # Search and Filter Actions
            elif action == 'focus_search':
                self.focus_search_box()
            elif action == 'advanced_search':
                self.show_advanced_search()
            elif action == 'refresh_data':
                self.main_window.refresh_data()
            elif action == 'clear_filters':
                self.clear_all_filters()
            
            # Quick Actions
            elif action == 'quick_add_task':
                self.show_quick_add_dialog()
            elif action == 'toggle_sidebar':
                self.toggle_sidebar()
            elif action == 'toggle_dark_mode':
                self.toggle_dark_mode()
            
            # Application Actions
            elif action == 'save_all':
                self.save_all_data()
            elif action == 'quit_app':
                self.quit_application()
            elif action == 'show_help':
                self.main_window.show_help()
            
            # Priority Actions
            elif action.startswith('set_priority_'):
                priority = action.split('_')[-1]
                self.set_selected_task_priority(priority)
            
            print(f"🎹 Executed shortcut: {action}")
            
        except Exception as e:
            print(f"Error handling shortcut '{action}': {e}")
    
    def register_main_window(self, main_window):
        """Register the main window for shortcut actions"""
        self.main_window = main_window
    
    def focus_search_box(self):
        """Focus the search input box"""
        try:
            if hasattr(self.main_window, 'current_frame'):
                current_frame = self.main_window.current_frame
                if hasattr(current_frame, 'search_entry'):
                    current_frame.search_entry.focus()
                    current_frame.search_entry.select_range(0, tk.END)
        except Exception as e:
            print(f"Error focusing search box: {e}")
    
    def show_quick_add_dialog(self):
        """Show quick add task dialog"""
        try:
            if hasattr(self.main_window, 'show_add_task_dialog'):
                self.main_window.show_add_task_dialog()
        except Exception as e:
            print(f"Error showing quick add dialog: {e}")
    
    def toggle_sidebar(self):
        """Toggle sidebar visibility"""
        try:
            if hasattr(self.main_window, 'sidebar'):
                sidebar = self.main_window.sidebar
                if sidebar.winfo_viewable():
                    sidebar.grid_remove()
                else:
                    sidebar.grid()
        except Exception as e:
            print(f"Error toggling sidebar: {e}")
    
    def toggle_dark_mode(self):
        """Toggle between light and dark mode"""
        try:
            from services.theme_manager import theme_manager
            current_theme = theme_manager.current_theme
            new_theme = 'dark' if current_theme == 'light' else 'light'
            theme_manager.apply_theme(new_theme)
            
            # Refresh UI
            if hasattr(self.main_window, 'refresh_theme'):
                self.main_window.refresh_theme()
        except Exception as e:
            print(f"Error toggling dark mode: {e}")
    
    def duplicate_selected_task(self):
        """Duplicate the currently selected task"""
        try:
            current_frame = getattr(self.main_window, 'current_frame', None)
            if hasattr(current_frame, 'duplicate_selected_task'):
                current_frame.duplicate_selected_task()
        except Exception as e:
            print(f"Error duplicating task: {e}")
    
    def delete_selected_task(self):
        """Delete the currently selected task"""
        try:
            current_frame = getattr(self.main_window, 'current_frame', None)
            if hasattr(current_frame, 'delete_selected_task'):
                current_frame.delete_selected_task()
        except Exception as e:
            print(f"Error deleting task: {e}")
    
    def complete_selected_task(self):
        """Mark selected task as completed"""
        try:
            current_frame = getattr(self.main_window, 'current_frame', None)
            if hasattr(current_frame, 'complete_selected_task'):
                current_frame.complete_selected_task()
        except Exception as e:
            print(f"Error completing task: {e}")
    
    def clear_all_filters(self):
        """Clear all active filters"""
        try:
            current_frame = getattr(self.main_window, 'current_frame', None)
            if hasattr(current_frame, 'clear_filters'):
                current_frame.clear_filters()
        except Exception as e:
            print(f"Error clearing filters: {e}")
    
    def save_all_data(self):
        """Save all application data"""
        try:
            if hasattr(self.main_window, 'save_settings'):
                self.main_window.save_settings()
            print("💾 All data saved")
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def quit_application(self):
        """Quit the application safely"""
        try:
            if hasattr(self.main_window, 'root'):
                self.main_window.root.quit()
        except Exception as e:
            print(f"Error quitting application: {e}")
    
    def add_custom_shortcut(self, key_combo: str, action: str):
        """Add a custom keyboard shortcut"""
        try:
            self.shortcuts[key_combo] = action
            self.root.bind(key_combo, lambda event, a=action: self.handle_shortcut(a, event))
            
            # Save to settings
            custom_shortcuts = self.settings.get('keyboard_shortcuts', {})
            custom_shortcuts[key_combo] = action
            self.settings.set('keyboard_shortcuts', custom_shortcuts)
            self.settings.save()
            
            print(f"✅ Added custom shortcut: {key_combo} -> {action}")
        except Exception as e:
            print(f"Error adding custom shortcut: {e}")
    
    def remove_shortcut(self, key_combo: str):
        """Remove a keyboard shortcut"""
        try:
            if key_combo in self.shortcuts:
                del self.shortcuts[key_combo]
                self.root.unbind(key_combo)
                
                # Remove from settings
                custom_shortcuts = self.settings.get('keyboard_shortcuts', {})
                if key_combo in custom_shortcuts:
                    del custom_shortcuts[key_combo]
                    self.settings.set('keyboard_shortcuts', custom_shortcuts)
                    self.settings.save()
                
                print(f"✅ Removed shortcut: {key_combo}")
        except Exception as e:
            print(f"Error removing shortcut: {e}")
    
    def get_shortcuts_help(self) -> str:
        """Get formatted help text for all shortcuts"""
        help_text = "🎹 KEYBOARD SHORTCUTS\n" + "="*50 + "\n\n"
        
        categories = {
            'Task Management': ['new_task', 'duplicate_task', 'delete_task', 'edit_task', 'complete_task'],
            'Navigation': ['show_tasks', 'show_calendar', 'show_goals', 'show_settings'],
            'Search & Filters': ['focus_search', 'refresh_data', 'clear_filters'],
            'Quick Actions': ['quick_add_task', 'toggle_sidebar', 'toggle_dark_mode'],
            'Application': ['save_all', 'quit_app', 'show_help']
        }
        
        for category, actions in categories.items():
            help_text += f"\n{category}:\n" + "-"*len(category) + "\n"
            for action in actions:
                # Find key combo for this action
                key_combo = next((k for k, v in self.shortcuts.items() if v == action), None)
                if key_combo:
                    # Format key combo for display
                    display_key = key_combo.replace('<Control-', 'Ctrl+').replace('<Shift-', 'Shift+').replace('>', '')
                    help_text += f"  {display_key:<20} {action.replace('_', ' ').title()}\n"
        
        return help_text
