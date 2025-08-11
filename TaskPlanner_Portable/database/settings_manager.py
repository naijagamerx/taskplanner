"""
Settings Manager for Task Planner
Handles application settings storage and retrieval
"""

import json
import os
import sys
from typing import Any, Dict, Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class SettingsManager:
    """Manages application settings"""
    
    def __init__(self, settings_file: str = None):
        if settings_file is None:
            # Default settings file in user's app data directory
            app_data_dir = self.get_app_data_directory()
            os.makedirs(app_data_dir, exist_ok=True)
            self.settings_file = os.path.join(app_data_dir, 'settings.json')
        else:
            self.settings_file = settings_file
            
        self.settings = {}
        self.load_settings()
    
    def get_app_data_directory(self) -> str:
        """Get application data directory"""
        if sys.platform == "win32":
            # Windows: %APPDATA%/TaskPlanner
            app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
            return os.path.join(app_data, 'TaskPlanner')
        elif sys.platform == "darwin":
            # macOS: ~/Library/Application Support/TaskPlanner
            return os.path.expanduser('~/Library/Application Support/TaskPlanner')
        else:
            # Linux: ~/.config/TaskPlanner
            config_dir = os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
            return os.path.join(config_dir, 'TaskPlanner')
    
    def load_settings(self):
        """Load settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
            else:
                # Create default settings
                self.settings = self.get_default_settings()
                self.save_settings()
        except Exception as e:
            print(f"Error loading settings: {e}")
            self.settings = self.get_default_settings()
    
    def save_settings(self):
        """Save settings to file"""
        try:
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def get_default_settings(self) -> Dict[str, Any]:
        """Get default application settings"""
        return {
            # Notification settings
            'desktop_notifications_enabled': True,
            'sound_alerts_enabled': True,
            'reminder_minutes_before': 15,
            'notification_sound': 'default',
            'notification_check_interval': 60,
            
            # UI settings
            'theme': 'light',
            'window_maximized': True,
            'window_width': 1200,
            'window_height': 800,
            'sidebar_width': 250,
            
            # Task settings
            'default_task_priority': 'medium',
            'auto_mark_overdue': True,
            'show_completed_tasks': True,
            'task_sort_order': 'due_date',
            
            # Calendar settings
            'default_calendar_view': 'month',
            'week_starts_on': 'monday',
            'show_weekends': True,
            
            # Backup settings
            'auto_backup_enabled': True,
            'backup_frequency_days': 7,
            'max_backup_files': 10,
            
            # Advanced settings
            'debug_mode': False,
            'check_for_updates': True,
            'send_usage_statistics': False
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get setting value"""
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set setting value"""
        self.settings[key] = value
    
    def save(self):
        """Save current settings"""
        self.save_settings()
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        self.settings = self.get_default_settings()
        self.save_settings()
    
    def get_notification_settings(self) -> Dict[str, Any]:
        """Get all notification-related settings"""
        return {
            'desktop_notifications_enabled': self.get('desktop_notifications_enabled', True),
            'sound_alerts_enabled': self.get('sound_alerts_enabled', True),
            'reminder_minutes_before': self.get('reminder_minutes_before', 15),
            'notification_sound': self.get('notification_sound', 'default'),
            'notification_check_interval': self.get('notification_check_interval', 60)
        }
    
    def update_notification_settings(self, settings: Dict[str, Any]):
        """Update notification settings"""
        for key, value in settings.items():
            if key in ['desktop_notifications_enabled', 'sound_alerts_enabled', 
                      'reminder_minutes_before', 'notification_sound', 'notification_check_interval']:
                self.set(key, value)
        self.save_settings()
    
    def get_ui_settings(self) -> Dict[str, Any]:
        """Get all UI-related settings"""
        return {
            'theme': self.get('theme', 'light'),
            'window_maximized': self.get('window_maximized', True),
            'window_width': self.get('window_width', 1200),
            'window_height': self.get('window_height', 800),
            'sidebar_width': self.get('sidebar_width', 250)
        }
    
    def update_ui_settings(self, settings: Dict[str, Any]):
        """Update UI settings"""
        for key, value in settings.items():
            if key in ['theme', 'window_maximized', 'window_width', 'window_height', 'sidebar_width']:
                self.set(key, value)
        self.save_settings()
    
    def export_settings(self, file_path: str):
        """Export settings to file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error exporting settings: {e}")
            return False
    
    def import_settings(self, file_path: str):
        """Import settings from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_settings = json.load(f)
            
            # Validate and merge settings
            default_settings = self.get_default_settings()
            for key, value in imported_settings.items():
                if key in default_settings:
                    self.settings[key] = value
            
            self.save_settings()
            return True
        except Exception as e:
            print(f"Error importing settings: {e}")
            return False
