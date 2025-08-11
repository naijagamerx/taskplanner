"""
Settings interface for Task Planner application
"""

import tkinter as tk
from tkinter import messagebox, filedialog
import customtkinter as ctk
import json
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import db_manager
from models.category import Category

class SettingsFrame(ctk.CTkFrame):
    """Settings interface"""

    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.main_window = main_window
        self.settings = self.load_settings()

        # Register with font manager
        try:
            from services.font_manager import register_for_font_updates
            register_for_font_updates(self)
        except ImportError:
            pass

        self.setup_ui()

    def setup_ui(self):
        """Setup settings UI"""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Create header
        self.create_header()

        # Create settings notebook
        self.create_settings_notebook()

    def create_header(self):
        """Create header with title"""
        header_frame = ctk.CTkFrame(self)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        header_frame.grid_columnconfigure(1, weight=1)

        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="Settings",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")

        # Save button
        save_btn = ctk.CTkButton(
            header_frame,
            text="💾 Save Settings",
            command=self.save_settings,
            height=35,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        save_btn.grid(row=0, column=2, padx=20, pady=15, sticky="e")

    def create_settings_notebook(self):
        """Create settings tabbed interface"""
        # Main settings frame
        settings_frame = ctk.CTkFrame(self)
        settings_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))
        settings_frame.grid_columnconfigure(1, weight=1)
        settings_frame.grid_rowconfigure(0, weight=1)

        # Settings sidebar
        self.create_settings_sidebar(settings_frame)

        # Settings content area
        self.create_settings_content(settings_frame)

        # Show default settings
        self.show_general_settings()

    def create_settings_sidebar(self, parent):
        """Create settings navigation sidebar"""
        sidebar_frame = ctk.CTkFrame(parent)
        sidebar_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        sidebar_frame.grid_rowconfigure(10, weight=1)

        # Sidebar title
        sidebar_title = ctk.CTkLabel(
            sidebar_frame,
            text="Settings",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        sidebar_title.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")

        # Settings categories
        self.settings_var = tk.StringVar(value="general")

        categories = [
            ("general", "🔧 General"),
            ("appearance", "🎨 Appearance"),
            ("database", "🗄️ Database"),
            ("categories", "📋 Categories"),
            ("notifications", "🔔 Notifications"),
            ("backup", "💾 Backup & Export")
        ]

        for i, (value, text) in enumerate(categories):
            radio = ctk.CTkRadioButton(
                sidebar_frame,
                text=text,
                variable=self.settings_var,
                value=value,
                command=self.change_settings_view
            )
            radio.grid(row=i+1, column=0, padx=15, pady=5, sticky="w")

    def create_settings_content(self, parent):
        """Create settings content area"""
        self.content_frame = ctk.CTkFrame(parent)
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

    def clear_content(self):
        """Clear settings content area"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def change_settings_view(self):
        """Change settings view based on selection"""
        view = self.settings_var.get()

        if view == "general":
            self.show_general_settings()
        elif view == "appearance":
            self.show_appearance_settings()
        elif view == "database":
            self.show_database_settings()
        elif view == "categories":
            self.show_categories_settings()
        elif view == "notifications":
            self.show_notifications_settings()
        elif view == "backup":
            self.show_backup_settings()

    def show_general_settings(self):
        """Show general settings"""
        self.clear_content()

        # Scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(self.content_frame)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Title
        title_label = ctk.CTkLabel(
            scroll_frame,
            text="General Settings",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(10, 20), anchor="w")

        # Default reminder time
        reminder_frame = ctk.CTkFrame(scroll_frame)
        reminder_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            reminder_frame,
            text="Default Reminder Time (minutes before due):",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self.reminder_time_var = tk.StringVar(value=self.settings.get("default_reminder_time", "15"))
        reminder_entry = ctk.CTkEntry(
            reminder_frame,
            textvariable=self.reminder_time_var,
            placeholder_text="15"
        )
        reminder_entry.pack(fill="x", padx=15, pady=(0, 15))

        # Work hours
        work_hours_frame = ctk.CTkFrame(scroll_frame)
        work_hours_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            work_hours_frame,
            text="Work Hours:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))

        hours_container = ctk.CTkFrame(work_hours_frame, fg_color="transparent")
        hours_container.pack(fill="x", padx=15, pady=(0, 15))
        hours_container.grid_columnconfigure((0, 1), weight=1)

        # Start time
        ctk.CTkLabel(hours_container, text="Start:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.work_start_var = tk.StringVar(value=self.settings.get("work_hours_start", "09:00"))
        start_entry = ctk.CTkEntry(hours_container, textvariable=self.work_start_var, placeholder_text="09:00")
        start_entry.grid(row=1, column=0, sticky="ew", padx=(0, 10))

        # End time
        ctk.CTkLabel(hours_container, text="End:").grid(row=0, column=1, sticky="w")
        self.work_end_var = tk.StringVar(value=self.settings.get("work_hours_end", "17:00"))
        end_entry = ctk.CTkEntry(hours_container, textvariable=self.work_end_var, placeholder_text="17:00")
        end_entry.grid(row=1, column=1, sticky="ew")

        # Date format
        date_format_frame = ctk.CTkFrame(scroll_frame)
        date_format_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            date_format_frame,
            text="Date Format:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self.date_format_var = tk.StringVar(value=self.settings.get("date_format", "%Y-%m-%d"))
        date_format_combo = ctk.CTkComboBox(
            date_format_frame,
            variable=self.date_format_var,
            values=["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%B %d, %Y"]
        )
        date_format_combo.pack(fill="x", padx=15, pady=(0, 15))

        # Auto-save interval
        autosave_frame = ctk.CTkFrame(scroll_frame)
        autosave_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            autosave_frame,
            text="Auto-save Interval (minutes):",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self.autosave_var = tk.StringVar(value=self.settings.get("autosave_interval", "5"))
        autosave_entry = ctk.CTkEntry(
            autosave_frame,
            textvariable=self.autosave_var,
            placeholder_text="5"
        )
        autosave_entry.pack(fill="x", padx=15, pady=(0, 15))

    def show_appearance_settings(self):
        """Show appearance settings"""
        self.clear_content()

        scroll_frame = ctk.CTkScrollableFrame(self.content_frame)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        title_label = ctk.CTkLabel(
            scroll_frame,
            text="Appearance Settings",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(10, 20), anchor="w")

        # Theme selection
        theme_frame = ctk.CTkFrame(scroll_frame)
        theme_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            theme_frame,
            text="Theme:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self.theme_var = tk.StringVar(value=self.settings.get("theme", "light"))
        theme_segment = ctk.CTkSegmentedButton(
            theme_frame,
            values=["light", "dark", "system"],
            variable=self.theme_var,
            command=self.change_theme
        )
        theme_segment.pack(fill="x", padx=15, pady=(0, 15))

        # Color theme
        color_theme_frame = ctk.CTkFrame(scroll_frame)
        color_theme_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            color_theme_frame,
            text="Color Theme:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self.color_theme_var = tk.StringVar(value=self.settings.get("color_theme", "blue"))
        color_theme_combo = ctk.CTkComboBox(
            color_theme_frame,
            variable=self.color_theme_var,
            values=["blue", "green", "dark-blue"],
            command=self.change_color_theme
        )
        color_theme_combo.pack(fill="x", padx=15, pady=(0, 15))

        # Font size
        font_frame = ctk.CTkFrame(scroll_frame)
        font_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            font_frame,
            text="Font Size:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self.font_size_var = tk.StringVar(value=self.settings.get("font_size", "12"))
        font_size_combo = ctk.CTkComboBox(
            font_frame,
            variable=self.font_size_var,
            values=["8", "9", "10", "11", "12", "13", "14", "15", "16", "18", "20", "22", "24", "26", "28", "30", "32", "36", "40", "44", "48", "52", "56", "60", "64", "68", "72", "76", "80", "84", "88", "92", "96", "100"],
            command=self.on_font_size_change
        )
        font_size_combo.pack(fill="x", padx=15, pady=(0, 15))

        # Window startup behavior
        startup_frame = ctk.CTkFrame(scroll_frame)
        startup_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            startup_frame,
            text="Window Startup Behavior:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self.startup_mode_var = tk.StringVar(value=self.settings.get("startup_mode", "maximized"))
        startup_mode_combo = ctk.CTkComboBox(
            startup_frame,
            variable=self.startup_mode_var,
            values=["maximized", "centered_large", "custom"],
            command=self.on_startup_mode_change
        )
        startup_mode_combo.pack(fill="x", padx=15, pady=(0, 15))

    def show_database_settings(self):
        """Show database settings"""
        self.clear_content()

        scroll_frame = ctk.CTkScrollableFrame(self.content_frame)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        title_label = ctk.CTkLabel(
            scroll_frame,
            text="Database Settings",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(10, 20), anchor="w")

        # Database connection info
        info_frame = ctk.CTkFrame(scroll_frame)
        info_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            info_frame,
            text="Database Connection Information",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 10))

        # Connection status
        try:
            if db_manager.test_connection():
                status_text = "✅ Connected"
                status_color = "green"
            else:
                status_text = "❌ Disconnected"
                status_color = "red"
        except:
            status_text = "❌ Connection Error"
            status_color = "red"

        status_label = ctk.CTkLabel(
            info_frame,
            text=f"Status: {status_text}",
            font=ctk.CTkFont(size=12),
            text_color=status_color
        )
        status_label.pack(anchor="w", padx=15, pady=5)

        # Database info
        conn_info = db_manager.get_connection_info()

        if conn_info['type'] == 'MySQL':
            info_text = f"""Type: {conn_info['type']}
Host: {conn_info.get('host', 'N/A')}
Port: {conn_info.get('port', 'N/A')}
Database: {conn_info.get('database', 'N/A')}
User: {conn_info.get('user', 'N/A')}"""
        elif conn_info['type'] == 'SQLite':
            info_text = f"""Type: {conn_info['type']}
Database File: {conn_info.get('database', 'N/A')}"""
        else:
            info_text = "Type: Not configured"

        self.db_info_label = ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=ctk.CTkFont(size=11),
            justify="left"
        )
        self.db_info_label.pack(anchor="w", padx=15, pady=(5, 15))

        # Buttons frame
        buttons_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=15, pady=(0, 15))

        # Test connection button
        test_btn = ctk.CTkButton(
            buttons_frame,
            text="🔍 Test Connection",
            command=self.test_database_connection,
            width=140,
            height=35
        )
        test_btn.pack(side="left", padx=(0, 10))

        # Configure database button
        config_btn = ctk.CTkButton(
            buttons_frame,
            text="⚙️ Configure Database",
            command=self.configure_database,
            width=160,
            height=35,
            fg_color="orange",
            hover_color="darkorange"
        )
        config_btn.pack(side="left")

    def show_categories_settings(self):
        """Show categories management"""
        self.clear_content()

        scroll_frame = ctk.CTkScrollableFrame(self.content_frame)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        title_label = ctk.CTkLabel(
            scroll_frame,
            text="Categories Management",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(10, 20), anchor="w")

        # Add new category
        add_frame = ctk.CTkFrame(scroll_frame)
        add_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            add_frame,
            text="Add New Category",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 10))

        # Category form
        form_frame = ctk.CTkFrame(add_frame, fg_color="transparent")
        form_frame.pack(fill="x", padx=15, pady=(0, 15))
        form_frame.grid_columnconfigure(0, weight=1)

        # Name
        self.new_cat_name_var = tk.StringVar()
        name_entry = ctk.CTkEntry(
            form_frame,
            textvariable=self.new_cat_name_var,
            placeholder_text="Category name..."
        )
        name_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10), pady=5)

        # Color
        self.new_cat_color_var = tk.StringVar(value="#3498db")
        color_entry = ctk.CTkEntry(
            form_frame,
            textvariable=self.new_cat_color_var,
            placeholder_text="#3498db",
            width=100
        )
        color_entry.grid(row=0, column=1, padx=(0, 10), pady=5)

        # Add button
        add_btn = ctk.CTkButton(
            form_frame,
            text="Add",
            command=self.add_category,
            width=80
        )
        add_btn.grid(row=0, column=2, pady=5)

        # Existing categories
        existing_frame = ctk.CTkFrame(scroll_frame)
        existing_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            existing_frame,
            text="Existing Categories",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 10))

        # Categories list
        self.categories_list_frame = ctk.CTkFrame(existing_frame)
        self.categories_list_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.load_categories_list()

    def show_notifications_settings(self):
        """Show notifications settings"""
        self.clear_content()

        scroll_frame = ctk.CTkScrollableFrame(self.content_frame)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        title_label = ctk.CTkLabel(
            scroll_frame,
            text="🔔 Notifications Settings",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(10, 20), anchor="w")

        # Load notification manager
        try:
            from services.notification_manager import notification_manager
            self.notification_manager = notification_manager
        except Exception as e:
            print(f"Error loading notification manager: {e}")
            self.notification_manager = None

        # Desktop Notifications
        desktop_frame = ctk.CTkFrame(scroll_frame)
        desktop_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            desktop_frame,
            text="🖥️ Desktop Notifications",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 10))

        # Enable desktop notifications
        self.desktop_notifications_var = tk.BooleanVar(
            value=self.notification_manager.desktop_notifications_enabled if self.notification_manager else True
        )
        desktop_check = ctk.CTkCheckBox(
            desktop_frame,
            text="Enable desktop notifications",
            variable=self.desktop_notifications_var,
            command=self.update_notification_settings
        )
        desktop_check.pack(anchor="w", padx=15, pady=5)

        # Test notification button
        test_btn = ctk.CTkButton(
            desktop_frame,
            text="🔔 Test Notification",
            command=self.test_notification,
            width=150,
            height=30
        )
        test_btn.pack(anchor="w", padx=15, pady=(5, 15))

        # Sound Alerts
        sound_frame = ctk.CTkFrame(scroll_frame)
        sound_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            sound_frame,
            text="🔊 Sound Alerts",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 10))

        # Enable sound alerts
        self.sound_alerts_var = tk.BooleanVar(
            value=self.notification_manager.sound_alerts_enabled if self.notification_manager else True
        )
        sound_check = ctk.CTkCheckBox(
            sound_frame,
            text="Enable sound alerts",
            variable=self.sound_alerts_var,
            command=self.update_notification_settings
        )
        sound_check.pack(anchor="w", padx=15, pady=5)

        # Sound selection
        sound_selection_frame = ctk.CTkFrame(sound_frame, fg_color="transparent")
        sound_selection_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(sound_selection_frame, text="Notification Sound:").pack(side="left")

        self.notification_sound_var = tk.StringVar(
            value=self.notification_manager.notification_sound if self.notification_manager else 'default'
        )
        sound_combo = ctk.CTkComboBox(
            sound_selection_frame,
            variable=self.notification_sound_var,
            values=["default", "reminder", "urgent", "complete"],
            command=self.update_notification_settings,
            width=120
        )
        sound_combo.pack(side="left", padx=(10, 0))

        # Test sound button
        test_sound_btn = ctk.CTkButton(
            sound_selection_frame,
            text="🎵 Test Sound",
            command=self.test_sound,
            width=100,
            height=25
        )
        test_sound_btn.pack(side="left", padx=(10, 0))

        # Add some spacing
        ctk.CTkLabel(sound_frame, text="").pack(pady=5)

        # Reminder Settings
        reminder_frame = ctk.CTkFrame(scroll_frame)
        reminder_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            reminder_frame,
            text="⏰ Reminder Settings",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 10))

        # Reminder time before due
        reminder_time_frame = ctk.CTkFrame(reminder_frame, fg_color="transparent")
        reminder_time_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(reminder_time_frame, text="Remind me:").pack(side="left")

        self.reminder_minutes_var = tk.StringVar(
            value=str(self.notification_manager.reminder_minutes if self.notification_manager else 15)
        )
        reminder_entry = ctk.CTkEntry(
            reminder_time_frame,
            textvariable=self.reminder_minutes_var,
            width=60,
            placeholder_text="15"
        )
        reminder_entry.pack(side="left", padx=(10, 5))
        reminder_entry.bind('<KeyRelease>', lambda e: self.update_notification_settings())

        ctk.CTkLabel(reminder_time_frame, text="minutes before due time").pack(side="left")

        # Check interval
        interval_frame = ctk.CTkFrame(reminder_frame, fg_color="transparent")
        interval_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(interval_frame, text="Check for reminders every:").pack(side="left")

        self.check_interval_var = tk.StringVar(
            value=str(self.notification_manager.check_interval if self.notification_manager else 60)
        )
        interval_entry = ctk.CTkEntry(
            interval_frame,
            textvariable=self.check_interval_var,
            width=60,
            placeholder_text="60"
        )
        interval_entry.pack(side="left", padx=(10, 5))
        interval_entry.bind('<KeyRelease>', lambda e: self.update_notification_settings())

        ctk.CTkLabel(interval_frame, text="seconds").pack(side="left")

        # Add some spacing
        ctk.CTkLabel(reminder_frame, text="").pack(pady=5)

        # Monitoring Status
        status_frame = ctk.CTkFrame(scroll_frame)
        status_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            status_frame,
            text="📊 Monitoring Status",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 10))

        # Status display
        status_text = "🟢 Active" if (self.notification_manager and self.notification_manager.running) else "🔴 Inactive"
        self.status_label = ctk.CTkLabel(
            status_frame,
            text=f"Notification monitoring: {status_text}",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(anchor="w", padx=15, pady=5)

        # Control buttons
        control_frame = ctk.CTkFrame(status_frame, fg_color="transparent")
        control_frame.pack(fill="x", padx=15, pady=(5, 15))

        start_btn = ctk.CTkButton(
            control_frame,
            text="▶️ Start Monitoring",
            command=self.start_monitoring,
            width=140,
            height=30,
            fg_color="green",
            hover_color="darkgreen"
        )
        start_btn.pack(side="left", padx=(0, 10))

        stop_btn = ctk.CTkButton(
            control_frame,
            text="⏹️ Stop Monitoring",
            command=self.stop_monitoring,
            width=140,
            height=30,
            fg_color="red",
            hover_color="darkred"
        )
        stop_btn.pack(side="left")

        # Force check button
        force_check_btn = ctk.CTkButton(
            control_frame,
            text="🔄 Check Now",
            command=self.force_check_now,
            width=120,
            height=30,
            fg_color="orange",
            hover_color="darkorange"
        )
        force_check_btn.pack(side="left", padx=(10, 0))

        # Refresh status button
        refresh_btn = ctk.CTkButton(
            control_frame,
            text="🔄 Refresh Status",
            command=self.refresh_monitoring_status,
            width=120,
            height=30
        )
        refresh_btn.pack(side="left", padx=(10, 0))

        # Detailed status info
        if self.notification_manager:
            status_info = self.notification_manager.get_monitoring_status()
            details_text = (
                f"Last Check: {status_info['last_check_time']}\n"
                f"Check Interval: {status_info['check_interval']} seconds\n"
                f"Check Failures: {status_info['check_failures']}/{status_info['max_check_failures']}\n"
                f"Notifications Sent Today: {status_info['notifications_sent_today']}"
            )

            details_label = ctk.CTkLabel(
                status_frame,
                text=details_text,
                font=ctk.CTkFont(size=10),
                justify="left"
            )
            details_label.pack(anchor="w", padx=15, pady=(5, 15))

    def start_monitoring(self):
        """Start notification monitoring"""
        if self.notification_manager:
            self.notification_manager.enable_monitoring()
            self.update_monitoring_status()
            messagebox.showinfo("Success", "Notification monitoring started!")
        else:
            messagebox.showerror("Error", "Notification manager not available")

    def stop_monitoring(self):
        """Stop notification monitoring"""
        if self.notification_manager:
            self.notification_manager.disable_monitoring()
            self.update_monitoring_status()
            messagebox.showinfo("Success", "Notification monitoring stopped!")
        else:
            messagebox.showerror("Error", "Notification manager not available")

    def force_check_now(self):
        """Force immediate notification check"""
        if self.notification_manager:
            if self.notification_manager.force_check_now():
                messagebox.showinfo("Success", "Immediate notification check completed!")
            else:
                messagebox.showerror("Error", "Failed to perform immediate check")
            self.refresh_monitoring_status()
        else:
            messagebox.showerror("Error", "Notification manager not available")

    def refresh_monitoring_status(self):
        """Refresh monitoring status display"""
        if hasattr(self, 'status_label') and self.notification_manager:
            status_text = "🟢 Active" if self.notification_manager.is_monitoring_active() else "🔴 Inactive"
            self.status_label.configure(text=f"Notification monitoring: {status_text}")

    def show_backup_settings(self):
        """Show backup and export settings"""
        self.clear_content()

        scroll_frame = ctk.CTkScrollableFrame(self.content_frame)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        title_label = ctk.CTkLabel(
            scroll_frame,
            text="Backup & Export",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(10, 20), anchor="w")

        # Export data
        export_frame = ctk.CTkFrame(scroll_frame)
        export_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            export_frame,
            text="Export Data",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 10))

        export_btn = ctk.CTkButton(
            export_frame,
            text="📤 Export Tasks to JSON",
            command=self.export_data,
            width=200
        )
        export_btn.pack(anchor="w", padx=15, pady=(0, 15))

        # Import data
        import_frame = ctk.CTkFrame(scroll_frame)
        import_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            import_frame,
            text="Import Data",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 10))

        import_btn = ctk.CTkButton(
            import_frame,
            text="📥 Import Tasks from JSON",
            command=self.import_data,
            width=200
        )
        import_btn.pack(anchor="w", padx=15, pady=(0, 15))

    def change_theme(self, theme):
        """Change application theme with enhanced dark mode"""
        try:
            # Prevent multiple rapid theme changes
            if hasattr(self, '_changing_theme') and self._changing_theme:
                return

            self._changing_theme = True

            # Store the theme setting
            self.settings["theme"] = theme

            # Apply enhanced theme with theme manager
            try:
                from services.theme_manager import theme_manager
                theme_manager.apply_theme(theme)
                print(f"✅ Applied enhanced theme: {theme}")
            except ImportError:
                # Fallback to basic theme change
                ctk.set_appearance_mode(theme)
                print(f"✅ Applied basic theme: {theme}")

            # Apply the theme gradually
            self.apply_theme_change(theme)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to change theme: {e}")
            # Revert theme variable if change failed
            if hasattr(self, 'theme_var'):
                self.theme_var.set(self.settings.get("theme", "light"))
        finally:
            # Reset the flag after a delay
            self.after(1000, lambda: setattr(self, '_changing_theme', False))

    def apply_theme_change(self, theme):
        """Apply theme change with proper refresh"""
        try:
            # Apply the theme
            ctk.set_appearance_mode(theme)

            # Schedule UI refresh after theme application
            self.after(100, self.refresh_ui_after_theme_change)

        except Exception as e:
            print(f"Error applying theme change: {e}")

    def refresh_ui_after_theme_change(self):
        """Refresh UI components after theme change"""
        try:
            # Force update all widgets
            self.update()
            self.update_idletasks()

            # Refresh the current settings view to apply new theme colors
            self.after(50, self.change_settings_view)

            # Update main window if it has a refresh method
            if hasattr(self.main_window, 'refresh_theme'):
                self.after(150, self.main_window.refresh_theme)

        except Exception as e:
            print(f"Error refreshing UI after theme change: {e}")

    def change_color_theme(self, color_theme):
        """Change color theme"""
        try:
            ctk.set_default_color_theme(color_theme)
            self.settings["color_theme"] = color_theme
            messagebox.showinfo("Info", "Color theme will be applied after restart.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to change color theme: {e}")

    def configure_database(self):
        """Open database configuration dialog"""
        try:
            from gui.database_setup_dialog import DatabaseSetupDialog

            dialog = DatabaseSetupDialog(self)
            result = dialog.show_dialog()

            if result:
                # Update database configuration
                if db_manager.update_configuration(result):
                    messagebox.showinfo(
                        "Success",
                        "Database configuration updated successfully!\n"
                        "The application will restart to apply changes."
                    )

                    # Refresh the database settings display
                    self.show_database_settings()

                    # Optionally restart the application
                    # self.restart_application()
                else:
                    messagebox.showerror(
                        "Error",
                        "Failed to update database configuration.\n"
                        "Please check your settings and try again."
                    )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open database configuration: {e}")

    def test_database_connection(self):
        """Test database connection"""
        try:
            print("Testing database connection from settings...")

            # Test connection using db_manager
            if db_manager.test_connection():
                # Get connection info for display
                conn_info = db_manager.get_connection_info()

                if conn_info['type'] == 'MySQL':
                    info_text = f"MySQL Connection Successful!\n\n" \
                               f"Host: {conn_info.get('host', 'N/A')}\n" \
                               f"Port: {conn_info.get('port', 'N/A')}\n" \
                               f"Database: {conn_info.get('database', 'N/A')}\n" \
                               f"User: {conn_info.get('user', 'N/A')}"
                elif conn_info['type'] == 'SQLite':
                    info_text = f"SQLite Connection Successful!\n\n" \
                               f"Database File: {conn_info.get('database', 'N/A')}"
                else:
                    info_text = "Database connection successful!"

                messagebox.showinfo("Success", info_text)
            else:
                messagebox.showerror("Error",
                                   "Database connection failed!\n\n"
                                   "Please check your database configuration in the Database Settings section.")

        except Exception as e:
            print(f"Database connection test error: {e}")
            messagebox.showerror("Error",
                               f"Connection test failed:\n\n{str(e)}\n\n"
                               f"Please check your database configuration.")

    def add_category(self):
        """Add new category"""
        name = self.new_cat_name_var.get().strip()
        color = self.new_cat_color_var.get().strip()

        if not name:
            messagebox.showerror("Error", "Category name is required!")
            return

        try:
            from models.category import Category
            category = Category(name=name, color=color)
            if category.save():
                messagebox.showinfo("Success", "Category added successfully!")
                self.new_cat_name_var.set("")
                self.new_cat_color_var.set("#3498db")
                self.load_categories_list()
            else:
                messagebox.showerror("Error", "Failed to add category!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add category: {e}")

    def load_categories_list(self):
        """Load and display categories list"""
        # Clear existing categories
        for widget in self.categories_list_frame.winfo_children():
            widget.destroy()

        try:
            categories = Category.get_all()
            for i, category in enumerate(categories):
                cat_frame = ctk.CTkFrame(self.categories_list_frame)
                cat_frame.pack(fill="x", padx=5, pady=2)
                cat_frame.grid_columnconfigure(1, weight=1)

                # Color indicator
                color_frame = ctk.CTkFrame(cat_frame, fg_color=category.color, width=20, height=30)
                color_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ns")

                # Name
                name_label = ctk.CTkLabel(
                    cat_frame,
                    text=category.name,
                    font=ctk.CTkFont(size=12)
                )
                name_label.grid(row=0, column=1, sticky="w", padx=10, pady=5)

                # Delete button (only for non-default categories)
                if category.id > 6:  # Don't delete default categories
                    delete_btn = ctk.CTkButton(
                        cat_frame,
                        text="Delete",
                        command=lambda c=category: self.delete_category(c),
                        width=60,
                        height=25,
                        fg_color="red",
                        hover_color="darkred"
                    )
                    delete_btn.grid(row=0, column=2, padx=10, pady=5)

        except Exception as e:
            print(f"Error loading categories: {e}")

    def delete_category(self, category):
        """Delete category"""
        if messagebox.askyesno("Confirm Delete", f"Delete category '{category.name}'?"):
            try:
                if category.delete():
                    messagebox.showinfo("Success", "Category deleted successfully!")
                    self.load_categories_list()
                else:
                    messagebox.showerror("Error", "Failed to delete category!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete category: {e}")

    def export_data(self):
        """Export data to JSON file"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )

            if filename:
                # Export implementation would go here
                messagebox.showinfo("Info", "Export functionality will be implemented in the next update!")

        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {e}")

    def import_data(self):
        """Import data from JSON file"""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )

            if filename:
                # Import implementation would go here
                messagebox.showinfo("Info", "Import functionality will be implemented in the next update!")

        except Exception as e:
            messagebox.showerror("Error", f"Import failed: {e}")

    def load_settings(self):
        """Load settings from file using SettingsManager"""
        try:
            from database.settings_manager import SettingsManager
            settings_manager = SettingsManager()

            # Get settings from SettingsManager (which uses AppData)
            return {
                "theme": settings_manager.get('theme', 'light'),
                "color_theme": settings_manager.get('color_theme', 'blue'),
                "font_size": str(settings_manager.get('font_size', 12)),
                "default_reminder_time": str(settings_manager.get('default_reminder_time', 15)),
                "work_hours_start": settings_manager.get('work_hours_start', '09:00'),
                "work_hours_end": settings_manager.get('work_hours_end', '17:00'),
                "date_format": settings_manager.get('date_format', '%Y-%m-%d'),
                "autosave_interval": str(settings_manager.get('autosave_interval', 5)),
                "startup_mode": settings_manager.get('startup_mode', 'maximized')
            }
        except Exception as e:
            print(f"Error loading settings: {e}")
            # Return defaults if SettingsManager fails
            return {
                "theme": "light",
                "color_theme": "blue",
                "font_size": "12",
                "default_reminder_time": "15",
                "work_hours_start": "09:00",
                "work_hours_end": "17:00",
                "date_format": "%Y-%m-%d",
                "autosave_interval": "5",
                "startup_mode": "maximized"
            }

    def update_notification_settings(self, *args):
        """Update notification settings"""
        if not self.notification_manager:
            return

        try:
            # Update notification manager settings
            self.notification_manager.desktop_notifications_enabled = self.desktop_notifications_var.get()
            self.notification_manager.sound_alerts_enabled = self.sound_alerts_var.get()
            self.notification_manager.notification_sound = self.notification_sound_var.get()

            # Update numeric settings with validation
            try:
                self.notification_manager.reminder_minutes = int(self.reminder_minutes_var.get())
            except ValueError:
                self.notification_manager.reminder_minutes = 15

            try:
                self.notification_manager.check_interval = int(self.check_interval_var.get())
            except ValueError:
                self.notification_manager.check_interval = 60

            # Save settings
            self.notification_manager.save_settings()

        except Exception as e:
            print(f"Error updating notification settings: {e}")

    def test_notification(self):
        """Test desktop notification"""
        if self.notification_manager:
            self.notification_manager.test_notification()
        else:
            messagebox.showinfo("Test", "Notification system not available")

    def test_sound(self):
        """Test notification sound"""
        if self.notification_manager:
            sound_type = self.notification_sound_var.get()
            self.notification_manager.play_notification_sound(sound_type)
        else:
            messagebox.showinfo("Test", "Sound system not available")

    def start_monitoring(self):
        """Start notification monitoring"""
        if self.notification_manager:
            self.notification_manager.start_monitoring()
            self.update_monitoring_status()
        else:
            messagebox.showerror("Error", "Notification manager not available")

    def stop_monitoring(self):
        """Stop notification monitoring"""
        if self.notification_manager:
            self.notification_manager.stop_monitoring()
            self.update_monitoring_status()
        else:
            messagebox.showerror("Error", "Notification manager not available")

    def update_monitoring_status(self):
        """Update monitoring status display"""
        if hasattr(self, 'status_label') and self.notification_manager:
            status_text = "🟢 Active" if self.notification_manager.running else "🔴 Inactive"
            self.status_label.configure(text=f"Notification monitoring: {status_text}")

    def on_font_size_change(self, value):
        """Handle font size change using global font manager"""
        try:
            # Import font manager
            from services.font_manager import set_global_font_size

            # Update global font size
            set_global_font_size(int(value))

            # Update settings
            self.settings["font_size"] = value

            # Show feedback
            messagebox.showinfo("Font Size Changed",
                              f"Font size changed to {value}px.\n"
                              f"All components have been updated!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to change font size: {e}")

    def on_startup_mode_change(self, value):
        """Handle startup mode change"""
        try:
            # Update settings
            self.settings["startup_mode"] = value

            # Update window config
            from config.window_config import window_config
            window_config.update_setting("startup_mode", value)

            # Show feedback
            mode_descriptions = {
                "maximized": "Window will start maximized (full screen)",
                "centered_large": "Window will start large and centered",
                "custom": "Window will start with custom size and position"
            }

            description = mode_descriptions.get(value, "Window startup behavior updated")
            messagebox.showinfo("Startup Mode Changed",
                              f"Startup mode changed to: {value.replace('_', ' ').title()}\n\n"
                              f"{description}\n\n"
                              f"This will take effect the next time you start the application.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to change startup mode: {e}")

    def update_fonts(self, font_size):
        """Update fonts in the settings window (called by font manager)"""
        try:
            # Update all labels and buttons in settings
            for widget in self.winfo_children():
                self.update_widget_font_recursive(widget, font_size)
        except Exception as e:
            print(f"Error updating settings fonts: {e}")

    def update_widget_font_recursive(self, widget, font_size):
        """Recursively update widget fonts"""
        try:
            # Update font for CTk widgets
            if hasattr(widget, 'configure'):
                if isinstance(widget, (ctk.CTkLabel, ctk.CTkButton, ctk.CTkEntry, ctk.CTkComboBox)):
                    widget.configure(font=ctk.CTkFont(size=font_size))
                elif isinstance(widget, ctk.CTkCheckBox):
                    widget.configure(font=ctk.CTkFont(size=font_size))
                elif isinstance(widget, ctk.CTkRadioButton):
                    widget.configure(font=ctk.CTkFont(size=font_size))

            # Recursively update children
            for child in widget.winfo_children():
                self.update_widget_font_recursive(child, font_size)

        except Exception as e:
            pass  # Ignore errors for widgets that don't support font changes

    def save_settings(self):
        """Save current settings using SettingsManager"""
        try:
            from database.settings_manager import SettingsManager
            settings_manager = SettingsManager()

            # Update settings from UI
            if hasattr(self, 'reminder_time_var'):
                try:
                    settings_manager.set('default_reminder_time', int(self.reminder_time_var.get()))
                except ValueError:
                    settings_manager.set('default_reminder_time', 15)
            if hasattr(self, 'work_start_var'):
                settings_manager.set('work_hours_start', self.work_start_var.get())
            if hasattr(self, 'work_end_var'):
                settings_manager.set('work_hours_end', self.work_end_var.get())
            if hasattr(self, 'date_format_var'):
                settings_manager.set('date_format', self.date_format_var.get())
            if hasattr(self, 'autosave_var'):
                try:
                    settings_manager.set('autosave_interval', int(self.autosave_var.get()))
                except ValueError:
                    settings_manager.set('autosave_interval', 5)
            if hasattr(self, 'theme_var'):
                settings_manager.set('theme', self.theme_var.get())
            if hasattr(self, 'color_theme_var'):
                settings_manager.set('color_theme', self.color_theme_var.get())
            if hasattr(self, 'font_size_var'):
                try:
                    settings_manager.set('font_size', int(self.font_size_var.get()))
                except ValueError:
                    settings_manager.set('font_size', 12)
            if hasattr(self, 'startup_mode_var'):
                settings_manager.set('startup_mode', self.startup_mode_var.get())

            # Save notification settings
            if hasattr(self, 'notification_manager') and self.notification_manager:
                self.update_notification_settings()

            # Save to AppData using SettingsManager
            settings_manager.save()

            messagebox.showinfo("Success", "Settings saved successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
