"""
Task Planner - Main Application Entry Point
A comprehensive desktop task planning application
"""

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import db_manager
from gui.main_window import MainWindow
from config.window_config import window_config

class TaskPlannerApp:
    """Main application class"""

    def __init__(self):
        self.root = None
        self.main_window = None
        self.setup_customtkinter()

    def setup_customtkinter(self):
        """Configure CustomTkinter appearance"""
        ctk.set_appearance_mode("light")  # "light" or "dark"
        ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"

    def initialize_database(self):
        """Initialize database connection and schema"""
        try:
            # Test database connection
            if not db_manager.test_connection():
                messagebox.showerror(
                    "Database Error",
                    "Could not connect to MySQL database.\n\n"
                    "Please ensure:\n"
                    "1. MySQL server is running\n"
                    "2. Database credentials are correct\n"
                    "3. Database 'task_planner' exists or can be created"
                )
                return False

            # Initialize database schema
            if not db_manager.initialize_database():
                messagebox.showerror(
                    "Database Error",
                    "Could not initialize database schema.\n"
                    "Please check database permissions."
                )
                return False

            return True

        except Exception as e:
            messagebox.showerror(
                "Database Error",
                f"Database initialization failed:\n{str(e)}"
            )
            return False

    def create_main_window(self):
        """Create and configure main application window"""
        self.root = ctk.CTk()
        self.root.title("Task Planner - Comprehensive Life Planning")
        # Set application icon
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "assets", "icons", "app_icon.png")
            if os.path.exists(icon_path):
                self.root.iconphoto(True, tk.PhotoImage(file=icon_path))
            else:
                # Fallback to ICO format
                ico_path = os.path.join(os.path.dirname(__file__), "assets", "icons", "favicon.ico")
                if os.path.exists(ico_path):
                    self.root.iconbitmap(ico_path)
        except Exception as e:
            print(f"Could not set application icon: {e}")

        # Set minimum size
        self.root.minsize(800, 600)

        # Center and maximize window on screen
        self.center_and_maximize_window()

        # Create main window interface
        self.main_window = MainWindow(self.root)

        # Configure window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def center_and_maximize_window(self):
        """Center and maximize the main window on screen using window config"""
        # Apply window settings from configuration
        window_config.apply_window_settings(self.root)

    def on_closing(self):
        """Handle application closing"""
        try:
            # Save any pending data
            if self.main_window:
                self.main_window.save_settings()

            # Close database connection
            db_manager.disconnect()

            # Destroy window
            self.root.destroy()

        except Exception as e:
            print(f"Error during application shutdown: {e}")
        finally:
            sys.exit(0)

    def run(self):
        """Run the application"""
        try:
            # Initialize database first
            if not self.initialize_database():
                messagebox.showerror(
                    "Database Error",
                    "Failed to initialize database. Please check your MySQL connection."
                )
                sys.exit(1)

            # Create and show main window directly
            self.create_main_window()
            self.root.mainloop()

        except Exception as e:
            messagebox.showerror(
                "Application Error",
                f"Failed to start Task Planner:\n{str(e)}"
            )
            sys.exit(1)



def main():
    """Main entry point"""
    try:
        app = TaskPlannerApp()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
