#!/usr/bin/env python3
"""
Enhanced Theme Manager for Task Planner
Provides comprehensive theme management with custom color schemes
"""

import customtkinter as ctk
from typing import Dict, Any, Optional
from database.settings_manager import SettingsManager

class ThemeManager:
    """Enhanced theme management system"""
    
    def __init__(self):
        self.settings = SettingsManager()
        self.current_theme = self.settings.get('theme', 'light')
        self.current_color_scheme = self.settings.get('color_scheme', 'blue')
        
        # Define custom color schemes
        self.color_schemes = {
            'blue': {
                'primary': '#1f538d',
                'primary_hover': '#14375e',
                'secondary': '#2b7cd6',
                'accent': '#3b82f6',
                'success': '#10b981',
                'warning': '#f59e0b',
                'error': '#ef4444',
                'info': '#3b82f6'
            },
            'green': {
                'primary': '#059669',
                'primary_hover': '#047857',
                'secondary': '#10b981',
                'accent': '#34d399',
                'success': '#10b981',
                'warning': '#f59e0b',
                'error': '#ef4444',
                'info': '#06b6d4'
            },
            'purple': {
                'primary': '#7c3aed',
                'primary_hover': '#5b21b6',
                'secondary': '#8b5cf6',
                'accent': '#a78bfa',
                'success': '#10b981',
                'warning': '#f59e0b',
                'error': '#ef4444',
                'info': '#3b82f6'
            },
            'orange': {
                'primary': '#ea580c',
                'primary_hover': '#c2410c',
                'secondary': '#f97316',
                'accent': '#fb923c',
                'success': '#10b981',
                'warning': '#f59e0b',
                'error': '#ef4444',
                'info': '#3b82f6'
            },
            'dark_blue': {
                'primary': '#1e293b',
                'primary_hover': '#0f172a',
                'secondary': '#334155',
                'accent': '#64748b',
                'success': '#10b981',
                'warning': '#f59e0b',
                'error': '#ef4444',
                'info': '#3b82f6'
            }
        }
        
        # Enhanced theme definitions
        self.themes = {
            'light': {
                'appearance_mode': 'light',
                'bg_color': '#f8fafc',
                'fg_color': '#ffffff',
                'text_color': '#1e293b',
                'text_color_secondary': '#64748b',
                'border_color': '#e2e8f0',
                'hover_color': '#f1f5f9',
                'selected_color': '#e0f2fe',
                'sidebar_color': '#f8fafc',
                'card_color': '#ffffff',
                'shadow_color': '#00000010'
            },
            'dark': {
                'appearance_mode': 'dark',
                'bg_color': '#0f172a',
                'fg_color': '#1e293b',
                'text_color': '#f8fafc',
                'text_color_secondary': '#94a3b8',
                'border_color': '#334155',
                'hover_color': '#334155',
                'selected_color': '#1e40af',
                'sidebar_color': '#1e293b',
                'card_color': '#334155',
                'shadow_color': '#00000030'
            },
            'auto': {
                'appearance_mode': 'system',
                'bg_color': 'default',
                'fg_color': 'default',
                'text_color': 'default',
                'text_color_secondary': 'default',
                'border_color': 'default',
                'hover_color': 'default',
                'selected_color': 'default',
                'sidebar_color': 'default',
                'card_color': 'default',
                'shadow_color': 'default'
            }
        }
    
    def apply_theme(self, theme_name: str, color_scheme: str = None) -> bool:
        """Apply a theme with optional color scheme"""
        try:
            if theme_name not in self.themes:
                print(f"Unknown theme: {theme_name}")
                return False
            
            # Set appearance mode
            theme_config = self.themes[theme_name]
            ctk.set_appearance_mode(theme_config['appearance_mode'])
            
            # Set color scheme if provided
            if color_scheme and color_scheme in self.color_schemes:
                self.current_color_scheme = color_scheme
                self.settings.set('color_scheme', color_scheme)
            
            # Store theme preference
            self.current_theme = theme_name
            self.settings.set('theme', theme_name)
            self.settings.save()
            
            print(f"Applied theme: {theme_name} with color scheme: {self.current_color_scheme}")
            return True
            
        except Exception as e:
            print(f"Error applying theme: {e}")
            return False
    
    def get_color(self, color_type: str) -> str:
        """Get color value for current theme and color scheme"""
        try:
            # First try to get from color scheme
            if color_type in self.color_schemes[self.current_color_scheme]:
                return self.color_schemes[self.current_color_scheme][color_type]
            
            # Then try to get from theme
            if color_type in self.themes[self.current_theme]:
                return self.themes[self.current_theme][color_type]
            
            # Return default
            return '#3b82f6'
            
        except Exception:
            return '#3b82f6'
    
    def get_theme_colors(self) -> Dict[str, str]:
        """Get all colors for current theme"""
        colors = {}
        
        # Add theme colors
        colors.update(self.themes[self.current_theme])
        
        # Add color scheme colors
        colors.update(self.color_schemes[self.current_color_scheme])
        
        return colors
    
    def get_available_themes(self) -> list:
        """Get list of available themes"""
        return list(self.themes.keys())
    
    def get_available_color_schemes(self) -> list:
        """Get list of available color schemes"""
        return list(self.color_schemes.keys())
    
    def is_dark_mode(self) -> bool:
        """Check if current theme is dark mode"""
        return self.current_theme == 'dark' or (
            self.current_theme == 'auto' and 
            ctk.get_appearance_mode() == 'Dark'
        )
    
    def get_priority_colors(self) -> Dict[str, str]:
        """Get priority-specific colors"""
        if self.is_dark_mode():
            return {
                'low': '#10b981',      # Green
                'medium': '#f59e0b',   # Yellow
                'high': '#f97316',     # Orange  
                'critical': '#ef4444'  # Red
            }
        else:
            return {
                'low': '#059669',      # Green
                'medium': '#d97706',   # Yellow
                'high': '#ea580c',     # Orange
                'critical': '#dc2626'  # Red
            }
    
    def get_category_colors(self) -> list:
        """Get predefined category colors"""
        if self.is_dark_mode():
            return [
                '#3b82f6', '#10b981', '#f59e0b', '#ef4444',
                '#8b5cf6', '#06b6d4', '#f97316', '#ec4899',
                '#84cc16', '#6366f1', '#14b8a6', '#f43f5e'
            ]
        else:
            return [
                '#2563eb', '#059669', '#d97706', '#dc2626',
                '#7c3aed', '#0891b2', '#ea580c', '#db2777',
                '#65a30d', '#4f46e5', '#0d9488', '#e11d48'
            ]
    
    def create_styled_button(self, parent, text: str, command=None, 
                           style: str = 'primary', **kwargs) -> ctk.CTkButton:
        """Create a styled button with theme colors"""
        colors = self.get_theme_colors()
        
        style_configs = {
            'primary': {
                'fg_color': self.get_color('primary'),
                'hover_color': self.get_color('primary_hover'),
                'text_color': '#ffffff'
            },
            'secondary': {
                'fg_color': self.get_color('secondary'),
                'hover_color': self.get_color('primary_hover'),
                'text_color': '#ffffff'
            },
            'success': {
                'fg_color': self.get_color('success'),
                'hover_color': '#059669',
                'text_color': '#ffffff'
            },
            'warning': {
                'fg_color': self.get_color('warning'),
                'hover_color': '#d97706',
                'text_color': '#ffffff'
            },
            'error': {
                'fg_color': self.get_color('error'),
                'hover_color': '#dc2626',
                'text_color': '#ffffff'
            }
        }
        
        config = style_configs.get(style, style_configs['primary'])
        config.update(kwargs)
        
        return ctk.CTkButton(parent, text=text, command=command, **config)

# Global theme manager instance
theme_manager = ThemeManager()
