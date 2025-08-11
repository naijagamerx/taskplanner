"""
Special startup configuration for compiled executables
Prevents window flashing by pre-configuring CustomTkinter
"""

import sys
import os

def configure_for_compiled():
    """Configure environment specifically for compiled executables"""
    if not getattr(sys, 'frozen', False):
        return  # Only for compiled executables
    
    try:
        # Set environment variables to prevent CustomTkinter from creating test windows
        os.environ['CTK_DISABLE_DPI_AWARENESS'] = '1'
        os.environ['CTK_DISABLE_THEME_DETECTION'] = '1'
        
        # Import and configure CustomTkinter immediately
        import customtkinter as ctk
        
        # Set appearance mode before any window creation
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Disable automatic DPI awareness that can cause window creation
        try:
            ctk.deactivate_automatic_dpi_awareness()
        except:
            pass  # Method might not exist in all versions
        
        # Pre-configure scaling to prevent detection windows
        try:
            ctk.set_widget_scaling(1.0)
            ctk.set_window_scaling(1.0)
        except:
            pass
            
        return True
        
    except Exception as e:
        print(f"Warning: Could not configure compiled startup: {e}")
        return False

def setup_compiled_environment():
    """Setup environment for compiled executable"""
    try:
        # Get executable directory
        if getattr(sys, 'frozen', False):
            exe_dir = os.path.dirname(sys.executable)
            
            # Add to Python path
            if exe_dir not in sys.path:
                sys.path.insert(0, exe_dir)
            
            # Set working directory
            os.chdir(exe_dir)
            
            return True
    except Exception:
        return False

# Auto-configure when imported
if __name__ != "__main__":
    configure_for_compiled()
    setup_compiled_environment()
