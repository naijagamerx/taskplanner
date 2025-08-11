"""
Main window interface for Task Planner application
"""

import tkinter as tk
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

# Import enhanced services
try:
    from services.theme_manager import theme_manager
    from services.keyboard_manager import KeyboardManager
    from services.search_manager import search_manager
    from services.template_manager import template_manager
    ENHANCED_FEATURES_AVAILABLE = True
except ImportError:
    ENHANCED_FEATURES_AVAILABLE = False
    print("Enhanced features not available - using basic functionality")

class MainWindow:
    """Main application window"""

    def __init__(self, root):
        self.root = root
        self.current_frame = None

        # Initialize enhanced features
        self.keyboard_manager = None
        self.global_search_visible = False
        self.license_update_id = None

        if ENHANCED_FEATURES_AVAILABLE:
            # Initialize keyboard manager
            self.keyboard_manager = KeyboardManager(root)
            self.keyboard_manager.register_main_window(self)

            # Apply saved theme
            saved_theme = theme_manager.settings.get('theme', 'light')
            theme_manager.apply_theme(saved_theme)

        # Register with font manager
        try:
            from services.font_manager import register_for_font_updates, get_current_font_size
            register_for_font_updates(self)
            self.current_font_size = get_current_font_size()
        except ImportError:
            self.current_font_size = 12

        self.setup_ui()
        self.load_initial_data()

    def setup_ui(self):
        """Setup main window UI"""
        # Configure grid weights
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(1, weight=1)  # Changed to accommodate header

        # Create header with global search
        self.create_header()

        # Create sidebar
        self.create_sidebar()

        # Create main content area
        self.create_main_content()

        # Initialize notifications
        self.init_notifications()

        # Show default view
        self.show_tasks()

    def create_header(self):
        """Create header with global search and quick actions"""
        if not ENHANCED_FEATURES_AVAILABLE:
            return

        # Header frame
        self.header = ctk.CTkFrame(self.root, height=60, corner_radius=0)
        self.header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
        self.header.grid_columnconfigure(1, weight=1)

        # App title/logo
        title_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        title_frame.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        app_title = ctk.CTkLabel(
            title_frame,
            text="📋 Task Planner",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=theme_manager.get_color('primary')
        )
        app_title.pack(side="left")

        # Global search frame
        search_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        search_frame.grid(row=0, column=1, padx=20, pady=10, sticky="ew")
        search_frame.grid_columnconfigure(0, weight=1)

        # Search input
        self.global_search_var = tk.StringVar()
        self.global_search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.global_search_var,
            placeholder_text="🔍 Global search (Ctrl+F)...",
            height=35,
            font=ctk.CTkFont(size=12)
        )
        self.global_search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.global_search_var.trace("w", self.on_global_search)

        # Quick action buttons
        actions_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        actions_frame.grid(row=0, column=2, padx=20, pady=10, sticky="e")

        # Quick add task button
        quick_add_btn = theme_manager.create_styled_button(
            actions_frame,
            text="+ Task",
            command=self.show_add_task_dialog,
            style="primary",
            width=80,
            height=35
        )
        quick_add_btn.pack(side="left", padx=(0, 5))

        # Theme toggle button
        theme_btn = theme_manager.create_styled_button(
            actions_frame,
            text="🌙" if theme_manager.current_theme == "light" else "☀️",
            command=self.toggle_theme,
            style="secondary",
            width=40,
            height=35
        )
        theme_btn.pack(side="left", padx=(0, 5))

        # Settings button
        settings_btn = theme_manager.create_styled_button(
            actions_frame,
            text="⚙️",
            command=self.show_settings,
            style="secondary",
            width=40,
            height=35
        )
        settings_btn.pack(side="left")

    def create_sidebar(self):
        """Create navigation sidebar"""
        self.sidebar = ctk.CTkFrame(self.root, width=200, corner_radius=0)
        # Updated row position to accommodate header
        self.sidebar.grid(row=1, column=0, sticky="nsew", padx=(0, 2))
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

        # License status section
        self.create_license_status()

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
        self.overdue_tasks_label.pack(pady=2)

        # Completed tasks
        self.completed_tasks_label = ctk.CTkLabel(
            stats_frame,
            text="Completed: 0 tasks",
            font=ctk.CTkFont(size=12),
            text_color="green"
        )
        self.completed_tasks_label.pack(pady=(2, 10))

    def create_license_status(self):
        """Create license status display"""
        license_frame = ctk.CTkFrame(self.sidebar)
        license_frame.grid(row=7, column=0, padx=20, pady=(10, 10), sticky="ew")

        license_title = ctk.CTkLabel(
            license_frame,
            text="🔐 License Status",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        license_title.pack(pady=(10, 8))

        # License info with better spacing
        self.license_type_label = ctk.CTkLabel(
            license_frame,
            text="Type: Loading...",
            font=ctk.CTkFont(size=10),
            anchor="w"
        )
        self.license_type_label.pack(pady=(0, 4), padx=10, fill="x")

        self.license_user_label = ctk.CTkLabel(
            license_frame,
            text="User: Loading...",
            font=ctk.CTkFont(size=10),
            anchor="w"
        )
        self.license_user_label.pack(pady=(0, 4), padx=10, fill="x")

        self.license_expires_label = ctk.CTkLabel(
            license_frame,
            text="Expires: Loading...",
            font=ctk.CTkFont(size=10),
            anchor="w"
        )
        self.license_expires_label.pack(pady=(0, 4), padx=10, fill="x")

        # Status indicator
        self.license_status_label = ctk.CTkLabel(
            license_frame,
            text="Status: Loading...",
            font=ctk.CTkFont(size=10, weight="bold"),
            anchor="w"
        )
        self.license_status_label.pack(pady=(0, 10), padx=10, fill="x")

        # Update license status
        self.update_license_status()

        # Schedule periodic updates (store the after ID to prevent orphaned callbacks)
        self.license_update_id = self.root.after(60000, self.schedule_license_update)  # Update every minute

    def create_quick_actions(self):
        """Create quick action buttons"""
        actions_frame = ctk.CTkFrame(self.sidebar)
        actions_frame.grid(row=9, column=0, padx=20, pady=10, sticky="ew")

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
        # Updated row position to accommodate header
        self.main_content.grid(row=1, column=1, sticky="nsew", padx=(2, 0))
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
        """Show enhanced analytics view"""
        self.clear_main_content()
        self.update_nav_buttons('analytics')

        try:
            # Try to load enhanced analytics first
            if ENHANCED_FEATURES_AVAILABLE:
                from gui.enhanced_analytics import EnhancedAnalytics
                self.current_frame = EnhancedAnalytics(self.main_content, self)
                self.current_frame.pack(fill="both", expand=True)
                print("✅ Loaded enhanced analytics dashboard")
            else:
                # Fallback to basic analytics
                from gui.analytics import AnalyticsFrame
                self.current_frame = AnalyticsFrame(self.main_content, self)
                self.current_frame.pack(fill="both", expand=True)
                print("✅ Loaded basic analytics dashboard")
        except ImportError as e:
            print(f"Analytics import error: {e}")
            # Show error message
            error_label = ctk.CTkLabel(
                self.main_content,
                text="📊 Analytics Dashboard\n\nAnalytics features are currently unavailable.\nPlease check your installation.",
                font=ctk.CTkFont(size=16),
                justify="center"
            )
            error_label.pack(expand=True, fill="both", padx=50, pady=50)

        # Refresh analytics data when switching to this view
        if hasattr(self.current_frame, 'refresh_data'):
            self.current_frame.refresh_data()

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

            # Get completed tasks
            completed_tasks = Task.get_by_status('completed')

            # Update labels
            self.today_tasks_label.configure(text=f"Today: {len(today_tasks)} tasks")
            self.pending_tasks_label.configure(text=f"Pending: {len(pending_tasks)} tasks")
            self.overdue_tasks_label.configure(text=f"Overdue: {len(overdue_tasks)} tasks")
            self.completed_tasks_label.configure(text=f"Completed: {len(completed_tasks)} tasks")

        except Exception as e:
            print(f"Error updating quick stats: {e}")

    def update_license_status(self):
        """Update license status display"""
        try:
            from auth.license_manager import LicenseManager
            license_manager = LicenseManager()

            if license_manager.is_license_valid():
                license_info = license_manager.get_license_info()

                # Update license type
                license_type = license_info.get('license_type', 'Unknown').title()
                self.license_type_label.configure(
                    text=f"Type: {license_type}",
                    text_color="green"
                )

                # Update user
                user_name = license_info.get('user_name', 'Unknown')
                if len(user_name) > 15:
                    user_name = user_name[:12] + "..."
                self.license_user_label.configure(
                    text=f"User: {user_name}",
                    text_color="gray"
                )

                # Update expiration
                days_remaining = license_info.get('days_remaining', -1)
                if days_remaining == -1:
                    expires_text = "Never"
                    expires_color = "green"
                elif days_remaining > 30:
                    expires_text = f"{days_remaining} days"
                    expires_color = "green"
                elif days_remaining > 7:
                    expires_text = f"{days_remaining} days"
                    expires_color = "orange"
                elif days_remaining > 0:
                    expires_text = f"{days_remaining} days"
                    expires_color = "red"
                else:
                    expires_text = "Expired"
                    expires_color = "red"

                self.license_expires_label.configure(
                    text=f"Expires: {expires_text}",
                    text_color=expires_color
                )

                # Update status
                if days_remaining == -1:
                    # Never expires
                    self.license_status_label.configure(
                        text="Status: ✅ Active",
                        text_color="green"
                    )
                elif days_remaining == 0:
                    self.license_status_label.configure(
                        text="Status: ⏰ Expires Today",
                        text_color="red"
                    )
                elif days_remaining <= 7:
                    self.license_status_label.configure(
                        text="Status: ⚠️ Expiring Soon",
                        text_color="orange"
                    )
                else:
                    self.license_status_label.configure(
                        text="Status: ✅ Active",
                        text_color="green"
                    )
            else:
                # Invalid license - check if it's expired
                license_status = license_manager.current_license.get('status', 'invalid') if license_manager.current_license else 'invalid'

                if license_status == 'expired':
                    self.license_type_label.configure(
                        text="Type: Trial (Expired)",
                        text_color="orange"
                    )
                    self.license_user_label.configure(
                        text="User: Trial User",
                        text_color="gray"
                    )
                    self.license_expires_label.configure(
                        text="Expires: Expired",
                        text_color="red"
                    )
                    self.license_status_label.configure(
                        text="Status: 🕐 Expired",
                        text_color="red"
                    )
                else:
                    # Invalid license
                    self.license_type_label.configure(
                        text="Type: Invalid",
                        text_color="red"
                    )
                    self.license_user_label.configure(
                        text="User: N/A",
                        text_color="gray"
                    )
                    self.license_expires_label.configure(
                        text="Expires: N/A",
                        text_color="red"
                    )
                    self.license_status_label.configure(
                        text="Status: ❌ Invalid",
                        text_color="red"
                    )

        except Exception as e:
            print(f"Error updating license status: {e}")
            self.license_type_label.configure(
                text="Type: Error",
                text_color="red"
            )
            self.license_user_label.configure(
                text="User: Error",
                text_color="red"
            )
            self.license_expires_label.configure(
                text="Expires: Error",
                text_color="red"
            )
            self.license_status_label.configure(
                text="Status: ⚠️ Error",
                text_color="red"
            )

    def schedule_license_update(self):
        """Schedule periodic license status updates"""
        try:
            # Check if window still exists
            if self.root and self.root.winfo_exists():
                self.update_license_status()
                # Schedule next update in 1 minute
                self.license_update_id = self.root.after(60000, self.schedule_license_update)
        except tk.TclError:
            # Window has been destroyed, stop scheduling
            pass

    def init_notifications(self):
        """Initialize notification system with persistent service"""
        if NOTIFICATIONS_AVAILABLE and notification_manager:
            try:
                # Start notification monitoring
                notification_manager.start_monitoring()
                print("Notification system initialized and monitoring started")

                # Also start the persistent notification service
                try:
                    from services.notification_service import start_notification_service
                    if start_notification_service():
                        print("✅ Persistent notification service started")
                    else:
                        print("⚠️ Failed to start persistent notification service")
                except Exception as e:
                    print(f"⚠️ Error starting notification service: {e}")

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

    def cleanup(self):
        """Cleanup resources when window is closing"""
        try:
            # Cancel scheduled license updates
            if self.license_update_id:
                self.root.after_cancel(self.license_update_id)
                self.license_update_id = None
        except Exception as e:
            print(f"Error during cleanup: {e}")

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

    def cleanup(self, stop_notifications=False):
        """Cleanup resources when closing the application"""
        try:
            # Only stop notifications if explicitly requested (app exit, not window close)
            if stop_notifications:
                # Stop notification service
                try:
                    from services.notification_service import stop_notification_service
                    stop_notification_service()
                    print("✅ Notification service stopped")
                except Exception as e:
                    print(f"⚠️ Error stopping notification service: {e}")

                # Stop notification manager
                if NOTIFICATIONS_AVAILABLE and notification_manager:
                    try:
                        notification_manager.stop_monitoring()
                        print("✅ Notification manager stopped")
                    except Exception as e:
                        print(f"⚠️ Error stopping notification manager: {e}")
            else:
                print("ℹ️ Window closed but notifications continue running in background")

            # Save any pending settings
            self.save_settings()

        except Exception as e:
            print(f"Error during cleanup: {e}")

    def update_fonts(self, font_size):
        """Update fonts throughout the main window (called by font manager)"""
        try:
            self.current_font_size = font_size

            # Update all widgets recursively
            self.update_widget_font_recursive(self.root, font_size)

            # Update current frame if it has font update method
            if hasattr(self.current_frame, 'update_fonts'):
                self.current_frame.update_fonts(font_size)

            print(f"Main window fonts updated to {font_size}px")

        except Exception as e:
            print(f"Error updating main window fonts: {e}")

    def update_widget_font_recursive(self, widget, font_size):
        """Recursively update widget fonts"""
        try:
            # Update font for CTk widgets
            if hasattr(widget, 'configure'):
                if isinstance(widget, (ctk.CTkLabel, ctk.CTkButton, ctk.CTkEntry, ctk.CTkComboBox, ctk.CTkTextbox)):
                    widget.configure(font=ctk.CTkFont(size=font_size))
                elif isinstance(widget, ctk.CTkCheckBox):
                    widget.configure(font=ctk.CTkFont(size=font_size))
                elif isinstance(widget, ctk.CTkRadioButton):
                    widget.configure(font=ctk.CTkFont(size=font_size))

            # Recursively update children
            for child in widget.winfo_children():
                self.update_widget_font_recursive(child, font_size)

        except Exception:
            pass  # Ignore errors for widgets that don't support font changes

    # Enhanced Features Methods
    def on_global_search(self, *args):
        """Handle global search input"""
        if not ENHANCED_FEATURES_AVAILABLE:
            return

        query = self.global_search_var.get().strip()
        if len(query) < 2:
            return

        try:
            # Perform global search
            results = search_manager.global_search(query)

            # Show search results in a popup or dedicated view
            self.show_search_results(results, query)

        except Exception as e:
            print(f"Error in global search: {e}")

    def show_search_results(self, results, query):
        """Show global search results"""
        if not results:
            return

        # Create search results window
        search_window = ctk.CTkToplevel(self.root)
        search_window.title(f"Search Results: '{query}'")
        search_window.geometry("800x600")
        search_window.transient(self.root)

        # Results header
        header_frame = ctk.CTkFrame(search_window)
        header_frame.pack(fill="x", padx=10, pady=10)

        header_label = ctk.CTkLabel(
            header_frame,
            text=f"Found {len(results)} results for '{query}'",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        header_label.pack(pady=10)

        # Results list
        results_frame = ctk.CTkScrollableFrame(search_window)
        results_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        for i, result in enumerate(results):
            self.create_search_result_widget(results_frame, result, i)

    def create_search_result_widget(self, parent, result, index):
        """Create a widget for a search result"""
        # Result frame
        result_frame = ctk.CTkFrame(parent)
        result_frame.pack(fill="x", padx=5, pady=5)

        # Type icon
        type_icons = {
            'task': '📋',
            'goal': '🎯',
            'category': '📁',
            'habit': '🔄'
        }

        icon = type_icons.get(result.item_type, '📄')

        # Content
        content_frame = ctk.CTkFrame(result_frame, fg_color="transparent")
        content_frame.pack(fill="x", padx=10, pady=10)

        # Title with icon
        title_label = ctk.CTkLabel(
            content_frame,
            text=f"{icon} {result.title}",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        title_label.pack(anchor="w")

        # Description
        if result.description:
            desc_label = ctk.CTkLabel(
                content_frame,
                text=result.description[:100] + "..." if len(result.description) > 100 else result.description,
                font=ctk.CTkFont(size=11),
                text_color="gray",
                anchor="w"
            )
            desc_label.pack(anchor="w", pady=(2, 0))

        # Match score and type
        info_label = ctk.CTkLabel(
            content_frame,
            text=f"Type: {result.item_type.title()} | Score: {result.match_score:.2f}",
            font=ctk.CTkFont(size=10),
            text_color="gray",
            anchor="w"
        )
        info_label.pack(anchor="w", pady=(2, 0))

    def toggle_theme(self):
        """Toggle between light and dark theme"""
        if not ENHANCED_FEATURES_AVAILABLE:
            return

        try:
            current_theme = theme_manager.current_theme
            new_theme = 'dark' if current_theme == 'light' else 'light'
            theme_manager.apply_theme(new_theme)

            # Update theme button icon
            if hasattr(self, 'header'):
                # Find and update theme button
                for widget in self.header.winfo_children():
                    if isinstance(widget, ctk.CTkFrame):
                        for child in widget.winfo_children():
                            if isinstance(child, ctk.CTkButton) and child.cget("text") in ["🌙", "☀️"]:
                                child.configure(text="🌙" if new_theme == "light" else "☀️")

            # Refresh UI
            self.refresh_theme()

        except Exception as e:
            print(f"Error toggling theme: {e}")

    def show_add_task_dialog(self):
        """Show add task dialog with template support"""
        try:
            if ENHANCED_FEATURES_AVAILABLE:
                # Show enhanced dialog with templates
                self.show_enhanced_task_dialog()
            else:
                # Show basic dialog
                from gui.dialogs.task_dialog import TaskDialog
                dialog = TaskDialog(self.root)
                self.root.wait_window(dialog)

                if dialog.result:
                    self.refresh_data()
                    self.update_quick_stats()
        except Exception as e:
            print(f"Error showing add task dialog: {e}")

    def show_enhanced_task_dialog(self):
        """Show enhanced task dialog with templates"""
        # Create enhanced dialog window
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Create New Task")
        dialog.geometry("600x500")
        dialog.transient(self.root)
        dialog.grab_set()

        # Template selection frame
        template_frame = ctk.CTkFrame(dialog)
        template_frame.pack(fill="x", padx=20, pady=20)

        template_label = ctk.CTkLabel(
            template_frame,
            text="📋 Quick Start with Templates",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        template_label.pack(pady=10)

        # Template buttons
        templates = template_manager.get_popular_templates(6)
        template_buttons_frame = ctk.CTkFrame(template_frame, fg_color="transparent")
        template_buttons_frame.pack(fill="x", padx=10, pady=10)

        for i, template in enumerate(templates):
            btn = ctk.CTkButton(
                template_buttons_frame,
                text=template.name,
                command=lambda t=template: self.create_task_from_template(t, dialog),
                height=30,
                font=ctk.CTkFont(size=11)
            )
            btn.grid(row=i//2, column=i%2, padx=5, pady=5, sticky="ew")

        template_buttons_frame.grid_columnconfigure(0, weight=1)
        template_buttons_frame.grid_columnconfigure(1, weight=1)

        # Separator
        separator = ctk.CTkLabel(dialog, text="─" * 50, text_color="gray")
        separator.pack(pady=10)

        # Custom task button
        custom_btn = theme_manager.create_styled_button(
            dialog,
            text="✏️ Create Custom Task",
            command=lambda: self.show_custom_task_dialog(dialog),
            style="primary",
            height=40
        )
        custom_btn.pack(pady=20)

    def create_task_from_template(self, template, dialog):
        """Create task from template"""
        try:
            task = template_manager.create_task_from_template(template.template_id)
            if task:
                dialog.destroy()
                self.refresh_data()
                self.update_quick_stats()
                messagebox.showinfo("Success", f"Task created from template: {template.name}")
        except Exception as e:
            print(f"Error creating task from template: {e}")
            messagebox.showerror("Error", f"Failed to create task from template: {e}")

    def show_custom_task_dialog(self, parent_dialog):
        """Show custom task creation dialog"""
        parent_dialog.destroy()
        from gui.dialogs.task_dialog import TaskDialog
        dialog = TaskDialog(self.root)
        self.root.wait_window(dialog)

        if dialog.result:
            self.refresh_data()
            self.update_quick_stats()
