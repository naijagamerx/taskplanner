"""
Simple Task Planner starter without splash screen
"""

import tkinter as tk
import customtkinter as ctk
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def start_task_planner():
    """Start Task Planner with simplified initialization"""

    # Set CustomTkinter appearance
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    # Test database connection first
    try:
        from database.db_manager import db_manager
        print("Testing database connection...")

        if not db_manager.test_connection():
            print("Database connection failed!")
            # Show error dialog
            root = tk.Tk()
            root.withdraw()
            tk.messagebox.showerror(
                "Database Error",
                "Could not connect to MySQL database.\n\nPlease ensure:\n1. MySQL server is running\n2. Database 'task_planner' exists"
            )
            root.destroy()
            return

        print("Database connection successful!")

        # Initialize database schema
        db_manager.initialize_database()
        print("Database schema initialized!")

    except Exception as e:
        print(f"Database error: {e}")
        root = tk.Tk()
        root.withdraw()
        tk.messagebox.showerror("Error", f"Database initialization failed:\n{e}")
        root.destroy()
        return

    # Create main window directly
    try:
        print("Creating main window...")

        # Create main window
        root = ctk.CTk()
        root.title("Task Planner - Comprehensive Life Planning")
        root.minsize(800, 600)

        # Center and maximize window
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Calculate window size (90% of screen for better appearance)
        window_width = int(screen_width * 0.9)
        window_height = int(screen_height * 0.9)

        # Calculate position to center the window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        # Set window geometry (centered and large)
        root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Ensure window appears on top and gets focus
        root.lift()
        root.focus_force()
        root.attributes('-topmost', True)
        root.after(100, lambda: root.attributes('-topmost', False))

        print("Loading main interface...")

        # Import and create main window interface
        from gui.main_window import MainWindow
        main_window = MainWindow(root)

        print("Task Planner window should now be visible!")
        print("Window title: 'Task Planner - Comprehensive Life Planning'")

        # Handle window close
        def on_closing():
            try:
                main_window.save_settings()
                db_manager.disconnect()
            except:
                pass
            root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_closing)

        # Start the main loop
        root.mainloop()

    except Exception as e:
        print(f"GUI Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 Starting Task Planner")
    print("=" * 50)

    start_task_planner()

    print("👋 Task Planner closed")
