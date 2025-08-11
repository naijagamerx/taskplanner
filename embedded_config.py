"""
Embedded configuration for compiled Task Planner
This file contains all configuration data to avoid exposing JSON files
"""

EMBEDDED_CONFIGS = {'db_config': {'type': 'sqlite', 'database': 'data/task_planner.db'}, 'settings': {'theme': 'dark', 'color_theme': 'green', 'font_size': '15', 'default_reminder_time': '15', 'work_hours_start': '09:00', 'work_hours_end': '17:00', 'date_format': '%Y-%m-%d', 'autosave_interval': '5'}}

def get_config(config_name):
    """Get embedded configuration"""
    return EMBEDDED_CONFIGS.get(config_name, {})

def has_config(config_name):
    """Check if configuration exists"""
    return config_name in EMBEDDED_CONFIGS
