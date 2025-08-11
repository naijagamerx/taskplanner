"""
Window configuration for Task Planner application
Handles window positioning, sizing, and startup behavior
"""

import json
import os

class WindowConfig:
    """Window configuration manager"""
    
    def __init__(self):
        self.config_file = "window_settings.json"
        self.default_config = {
            "startup_mode": "centered_large",  # Options: "centered_large", "maximized", "custom"
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
        
        # Get geometry
        geometry = self.get_window_geometry(root)
        
        if geometry is None:
            # Maximized mode
            try:
                # Try different maximization methods for different platforms
                import platform
                system = platform.system().lower()
                
                if system == "windows":
                    root.state('zoomed')
                elif system == "linux":
                    root.attributes('-zoomed', True)
                elif system == "darwin":  # macOS
                    root.attributes('-zoomed', True)
                else:
                    # Fallback to manual maximization
                    screen_width = root.winfo_screenwidth()
                    screen_height = root.winfo_screenheight()
                    root.geometry(f"{screen_width}x{screen_height}+0+0")
            except Exception as e:
                print(f"Could not maximize window: {e}")
                # Fallback to large centered window
                geometry = self.get_window_geometry(root)
                root.geometry(geometry)
        else:
            # Set specific geometry
            root.geometry(geometry)
        
        # Apply focus and visibility settings
        if self.config.get("focus_on_startup", True):
            root.lift()
            root.focus_force()
        
        if self.config.get("always_on_top_startup", True):
            root.attributes('-topmost', True)
            # Remove topmost after a short delay
            root.after(100, lambda: root.attributes('-topmost', False))
    
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
