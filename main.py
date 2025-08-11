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

# Set Application User Model ID for proper Windows notifications (must be done early)
if sys.platform == "win32":
    try:
        import ctypes
        app_id = "TaskPlanner.DesktopApp.1.0"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
        print(f"Application User Model ID set to: {app_id}")
    except Exception as e:
        print(f"Failed to set Application User Model ID: {e}")

# Ensure environment is properly set up
try:
    # Try enhanced startup check first, fallback to basic if needed
    try:
        from startup_check_enhanced import run_startup_check
        # Use silent mode for compiled executables to prevent console flashing
        silent_mode = getattr(sys, 'frozen', False)
        if not run_startup_check(silent=silent_mode):
            if not silent_mode:
                print("Enhanced startup check failed. Exiting...")
            sys.exit(1)
    except ImportError:
        # Fallback to basic startup check
        from startup_check import setup_environment
        if not setup_environment():
            print("Startup check failed. Exiting...")
            sys.exit(1)
except Exception as e:
    print(f"Startup check error: {e}")
    print("Continuing with basic initialization...")

# Special configuration for compiled executables to prevent window flashing
if getattr(sys, 'frozen', False):
    try:
        from compiled_startup import configure_for_compiled
        configure_for_compiled()
    except ImportError:
        pass

# Import CustomTkinter after configuration
import customtkinter as ctk

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
        # Only set if not already configured (for compiled executables)
        if not getattr(sys, 'frozen', False):
            ctk.set_appearance_mode("light")  # "light" or "dark"
            ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"

    def initialize_database(self):
        """Initialize database connection and schema - graceful for distribution"""
        try:
            # Test database connection
            if db_manager.test_connection():
                # Connection successful, initialize schema
                if db_manager.initialize_database():
                    print("Database connected and initialized successfully")
                    # Ensure default data exists
                    self.ensure_default_data()
                    return True
                else:
                    print("Database connected but schema initialization failed")
                    # Try to create schema manually
                    self.ensure_default_data()
                    return True
            else:
                # Connection failed - this is normal for distributed apps
                print("Database connection failed - will show setup dialog")
                return True  # Allow app to start and show database setup dialog

        except Exception as e:
            print(f"Database initialization error: {e}")
            return True  # Allow app to start anyway

    def ensure_default_data(self):
        """Ensure default categories and priorities exist"""
        try:
            from models.category import Category, Priority

            # Check if categories exist
            categories = Category.get_all()
            if not categories:
                # Create default categories
                default_categories = [
                    {'name': 'Work', 'color': '#3498db', 'description': 'Work-related tasks and projects'},
                    {'name': 'Personal', 'color': '#e74c3c', 'description': 'Personal tasks and activities'},
                    {'name': 'Health', 'color': '#2ecc71', 'description': 'Health and fitness related'},
                    {'name': 'Learning', 'color': '#f39c12', 'description': 'Education and skill development'},
                    {'name': 'Finance', 'color': '#9b59b6', 'description': 'Financial planning and management'}
                ]

                for cat_data in default_categories:
                    try:
                        category = Category(
                            name=cat_data['name'],
                            color=cat_data['color'],
                            description=cat_data['description']
                        )
                        category.save()
                        print(f"Created default category: {cat_data['name']}")
                    except Exception as e:
                        print(f"Error creating category {cat_data['name']}: {e}")

            # Check if priorities exist
            priorities = Priority.get_all()
            if not priorities:
                # Create default priorities
                default_priorities = [
                    {'name': 'Low', 'level': 1, 'color': '#95a5a6', 'description': 'Low priority tasks'},
                    {'name': 'Medium', 'level': 2, 'color': '#f39c12', 'description': 'Medium priority tasks'},
                    {'name': 'High', 'level': 3, 'color': '#e74c3c', 'description': 'High priority tasks'},
                    {'name': 'Critical', 'level': 4, 'color': '#8e44ad', 'description': 'Critical priority tasks'}
                ]

                for pri_data in default_priorities:
                    try:
                        priority = Priority(
                            name=pri_data['name'],
                            level=pri_data['level'],
                            color=pri_data['color'],
                            description=pri_data['description']
                        )
                        priority.save()
                        print(f"Created default priority: {pri_data['name']}")
                    except Exception as e:
                        print(f"Error creating priority {pri_data['name']}: {e}")

        except Exception as e:
            print(f"Error ensuring default data: {e}")

    def create_main_window(self):
        """Create and configure main application window"""
        # Check if window already exists (from license activation)
        if self.root is None:
            self.root = ctk.CTk()

        # For compiled executables, keep window hidden until fully configured
        if getattr(sys, 'frozen', False):
            self.root.withdraw()

        # Configure the window
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

        # Apply initial window settings (without immediate maximization)
        self.setup_initial_window()

        # Create main window interface
        self.main_window = MainWindow(self.root)

        # Apply final window state after everything is loaded
        self.root.after(50, self.force_maximize)

        # Configure window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Start periodic license validation
        self.license_validation_id = None
        self.start_license_monitoring()

    def setup_initial_window(self):
        """Setup initial window state without maximization"""
        try:
            # Start with a reasonable default size, centered
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()

            # Use 90% of screen size initially
            window_width = int(screen_width * 0.9)
            window_height = int(screen_height * 0.9)

            # Center the window
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2

            # Set geometry without showing
            self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

            # Don't maximize yet - wait for content to load

        except Exception:
            # Fallback to default size
            self.root.geometry("1200x800+100+100")

    def force_maximize(self):
        """Apply final window state after all content is loaded"""
        try:
            startup_mode = window_config.get_setting("startup_mode", "maximized")
            if startup_mode == "maximized":
                # Ensure all content is rendered first
                self.root.update_idletasks()

                import platform
                system = platform.system().lower()

                if system == "windows":
                    # Use the most reliable Windows maximization method
                    self.root.state('zoomed')
                elif system == "linux":
                    self.root.attributes('-zoomed', True)
                elif system == "darwin":  # macOS
                    self.root.attributes('-zoomed', True)
                else:
                    # Fallback to manual maximization
                    screen_width = self.root.winfo_screenwidth()
                    screen_height = self.root.winfo_screenheight()
                    self.root.geometry(f"{screen_width}x{screen_height}+0+0")

            # For compiled executables, show the window now that it's fully configured
            if getattr(sys, 'frozen', False):
                self.root.deiconify()
                self.root.lift()
                self.root.focus_force()

        except Exception:
            # Keep the current large window size as fallback
            # Still show the window even if maximization failed
            if getattr(sys, 'frozen', False):
                self.root.deiconify()



    def on_closing(self):
        """Handle application closing"""
        try:
            # Cancel license validation
            if self.license_validation_id:
                self.root.after_cancel(self.license_validation_id)
                self.license_validation_id = None

            # Save any pending data and cleanup (stop notifications on app exit)
            if self.main_window:
                self.main_window.save_settings()
                self.main_window.cleanup(stop_notifications=True)

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
            # Check license first before anything else
            if not self.check_license():
                return  # License check failed, exit application

            # Initialize database (graceful - always returns True for distribution)
            self.initialize_database()

            # Create and show main window
            self.create_main_window()

            # Check if database setup is needed after window is created
            self.check_database_setup()

            # Start the main loop
            self.root.mainloop()

        except Exception as e:
            messagebox.showerror(
                "Application Error",
                f"Failed to start Task Planner:\n{str(e)}"
            )
            sys.exit(1)

    def check_license(self):
        """Check license before starting the application"""
        try:
            from auth.license_manager import LicenseManager
            license_manager = LicenseManager()

            # Check if license is valid
            if license_manager.is_license_valid():
                return True

            # For compiled executables, use a different approach to prevent flashing
            if getattr(sys, 'frozen', False):
                # Use the main window as parent for license dialog
                # This prevents creating additional CTk instances
                return self.show_license_with_main_window(license_manager)
            else:
                # Show license activation window with proper window management
                from gui.auth.license_activation_window import LicenseActivationWindow

                # Create temporary root for license window - completely hidden
                temp_root = ctk.CTk()
                temp_root.withdraw()  # Hide the temporary root
                temp_root.attributes('-alpha', 0)  # Make completely transparent
                temp_root.overrideredirect(True)  # Remove window decorations

                # Position off-screen to prevent flashing
                temp_root.geometry("1x1+-1000+-1000")

                license_window = LicenseActivationWindow(temp_root, license_manager)
                result = license_window.show()

                # Clean up properly
                temp_root.quit()
                temp_root.destroy()

                return result

        except Exception as e:
            messagebox.showerror(
                "License Error",
                f"Failed to check license:\n{str(e)}"
            )
            return False

    def show_license_with_main_window(self, license_manager):
        """Show license activation using main window to prevent flashing"""
        try:
            # Create main window first (hidden)
            self.root = ctk.CTk()
            self.root.withdraw()  # Hide initially
            self.root.title("Task Planner - License Activation")

            # Import and show license window using main window as parent
            from gui.auth.license_activation_window import LicenseActivationWindow
            license_window = LicenseActivationWindow(self.root, license_manager)

            # Show the license window
            result = license_window.show()

            if not result:
                # License activation failed, clean up and exit
                self.root.destroy()
                self.root = None
                return False

            # License activated successfully, keep the main window for later use
            return True

        except Exception as e:
            if self.root:
                self.root.destroy()
                self.root = None
            messagebox.showerror("License Error", f"Failed to show license activation: {e}")
            return False

    def check_database_setup(self):
        """Check if database setup dialog should be shown"""
        try:
            # Test if database is properly configured and accessible
            if not db_manager.test_connection():
                # Show database setup dialog
                from gui.database_setup_dialog import show_database_setup

                # Show setup dialog
                if show_database_setup(self.root):
                    # Database configured successfully, refresh the main window
                    if hasattr(self.main_window, 'refresh_data'):
                        self.main_window.refresh_data()
                else:
                    # User cancelled setup, continue with limited functionality
                    messagebox.showinfo(
                        "Database Setup",
                        "Database setup was cancelled.\n\n"
                        "You can configure the database later through the Settings menu.\n"
                        "Some features may be limited until database is configured."
                    )
        except Exception as e:
            print(f"Error checking database setup: {e}")
            # Continue running even if setup check fails

    def start_license_monitoring(self):
        """Start periodic license validation to catch revoked licenses"""
        self.validate_license_periodically()

    def validate_license_periodically(self):
        """Validate license periodically and handle revoked licenses"""
        try:
            from auth.license_manager import LicenseManager
            license_manager = LicenseManager()

            # Check if current license is still valid
            if not license_manager.is_license_valid():
                # License is no longer valid (could be revoked, expired, etc.)
                print("License validation failed - showing activation window")

                # Show license activation window
                from gui.auth.license_activation_window import LicenseActivationWindow

                license_window = LicenseActivationWindow(self.root, license_manager)
                result = license_window.show()

                if not result:
                    # User cancelled or failed to activate - close app
                    messagebox.showwarning(
                        "License Required",
                        "A valid license is required to continue using Task Planner.\n\n"
                        "The application will now close."
                    )
                    self.on_closing()
                    return
                else:
                    # License reactivated successfully
                    print("License reactivated successfully")
                    # Update license status in main window
                    if hasattr(self.main_window, 'update_license_status'):
                        self.main_window.update_license_status()

        except Exception as e:
            print(f"Error during periodic license validation: {e}")

        # Schedule next validation in 5 minutes (only if window still exists)
        try:
            if self.root and self.root.winfo_exists():
                self.license_validation_id = self.root.after(300000, self.validate_license_periodically)
        except tk.TclError:
            # Window has been destroyed, stop scheduling
            pass


def main():
    """Main entry point"""
    try:
        # Run file migration to AppData (for compiled executables)
        if getattr(sys, 'frozen', False):
            try:
                from utils.file_migration import run_migration
                run_migration()
            except Exception as e:
                print(f"File migration warning: {e}")

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
