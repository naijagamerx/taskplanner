"""
Global Font Manager for Task Planner Application
Manages font sizes across all UI components
"""

import customtkinter as ctk
import json
import os
from typing import Dict, List, Any, Optional

class FontManager:
    """Manages global font settings for the application"""
    
    def __init__(self):
        self.current_font_size = 12
        self.settings_file = "settings.json"
        self.font_observers = []  # Components that need font updates
        self.load_font_settings()
    
    def load_font_settings(self):
        """Load font size from settings file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    self.current_font_size = int(settings.get("font_size", 12))
            else:
                self.current_font_size = 12
        except Exception as e:
            print(f"Error loading font settings: {e}")
            self.current_font_size = 12
    
    def save_font_settings(self):
        """Save font size to settings file"""
        try:
            settings = {}
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
            
            settings["font_size"] = str(self.current_font_size)
            
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            print(f"Error saving font settings: {e}")
    
    def register_observer(self, component):
        """Register a component to receive font updates"""
        if component not in self.font_observers:
            self.font_observers.append(component)
    
    def unregister_observer(self, component):
        """Unregister a component from font updates"""
        if component in self.font_observers:
            self.font_observers.remove(component)
    
    def set_font_size(self, size: int):
        """Set new font size and notify all observers"""
        try:
            self.current_font_size = int(size)
            self.save_font_settings()
            self.notify_observers()
            print(f"Font size changed to {size}px")
        except Exception as e:
            print(f"Error setting font size: {e}")
    
    def get_font_size(self) -> int:
        """Get current font size"""
        return self.current_font_size
    
    def notify_observers(self):
        """Notify all registered components about font size change"""
        for component in self.font_observers[:]:  # Copy list to avoid modification during iteration
            try:
                if hasattr(component, 'update_fonts'):
                    component.update_fonts(self.current_font_size)
                elif hasattr(component, 'refresh_fonts'):
                    component.refresh_fonts(self.current_font_size)
            except Exception as e:
                print(f"Error notifying component about font change: {e}")
                # Remove invalid observers
                self.unregister_observer(component)
    
    def create_font(self, size_offset: int = 0, weight: str = "normal") -> ctk.CTkFont:
        """Create a CTkFont with current size plus offset"""
        return ctk.CTkFont(size=self.current_font_size + size_offset, weight=weight)
    
    def get_scaled_size(self, base_size: int) -> int:
        """Get scaled font size based on current setting"""
        # Scale relative to default size of 12
        scale_factor = self.current_font_size / 12
        return max(8, int(base_size * scale_factor))

# Global font manager instance
font_manager = FontManager()

def get_font_manager() -> FontManager:
    """Get the global font manager instance"""
    return font_manager

def create_font(size_offset: int = 0, weight: str = "normal") -> ctk.CTkFont:
    """Convenience function to create a font with current global size"""
    return font_manager.create_font(size_offset, weight)

def get_current_font_size() -> int:
    """Convenience function to get current font size"""
    return font_manager.get_font_size()

def set_global_font_size(size: int):
    """Convenience function to set global font size"""
    font_manager.set_font_size(size)

def register_for_font_updates(component):
    """Convenience function to register component for font updates"""
    font_manager.register_observer(component)

def unregister_from_font_updates(component):
    """Convenience function to unregister component from font updates"""
    font_manager.unregister_observer(component)
