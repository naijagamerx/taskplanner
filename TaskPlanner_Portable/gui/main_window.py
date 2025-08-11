"""
Main window interface for Task Planner application
"""

from tkinter import messagebox
import customtkinter as ctk
from datetime import date
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.task_manager import TaskManagerFrame
from gui.calendar_view import CalendarFrame
from gui.analytics import AnalyticsFrame
from gui.settings import SettingsFrame
from gui.dialogs.help_dialog import HelpDialog
from models.task import Task
from models.category import Category, Priority

# Import notification manager
try:
    from services.notification_manager import notification_manager
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False
    notification_manager = None

class MainWindow:
    """Main application window"""

    def __init__(self, root):
        self.root = root
        self.current_frame = None
        self.setup_ui()
        self.load_initial_data()

    def setup_ui(self):
        """Setup main window UI"""
        # Configure grid weights
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # Create sidebar
        self.create_sidebar()

        # Create main content area
        self.create_main_content()

        # Initialize notifications
        self.init_notifications()

        # Show default view
        self.show_tasks()

    def create_sidebar(self):
        """Create navigation sidebar"""
        self.sidebar = ctk.CTkFrame(self.root, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 2))
        self.sidebar.grid_rowconfigure(6, weight=1)  # Spacer

        # App title and welcome
        title_label = ctk.CTkLabel(
            self.sidebar,
            text="Task Planner",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Stylish welcome badge
        welcome_frame = ctk.CTkFrame(self.sidebar, fg_color=("gray90", "gray20"), corner_radius=15)
        welcome_frame.grid(row=0, column=0, padx=20, pady=(50, 15), sticky="ew")

        welcome_label = ctk.CTkLabel(
            welcome_frame,
            text="✨ Task Planner",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("gray20", "gray80")
        )
        welcome_label.pack(pady=(8, 2))

        tagline_label = ctk.CTkLabel(
            welcome_frame,
            text="Stay organized, stay productive",
            font=ctk.CTkFont(size=10),
            text_color=("gray40", "gray60")
        )
        tagline_label.pack(pady=(0, 8))

        # Navigation buttons
        self.nav_buttons = {}

        # Navigation section header
        nav_header = ctk.CTkLabel(
            self.sidebar,
            text="Navigation",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="gray"
        )
        nav_header.grid(row=1, column=0, padx=20, pady=(10, 5), sticky="w")

        # Tasks button
        self.nav_buttons['tasks'] = ctk.CTkButton(
            self.sidebar,
            text="📋 Tasks",
            command=self.show_tasks,
            height=40,
            font=ctk.CTkFont(size=14),
            text_color=("black", "white")
        )
        self.nav_buttons['tasks'].grid(row=2, column=0, padx=20, pady=5, sticky="ew")

        # Calendar button
        self.nav_buttons['calendar'] = ctk.CTkButton(
            self.sidebar,
            text="📅 Calendar",
            command=self.show_calendar,
            height=40,
            font=ctk.CTkFont(size=14),
            text_color=("black", "white")
        )
        self.nav_buttons['calendar'].grid(row=3, column=0, padx=20, pady=5, sticky="ew")

        # Analytics button
        self.nav_buttons['analytics'] = ctk.CTkButton(
            self.sidebar,
            text="📊 Analytics",
            command=self.show_analytics,
            height=40,
            font=ctk.CTkFont(size=14),
            text_color=("black", "white")
        )
        self.nav_buttons['analytics'].grid(row=4, column=0, padx=20, pady=5, sticky="ew")

        # Settings button
        self.nav_buttons['settings'] = ctk.CTkButton(
            self.sidebar,
            text="⚙️ Settings",
            command=self.show_settings,
            height=40,
            font=ctk.CTkFont(size=14),
            text_color=("black", "white")
        )
        self.nav_buttons['settings'].grid(row=5, column=0, padx=20, pady=5, sticky="ew")

        # Quick stats section
        self.create_quick_stats()

        # Quick actions section
        self.create_quick_actions()

    def create_quick_stats(self):
        """Create quick statistics display"""
        stats_frame = ctk.CTkFrame(self.sidebar)
        stats_frame.grid(row=7, column=0, padx=20, pady=(20, 10), sticky="ew")

        stats_title = ctk.CTkLabel(
            stats_frame,
            text="📈 Quick Stats",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        stats_title.pack(pady=(10, 10))

        # Today's tasks
        self.today_tasks_label = ctk.CTkLabel(
            stats_frame,
            text="Today: 0 tasks",
            font=ctk.CTkFont(size=12)
        )
        self.today_tasks_label.pack(pady=2)

        # Pending tasks
        self.pending_tasks_label = ctk.CTkLabel(
            stats_frame,
            text="Pending: 0 tasks",
            font=ctk.CTkFont(size=12)
        )
        self.pending_tasks_label.pack(pady=2)

        # Overdue tasks
        self.overdue_tasks_label = ctk.CTkLabel(
            stats_frame,
            text="Overdue: 0 tasks",
            font=ctk.CTkFont(size=12),
            text_color="red"
        )
        self.overdue_tasks_label.pack(pady=(2, 10))

    def create_quick_actions(self):
        """Create quick action buttons"""
        actions_frame = ctk.CTkFrame(self.sidebar)
        actions_frame.grid(row=8, column=0, padx=20, pady=10, sticky="ew")

        actions_title = ctk.CTkLabel(
            actions_frame,
            text="⚡ Quick Actions",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        actions_title.pack(pady=(10, 10))

        # Add task button
        add_task_btn = ctk.CTkButton(
            actions_frame,
            text="+ Add Task",
            command=self.quick_add_task,
            height=30,
            font=ctk.CTkFont(size=12)
        )
        add_task_btn.pack(pady=5, padx=10, fill="x")

        # Add goal button
        add_goal_btn = ctk.CTkButton(
            actions_frame,
            text="+ Add Goal",
            command=self.quick_add_goal,
            height=30,
            font=ctk.CTkFont(size=12)
        )
        add_goal_btn.pack(pady=5, padx=10, fill="x")

        # Help button
        help_btn = ctk.CTkButton(
            actions_frame,
            text="❓ Help & Tips",
            command=self.show_help,
            height=30,
            font=ctk.CTkFont(size=12),
            fg_color="gray",
            hover_color="darkgray"
        )
        help_btn.pack(pady=(5, 10), padx=10, fill="x")

    def create_main_content(self):
        """Create main content area"""
        self.main_content = ctk.CTkFrame(self.root, corner_radius=0)
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=(2, 0))
        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_rowconfigure(0, weight=1)

    def clear_main_content(self):
        """Clear main content area"""
        for widget in self.main_content.winfo_children():
            widget.destroy()

    def update_nav_buttons(self, active_button):
        """Update navigation button states"""
        for name, button in self.nav_buttons.items():
            if name == active_button:
                button.configure(fg_color=("gray75", "gray25"))
            else:
                button.configure(fg_color=("gray85", "gray15"))

    def show_tasks(self):
        """Show tasks management view"""
        self.clear_main_content()
        self.update_nav_buttons('tasks')

        self.current_frame = TaskManagerFrame(self.main_content, self)
        self.current_frame.pack(fill="both", expand=True)

        self.update_quick_stats()

    def show_calendar(self):
        """Show calendar view"""
        self.clear_main_content()
        self.update_nav_buttons('calendar')

        self.current_frame = CalendarFrame(self.main_content, self)
        self.current_frame.pack(fill="both", expand=True)

    def show_analytics(self):
        """Show analytics view"""
        self.clear_main_content()
        self.update_nav_buttons('analytics')

        self.current_frame = AnalyticsFrame(self.main_content, self)
        self.current_frame.pack(fill="both", expand=True)

    def show_settings(self):
        """Show settings view"""
        self.clear_main_content()
        self.update_nav_buttons('settings')

        self.current_frame = SettingsFrame(self.main_content, self)
        self.current_frame.pack(fill="both", expand=True)

    def quick_add_task(self):
        """Quick add task dialog"""
        if hasattr(self.current_frame, 'show_add_task_dialog'):
            self.current_frame.show_add_task_dialog()
        else:
            # If not in tasks view, switch to it first
            self.show_tasks()
            if hasattr(self.current_frame, 'show_add_task_dialog'):
                self.current_frame.show_add_task_dialog()

    def quick_add_goal(self):
        """Quick add goal dialog"""
        if hasattr(self.current_frame, 'show_add_goal_dialog'):
            self.current_frame.show_add_goal_dialog()
        else:
            messagebox.showinfo("Info", "Goal creation will be available in the next update!")

    def show_help(self):
        """Show help and instructions dialog"""
        HelpDialog(self.root)

    def update_quick_stats(self):
        """Update quick statistics in sidebar"""
        try:
            # Get today's tasks
            today = date.today()
            today_tasks = Task.get_by_date_range(today, today)

            # Get pending tasks
            pending_tasks = Task.get_by_status('pending')

            # Get overdue tasks
            overdue_tasks = Task.get_overdue()

            # Update labels
            self.today_tasks_label.configure(text=f"Today: {len(today_tasks)} tasks")
            self.pending_tasks_label.configure(text=f"Pending: {len(pending_tasks)} tasks")
            self.overdue_tasks_label.configure(text=f"Overdue: {len(overdue_tasks)} tasks")

        except Exception as e:
            print(f"Error updating quick stats: {e}")

    def init_notifications(self):
        """Initialize notification system"""
        if NOTIFICATIONS_AVAILABLE and notification_manager:
            try:
                # Start notification monitoring
                notification_manager.start_monitoring()
                print("Notification system initialized and monitoring started")
            except Exception as e:
                print(f"Error initializing notifications: {e}")
        else:
            print("Notification system not available")

    def load_initial_data(self):
        """Load initial application data"""
        try:
            # Load categories and priorities
            self.categories = Category.get_all()
            self.priorities = Priority.get_all()

            # Update quick stats
            self.update_quick_stats()

        except Exception as e:
            print(f"Error loading initial data: {e}")
            messagebox.showerror("Error", f"Failed to load initial data: {e}")

    def refresh_data(self):
        """Refresh all data in current view"""
        try:
            self.load_initial_data()

            if hasattr(self.current_frame, 'refresh_data'):
                self.current_frame.refresh_data()

        except Exception as e:
            print(f"Error refreshing data: {e}")

    def refresh_theme(self):
        """Refresh UI after theme change"""
        try:
            # Force update all widgets
            self.root.update()
            self.root.update_idletasks()

            # Refresh current frame if it has a refresh method
            if hasattr(self.current_frame, 'refresh_data'):
                self.current_frame.refresh_data()

            # Update quick stats to refresh colors
            self.update_quick_stats()

        except Exception as e:
            print(f"Error refreshing theme: {e}")

    def save_settings(self):
        """Save application settings"""
        try:
            # Save any pending settings
            if hasattr(self.current_frame, 'save_settings'):
                self.current_frame.save_settings()

        except Exception as e:
            print(f"Error saving settings: {e}")
