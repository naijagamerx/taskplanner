"""
Window configuration for Task Planner application
Handles window positioning, sizing, and startup behavior
"""

import json
import os

class WindowConfig:
    """Window configuration manager"""

    def __init__(self):
        self.config_file = self._get_config_file_path()
        self.default_config = {
            "startup_mode": "maximized",  # Options: "centered_large", "maximized", "custom"
            "window_width": 1200,
            "window_height": 800,
            "center_on_startup": True,
            "remember_position": False,
            "remember_size": False,
            "always_on_top_startup": True,
            "focus_on_startup": True,
            "screen_percentage": 0.9  # For centered_large mode
        }
        self.config = self.load_config()

    def _get_config_file_path(self) -> str:
        """Get the path for window settings in AppData directory"""
        import sys

        if sys.platform == "win32":
            # Windows: %APPDATA%/TaskPlanner/window_settings.json
            app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
            app_dir = os.path.join(app_data, 'TaskPlanner')
        elif sys.platform == "darwin":
            # macOS: ~/Library/Application Support/TaskPlanner/window_settings.json
            app_dir = os.path.expanduser('~/Library/Application Support/TaskPlanner')
        else:
            # Linux: ~/.config/TaskPlanner/window_settings.json
            config_dir = os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
            app_dir = os.path.join(config_dir, 'TaskPlanner')

        # Create directory if it doesn't exist
        os.makedirs(app_dir, exist_ok=True)
        return os.path.join(app_dir, 'window_settings.json')

    def load_config(self):
        """Load window configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    merged_config = self.default_config.copy()
                    merged_config.update(config)
                    return merged_config
            else:
                return self.default_config.copy()
        except Exception as e:
            print(f"Error loading window config: {e}")
            return self.default_config.copy()

    def save_config(self):
        """Save window configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving window config: {e}")
            return False

    def get_window_geometry(self, root):
        """Calculate window geometry based on configuration"""
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        startup_mode = self.config.get("startup_mode", "centered_large")

        if startup_mode == "maximized":
            # Return None to indicate maximized state should be used
            return None

        elif startup_mode == "centered_large":
            # Calculate large centered window
            percentage = self.config.get("screen_percentage", 0.9)
            window_width = int(screen_width * percentage)
            window_height = int(screen_height * percentage)

            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2

            return f"{window_width}x{window_height}+{x}+{y}"

        elif startup_mode == "custom":
            # Use custom dimensions
            window_width = self.config.get("window_width", 1200)
            window_height = self.config.get("window_height", 800)

            if self.config.get("center_on_startup", True):
                x = (screen_width - window_width) // 2
                y = (screen_height - window_height) // 2
            else:
                x = 100  # Default offset from top-left
                y = 100

            return f"{window_width}x{window_height}+{x}+{y}"

        else:
            # Fallback to default
            return "1200x800+100+100"

    def apply_window_settings(self, root):
        """Apply all window settings to the root window"""
        # Set minimum size
        root.minsize(800, 600)

        # Get startup mode
        startup_mode = self.config.get("startup_mode", "maximized")

        if startup_mode == "maximized":
            # Maximized mode - don't apply here, let main.py handle it
            # This prevents multiple maximization attempts that cause flashing
            pass

        else:
            # Non-maximized modes - set geometry immediately
            geometry = self.get_window_geometry(root)
            if geometry:
                root.geometry(geometry)

        # Apply focus and visibility settings
        if self.config.get("focus_on_startup", True):
            root.lift()
            root.focus_force()

        if self.config.get("always_on_top_startup", True):
            root.attributes('-topmost', True)
            # Remove topmost after a short delay
            root.after(200, lambda: root.attributes('-topmost', False))

    def update_setting(self, key, value):
        """Update a specific setting"""
        self.config[key] = value
        return self.save_config()

    def get_setting(self, key, default=None):
        """Get a specific setting"""
        return self.config.get(key, default)

    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self.config = self.default_config.copy()
        return self.save_config()

# Global window config instance
window_config = WindowConfig()
