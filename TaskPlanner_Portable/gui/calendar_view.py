"""
Calendar view interface for Task Planner application
"""

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from datetime import datetime, date, timedelta, time
from tkcalendar import Calendar
import calendar as cal
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.task import Task
from models.category import Category, Priority
from gui.dialogs.task_dialog import TaskDialog

# Import notification manager
try:
    from services.notification_manager import notification_manager
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False
    notification_manager = None

class CalendarFrame(ctk.CTkFrame):
    """Calendar view interface"""

    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.main_window = main_window
        self.current_date = date.today()
        self.selected_date = date.today()
        self.view_mode = "month"  # month, week, day
        self.tasks = []

        # Pagination variables for task details
        self.task_page = 1
        self.task_page_size = 5
        self.total_task_pages = 1

        self.setup_ui()
        self.load_tasks()

    def setup_ui(self):
        """Setup calendar UI"""
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Create header
        self.create_header()

        # Create calendar panel
        self.create_calendar_panel()

        # Create task details panel
        self.create_task_details_panel()

    def create_header(self):
        """Create modern header with navigation and view controls"""
        header_frame = ctk.CTkFrame(self, corner_radius=15)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 5))
        header_frame.grid_columnconfigure(1, weight=1)

        # Left side - Navigation
        nav_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        nav_frame.grid(row=0, column=0, padx=20, pady=15, sticky="w")

        # Navigation buttons with modern styling
        prev_btn = ctk.CTkButton(
            nav_frame,
            text="◀",
            command=self.previous_period,
            width=45,
            height=40,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=("gray85", "gray25"),
            hover_color=("gray75", "gray35"),
            corner_radius=12
        )
        prev_btn.pack(side="left", padx=(0, 15))

        # Current period label with better styling
        period_container = ctk.CTkFrame(nav_frame, fg_color="transparent")
        period_container.pack(side="left", padx=10)

        self.period_label = ctk.CTkLabel(
            period_container,
            text="",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self.period_label.pack()

        # Next button
        next_btn = ctk.CTkButton(
            nav_frame,
            text="▶",
            command=self.next_period,
            width=45,
            height=40,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=("gray85", "gray25"),
            hover_color=("gray75", "gray35"),
            corner_radius=12
        )
        next_btn.pack(side="left", padx=(15, 0))

        # Today button with accent color
        today_btn = ctk.CTkButton(
            nav_frame,
            text="📅 Today",
            command=self.go_to_today,
            width=90,
            height=40,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#4a90e2",
            hover_color="#357abd",
            corner_radius=12
        )
        today_btn.pack(side="left", padx=(25, 0))

        # Right side - Controls
        controls_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        controls_frame.grid(row=0, column=2, padx=20, pady=15, sticky="e")

        # Add task button with prominent styling
        add_task_btn = ctk.CTkButton(
            controls_frame,
            text="+ Add Task",
            command=self.add_task_for_date,
            width=120,
            height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#34c759",
            hover_color="#30b855",
            corner_radius=12
        )
        add_task_btn.pack(side="right", padx=(15, 0))

        # View mode segmented button with better styling
        self.view_mode_var = tk.StringVar(value="month")
        view_segment = ctk.CTkSegmentedButton(
            controls_frame,
            values=["Day", "Week", "Month"],
            variable=self.view_mode_var,
            command=self.change_view_mode,
            width=200,
            height=40,
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=12
        )
        view_segment.pack(side="right")

        self.update_period_label()

    def create_calendar_panel(self):
        """Create calendar display panel"""
        self.calendar_frame = ctk.CTkFrame(self)
        self.calendar_frame.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=5)
        self.calendar_frame.grid_columnconfigure(0, weight=1)
        self.calendar_frame.grid_rowconfigure(1, weight=1)

        # Calendar widget
        self.create_calendar_widget()

    def create_calendar_widget(self):
        """Create the calendar widget based on view mode"""
        # Clear existing calendar
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        if self.view_mode == "month":
            self.create_month_view()
        elif self.view_mode == "week":
            self.create_week_view()
        else:  # day view
            self.create_day_view()

    def create_month_view(self):
        """Create modern month calendar view"""
        # Calendar header
        header_frame = ctk.CTkFrame(self.calendar_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 10))
        header_frame.grid_columnconfigure(0, weight=1)

        cal_title = ctk.CTkLabel(
            header_frame,
            text="📅 Monthly Calendar",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        cal_title.grid(row=0, column=0, sticky="w")

        cal_subtitle = ctk.CTkLabel(
            header_frame,
            text="Click on any date to view tasks",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        cal_subtitle.grid(row=1, column=0, sticky="w", pady=(2, 0))

        # Modern calendar widget with better styling
        calendar_container = ctk.CTkFrame(self.calendar_frame, corner_radius=15)
        calendar_container.grid(row=1, column=0, padx=15, pady=15, sticky="nsew")

        self.calendar_widget = Calendar(
            calendar_container,
            selectmode='day',
            year=self.current_date.year,
            month=self.current_date.month,
            day=self.current_date.day,
            date_pattern='yyyy-mm-dd',
            background='#f0f0f0',
            foreground='#333333',
            bordercolor='#e0e0e0',
            headersbackground='#4a90e2',
            headersforeground='white',
            normalbackground='white',
            normalforeground='#333333',
            weekendbackground='#f8f9fa',
            weekendforeground='#666666',
            selectbackground='#4a90e2',
            selectforeground='white',
            othermonthbackground='#f5f5f5',
            othermonthforeground='#cccccc',
            font=('Arial', 10),
            borderwidth=0
        )
        self.calendar_widget.pack(padx=20, pady=20, fill="both", expand=True)

        # Bind calendar selection
        self.calendar_widget.bind("<<CalendarSelected>>", self.on_date_selected)

        # Mark dates with tasks
        self.mark_task_dates()

    def create_week_view(self):
        """Create modern week calendar view"""
        # Week header
        header_frame = ctk.CTkFrame(self.calendar_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 10))
        header_frame.grid_columnconfigure(0, weight=1)

        week_title = ctk.CTkLabel(
            header_frame,
            text="📅 Weekly Schedule",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        week_title.grid(row=0, column=0, sticky="w")

        # Get week dates
        start_of_week = self.current_date - timedelta(days=self.current_date.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        week_subtitle = ctk.CTkLabel(
            header_frame,
            text=f"{start_of_week.strftime('%B %d')} - {end_of_week.strftime('%B %d, %Y')}",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        week_subtitle.grid(row=1, column=0, sticky="w", pady=(2, 0))

        # Week container
        week_container = ctk.CTkFrame(self.calendar_frame, corner_radius=15)
        week_container.grid(row=1, column=0, sticky="nsew", padx=15, pady=15)
        week_container.grid_columnconfigure(0, weight=1)
        week_container.grid_rowconfigure(0, weight=1)

        # Scrollable week frame
        week_frame = ctk.CTkScrollableFrame(week_container)
        week_frame.pack(fill="both", expand=True, padx=20, pady=20)

        week_dates = [start_of_week + timedelta(days=i) for i in range(7)]

        # Create day columns
        for day_idx, day_date in enumerate(week_dates):
            day_frame = ctk.CTkFrame(week_frame, corner_radius=10)
            day_frame.grid(row=0, column=day_idx, padx=5, pady=5, sticky="nsew")
            week_frame.grid_columnconfigure(day_idx, weight=1, minsize=150)

            # Day header
            day_header = ctk.CTkLabel(
                day_frame,
                text=day_date.strftime("%a\n%m/%d"),
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color=("gray85", "gray25") if day_date == date.today() else "transparent",
                corner_radius=8
            )
            day_header.pack(pady=(10, 5), padx=10, fill="x")

            # Tasks for this day
            day_tasks = [t for t in self.tasks if t.due_date == day_date]
            day_tasks.sort(key=lambda x: x.due_time or time(0, 0))

            if day_tasks:
                for task in day_tasks[:5]:  # Show max 5 tasks
                    task_widget = ctk.CTkFrame(day_frame, corner_radius=8)
                    task_widget.pack(pady=2, padx=10, fill="x")

                    # Task time and title
                    if task.due_time and hasattr(task.due_time, 'strftime'):
                        time_text = task.due_time.strftime("%H:%M")
                    else:
                        time_text = "All day"
                    task_label = ctk.CTkLabel(
                        task_widget,
                        text=f"{time_text}\n{task.title[:25]}{'...' if len(task.title) > 25 else ''}",
                        font=ctk.CTkFont(size=9),
                        justify="left"
                    )
                    task_label.pack(pady=5, padx=8, anchor="w")

                if len(day_tasks) > 5:
                    more_label = ctk.CTkLabel(
                        day_frame,
                        text=f"+{len(day_tasks) - 5} more",
                        font=ctk.CTkFont(size=8),
                        text_color="gray"
                    )
                    more_label.pack(pady=2)
            else:
                no_tasks_label = ctk.CTkLabel(
                    day_frame,
                    text="No tasks",
                    font=ctk.CTkFont(size=10),
                    text_color="gray"
                )
                no_tasks_label.pack(pady=20)

    def create_day_view(self):
        """Create modern day calendar view"""
        # Day header
        header_frame = ctk.CTkFrame(self.calendar_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 10))
        header_frame.grid_columnconfigure(0, weight=1)

        day_title = ctk.CTkLabel(
            header_frame,
            text="📅 Daily Schedule",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        day_title.grid(row=0, column=0, sticky="w")

        day_subtitle = ctk.CTkLabel(
            header_frame,
            text=self.current_date.strftime('%A, %B %d, %Y'),
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        day_subtitle.grid(row=1, column=0, sticky="w", pady=(2, 0))

        # Day container
        day_container = ctk.CTkFrame(self.calendar_frame, corner_radius=15)
        day_container.grid(row=1, column=0, sticky="nsew", padx=15, pady=15)
        day_container.grid_columnconfigure(0, weight=1)
        day_container.grid_rowconfigure(0, weight=1)

        # Scrollable day frame
        day_frame = ctk.CTkScrollableFrame(day_container)
        day_frame.pack(fill="both", expand=True, padx=20, pady=20)
        day_frame.grid_columnconfigure(1, weight=1)

        # Get tasks for the day
        day_tasks = [t for t in self.tasks if t.due_date == self.current_date]
        day_tasks.sort(key=lambda x: x.due_time or time(0, 0))

        # Create time slots (6 AM to 11 PM)
        for hour in range(6, 24):
            # Time label
            time_str = f"{hour:02d}:00"
            if hour < 12:
                display_time = f"{hour}:00 AM" if hour != 0 else "12:00 AM"
            elif hour == 12:
                display_time = "12:00 PM"
            else:
                display_time = f"{hour-12}:00 PM"

            time_frame = ctk.CTkFrame(day_frame, fg_color="transparent")
            time_frame.grid(row=hour-6, column=0, sticky="nsew", pady=2)

            time_label = ctk.CTkLabel(
                time_frame,
                text=display_time,
                font=ctk.CTkFont(size=11, weight="bold"),
                width=80,
                anchor="e"
            )
            time_label.pack(padx=10, pady=5)

            # Task slot
            task_slot = ctk.CTkFrame(day_frame, corner_radius=8, height=50)
            task_slot.grid(row=hour-6, column=1, sticky="ew", padx=(10, 0), pady=2)
            task_slot.grid_columnconfigure(0, weight=1)

            # Tasks for this hour
            hour_tasks = [t for t in day_tasks if t.due_time and t.due_time.hour == hour]

            if hour_tasks:
                for task_idx, task in enumerate(hour_tasks):
                    task_widget = ctk.CTkFrame(task_slot, corner_radius=6)
                    task_widget.grid(row=task_idx, column=0, sticky="ew", padx=5, pady=2)
                    task_widget.grid_columnconfigure(0, weight=1)

                    # Task content
                    task_content = ctk.CTkFrame(task_widget, fg_color="transparent")
                    task_content.grid(row=0, column=0, sticky="ew", padx=8, pady=6)
                    task_content.grid_columnconfigure(0, weight=1)

                    # Task title with time
                    if task.due_time and hasattr(task.due_time, 'strftime'):
                        title_text = f"{task.due_time.strftime('%H:%M')} - {task.title}"
                    else:
                        title_text = task.title
                    task_title = ctk.CTkLabel(
                        task_content,
                        text=title_text,
                        font=ctk.CTkFont(size=12, weight="bold"),
                        anchor="w"
                    )
                    task_title.grid(row=0, column=0, sticky="ew")

                    # Task description (if exists)
                    if task.description:
                        desc_text = task.description[:50] + "..." if len(task.description) > 50 else task.description
                        task_desc = ctk.CTkLabel(
                            task_content,
                            text=desc_text,
                            font=ctk.CTkFont(size=10),
                            text_color="gray",
                            anchor="w"
                        )
                        task_desc.grid(row=1, column=0, sticky="ew", pady=(2, 0))

                    # Priority indicator
                    try:
                        priority = Priority.get_by_id(task.priority_id)
                        if priority:
                            priority_badge = ctk.CTkLabel(
                                task_content,
                                text=priority.name,
                                font=ctk.CTkFont(size=8),
                                fg_color=priority.color,
                                corner_radius=8,
                                width=60,
                                height=20
                            )
                            priority_badge.grid(row=0, column=1, padx=(10, 0), sticky="e")
                    except:
                        pass
            else:
                # Empty slot
                empty_label = ctk.CTkLabel(
                    task_slot,
                    text="",
                    height=30
                )
                empty_label.pack()

    def create_task_details_panel(self):
        """Create modern task details panel"""
        details_frame = ctk.CTkFrame(self, corner_radius=15)
        details_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=5)
        details_frame.grid_columnconfigure(0, weight=1)
        details_frame.grid_rowconfigure(1, weight=1)

        # Details header
        details_header = ctk.CTkFrame(details_frame, fg_color="transparent")
        details_header.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 10))
        details_header.grid_columnconfigure(0, weight=1)

        # Header icon and title
        header_content = ctk.CTkFrame(details_header, fg_color="transparent")
        header_content.grid(row=0, column=0, sticky="ew")
        header_content.grid_columnconfigure(0, weight=1)

        self.details_title = ctk.CTkLabel(
            header_content,
            text="📋 Task Details",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.details_title.grid(row=0, column=0, sticky="w")

        self.details_subtitle = ctk.CTkLabel(
            header_content,
            text="Select a date to view tasks",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.details_subtitle.grid(row=1, column=0, sticky="w", pady=(2, 0))

        # Task list container
        list_container = ctk.CTkFrame(details_frame, corner_radius=10)
        list_container.grid(row=1, column=0, sticky="nsew", padx=15, pady=(10, 15))
        list_container.grid_columnconfigure(0, weight=1)
        list_container.grid_rowconfigure(0, weight=1)

        # Task list for selected date
        self.task_details_frame = ctk.CTkScrollableFrame(list_container)
        self.task_details_frame.pack(fill="both", expand=True, padx=10, pady=(10, 5))
        self.task_details_frame.grid_columnconfigure(0, weight=1)

        # Pagination controls for tasks
        self.create_task_pagination_controls(list_container)

        self.update_task_details()

    def create_task_pagination_controls(self, parent):
        """Create pagination controls for task details"""
        self.task_pagination_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.task_pagination_frame.pack(fill="x", padx=10, pady=(5, 10))

        # Page size selector
        page_size_frame = ctk.CTkFrame(self.task_pagination_frame, fg_color="transparent")
        page_size_frame.pack(side="left")

        ctk.CTkLabel(
            page_size_frame,
            text="Show:",
            font=ctk.CTkFont(size=10)
        ).pack(side="left", padx=(0, 5))

        self.task_page_size_var = tk.StringVar(value="5")
        task_page_combo = ctk.CTkComboBox(
            page_size_frame,
            variable=self.task_page_size_var,
            values=["3", "5", "10", "20"],
            command=self.change_task_page_size,
            width=60,
            height=25
        )
        task_page_combo.pack(side="left")

        # Navigation controls
        nav_frame = ctk.CTkFrame(self.task_pagination_frame, fg_color="transparent")
        nav_frame.pack(side="right")

        # Previous button
        self.task_prev_btn = ctk.CTkButton(
            nav_frame,
            text="◀",
            command=self.previous_task_page,
            width=30,
            height=25,
            state="disabled"
        )
        self.task_prev_btn.pack(side="left", padx=(0, 5))

        # Page info
        self.task_page_info_label = ctk.CTkLabel(
            nav_frame,
            text="1/1",
            font=ctk.CTkFont(size=10)
        )
        self.task_page_info_label.pack(side="left", padx=5)

        # Next button
        self.task_next_btn = ctk.CTkButton(
            nav_frame,
            text="▶",
            command=self.next_task_page,
            width=30,
            height=25,
            state="disabled"
        )
        self.task_next_btn.pack(side="left", padx=(5, 0))

    def mark_task_dates(self):
        """Mark dates that have tasks on the calendar"""
        if hasattr(self, 'calendar_widget'):
            # Get all task dates for current month
            task_dates = set()
            for task in self.tasks:
                if (task.due_date and
                    task.due_date.year == self.current_date.year and
                    task.due_date.month == self.current_date.month):
                    task_dates.add(task.due_date)

            # Mark dates (this is a simplified approach)
            for task_date in task_dates:
                try:
                    self.calendar_widget.calevent_create(task_date, "Tasks", "task_marker")
                except:
                    pass

    def on_date_selected(self, event=None):
        """Handle calendar date selection"""
        if hasattr(self, 'calendar_widget'):
            selected = self.calendar_widget.selection_get()
            self.selected_date = selected
            self.task_page = 1  # Reset to first page when date changes
            self.update_task_details()

    def update_task_details(self):
        """Update task details for selected date"""
        # Clear existing details
        for widget in self.task_details_frame.winfo_children():
            widget.destroy()

        # Update subtitle with selected date
        self.details_subtitle.configure(
            text=f"Tasks for {self.selected_date.strftime('%A, %B %d, %Y')}"
        )

        # Get tasks for selected date
        selected_tasks = [t for t in self.tasks if t.due_date == self.selected_date]
        selected_tasks.sort(key=lambda x: (x.due_time or time(0, 0), x.title))

        # Calculate pagination
        total_tasks = len(selected_tasks)
        start_index = (self.task_page - 1) * self.task_page_size
        end_index = min(start_index + self.task_page_size, total_tasks)
        page_tasks = selected_tasks[start_index:end_index]

        # Update pagination controls
        self.update_task_pagination(total_tasks)

        if not selected_tasks:
            # Empty state with better design
            empty_container = ctk.CTkFrame(self.task_details_frame, fg_color="transparent")
            empty_container.pack(expand=True, fill="both", pady=50)

            empty_icon = ctk.CTkLabel(
                empty_container,
                text="📅",
                font=ctk.CTkFont(size=48)
            )
            empty_icon.pack(pady=(20, 10))

            empty_title = ctk.CTkLabel(
                empty_container,
                text="No tasks scheduled",
                font=ctk.CTkFont(size=16, weight="bold")
            )
            empty_title.pack(pady=5)

            empty_desc = ctk.CTkLabel(
                empty_container,
                text="Click '+ Add Task' to schedule\nsomething for this date",
                font=ctk.CTkFont(size=11),
                text_color="gray",
                justify="center"
            )
            empty_desc.pack(pady=5)
        else:
            # Task count header
            if total_tasks > 0:
                count_text = f"Showing {start_index + 1}-{end_index} of {total_tasks} task{'s' if total_tasks != 1 else ''}"
            else:
                count_text = "No tasks scheduled"

            count_label = ctk.CTkLabel(
                self.task_details_frame,
                text=count_text,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="gray"
            )
            count_label.pack(pady=(0, 10), anchor="w")

            for i, task in enumerate(page_tasks):
                self.create_task_detail_widget(task, i)

    def create_task_detail_widget(self, task, index):
        """Create modern widget for task details"""
        task_frame = ctk.CTkFrame(self.task_details_frame, corner_radius=12)
        task_frame.pack(fill="x", padx=0, pady=8)
        task_frame.grid_columnconfigure(0, weight=1)

        # Main content frame
        content_frame = ctk.CTkFrame(task_frame, fg_color="transparent")
        content_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=12)
        content_frame.grid_columnconfigure(0, weight=1)

        # Header with time, title, and status
        header_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1)

        # Time badge
        if task.due_time and hasattr(task.due_time, 'strftime'):
            time_badge = ctk.CTkLabel(
                header_frame,
                text=task.due_time.strftime('%H:%M'),
                font=ctk.CTkFont(size=10, weight="bold"),
                fg_color=("gray80", "gray30"),
                corner_radius=8,
                width=50,
                height=24
            )
            time_badge.grid(row=0, column=0, sticky="w", padx=(0, 10))

        # Task title
        title_label = ctk.CTkLabel(
            header_frame,
            text=task.title,
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        title_label.grid(row=0, column=1, sticky="ew")

        # Status badge
        status_colors = {
            "pending": ("#ff9500", "#ff9500"),
            "in_progress": ("#007aff", "#007aff"),
            "completed": ("#34c759", "#34c759"),
            "cancelled": ("#ff3b30", "#ff3b30")
        }

        status_color = status_colors.get(task.status, ("#8e8e93", "#8e8e93"))
        status_label = ctk.CTkLabel(
            header_frame,
            text=task.status.replace("_", " ").title(),
            font=ctk.CTkFont(size=9, weight="bold"),
            fg_color=status_color,
            text_color="white",
            corner_radius=10,
            width=70,
            height=22
        )
        status_label.grid(row=0, column=2, sticky="e", padx=(10, 0))

        # Description
        if task.description:
            desc_label = ctk.CTkLabel(
                content_frame,
                text=task.description[:120] + "..." if len(task.description) > 120 else task.description,
                font=ctk.CTkFont(size=11),
                text_color="gray",
                anchor="w",
                justify="left"
            )
            desc_label.grid(row=1, column=0, sticky="ew", pady=(8, 0))

        # Priority and category info
        info_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        info_frame.grid(row=2, column=0, sticky="ew", pady=(8, 0))

        info_items = []

        # Priority
        try:
            priority = Priority.get_by_id(task.priority_id)
            if priority:
                info_items.append(f"Priority: {priority.name}")
        except:
            pass

        # Duration
        if task.estimated_duration:
            info_items.append(f"Duration: {task.estimated_duration} min")

        if info_items:
            info_label = ctk.CTkLabel(
                info_frame,
                text=" • ".join(info_items),
                font=ctk.CTkFont(size=10),
                text_color="gray",
                anchor="w"
            )
            info_label.pack(side="left")

        # Action buttons
        actions_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        actions_frame.grid(row=3, column=0, sticky="ew", pady=(10, 0))

        # Edit button
        edit_btn = ctk.CTkButton(
            actions_frame,
            text="✏️ Edit",
            command=lambda t=task: self.edit_task(t),
            width=70,
            height=28,
            font=ctk.CTkFont(size=10),
            fg_color=("gray75", "gray25"),
            hover_color=("gray65", "gray35")
        )
        edit_btn.pack(side="left", padx=(0, 8))

        # Complete/Uncomplete button
        if task.status != "completed":
            complete_btn = ctk.CTkButton(
                actions_frame,
                text="✅ Complete",
                command=lambda t=task: self.complete_task(t),
                width=90,
                height=28,
                font=ctk.CTkFont(size=10),
                fg_color="#34c759",
                hover_color="#30b855"
            )
            complete_btn.pack(side="left", padx=(0, 8))
        else:
            uncomplete_btn = ctk.CTkButton(
                actions_frame,
                text="↩️ Reopen",
                command=lambda t=task: self.reopen_task(t),
                width=80,
                height=28,
                font=ctk.CTkFont(size=10),
                fg_color="#ff9500",
                hover_color="#e6850e"
            )
            uncomplete_btn.pack(side="left", padx=(0, 8))

    def update_task_pagination(self, total_tasks):
        """Update task pagination controls"""
        self.total_task_pages = max(1, (total_tasks + self.task_page_size - 1) // self.task_page_size)

        # Ensure current page is valid
        if self.task_page > self.total_task_pages:
            self.task_page = self.total_task_pages

        # Update page info label
        if hasattr(self, 'task_page_info_label'):
            self.task_page_info_label.configure(text=f"{self.task_page}/{self.total_task_pages}")

        # Update button states
        if hasattr(self, 'task_prev_btn'):
            self.task_prev_btn.configure(state="normal" if self.task_page > 1 else "disabled")
        if hasattr(self, 'task_next_btn'):
            self.task_next_btn.configure(state="normal" if self.task_page < self.total_task_pages else "disabled")

    def change_task_page_size(self, value):
        """Change the number of tasks per page in calendar view"""
        try:
            self.task_page_size = int(value)
            self.task_page = 1  # Reset to first page
            self.update_task_details()
        except ValueError:
            pass

    def next_task_page(self):
        """Go to next task page"""
        if self.task_page < self.total_task_pages:
            self.task_page += 1
            self.update_task_details()

    def previous_task_page(self):
        """Go to previous task page"""
        if self.task_page > 1:
            self.task_page -= 1
            self.update_task_details()

    def update_period_label(self):
        """Update the period label based on current view"""
        if self.view_mode == "month":
            self.period_label.configure(text=self.current_date.strftime("%B %Y"))
        elif self.view_mode == "week":
            start_of_week = self.current_date - timedelta(days=self.current_date.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            self.period_label.configure(text=f"{start_of_week.strftime('%b %d')} - {end_of_week.strftime('%b %d, %Y')}")
        else:  # day
            self.period_label.configure(text=self.current_date.strftime("%A, %B %d, %Y"))

    def previous_period(self):
        """Navigate to previous period"""
        if self.view_mode == "month":
            if self.current_date.month == 1:
                self.current_date = self.current_date.replace(year=self.current_date.year - 1, month=12)
            else:
                self.current_date = self.current_date.replace(month=self.current_date.month - 1)
        elif self.view_mode == "week":
            self.current_date -= timedelta(weeks=1)
        else:  # day
            self.current_date -= timedelta(days=1)

        self.update_period_label()
        self.create_calendar_widget()

    def next_period(self):
        """Navigate to next period"""
        if self.view_mode == "month":
            if self.current_date.month == 12:
                self.current_date = self.current_date.replace(year=self.current_date.year + 1, month=1)
            else:
                self.current_date = self.current_date.replace(month=self.current_date.month + 1)
        elif self.view_mode == "week":
            self.current_date += timedelta(weeks=1)
        else:  # day
            self.current_date += timedelta(days=1)

        self.update_period_label()
        self.create_calendar_widget()

    def go_to_today(self):
        """Navigate to today"""
        self.current_date = date.today()
        self.selected_date = date.today()
        self.update_period_label()
        self.create_calendar_widget()
        self.update_task_details()

    def change_view_mode(self, mode):
        """Change calendar view mode"""
        self.view_mode = mode.lower()  # Convert to lowercase for internal use
        self.update_period_label()
        self.create_calendar_widget()

    def add_task_for_date(self):
        """Add task for selected date"""
        dialog = TaskDialog(self)
        if dialog.result:
            # Set the due date to selected date
            task = dialog.result
            task.due_date = self.selected_date
            task.save()
            self.refresh_data()
            self.main_window.update_quick_stats()

    def edit_task(self, task):
        """Edit selected task"""
        dialog = TaskDialog(self, task=task)
        if dialog.result:
            self.refresh_data()
            self.main_window.update_quick_stats()

    def complete_task(self, task):
        """Mark task as completed"""
        try:
            task.mark_completed()
            # Send completion notification
            if NOTIFICATIONS_AVAILABLE and notification_manager:
                notification_manager.send_task_completion_notification(task)
            self.refresh_data()
            self.main_window.update_quick_stats()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to complete task: {e}")

    def reopen_task(self, task):
        """Reopen a completed task"""
        try:
            task.status = "pending"
            task.completed_at = None
            task.save()
            self.refresh_data()
            self.main_window.update_quick_stats()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reopen task: {e}")

    def load_tasks(self):
        """Load tasks from database"""
        try:
            self.tasks = Task.get_all()
            if hasattr(self, 'calendar_widget'):
                self.mark_task_dates()
            self.update_task_details()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load tasks: {e}")

    def refresh_data(self):
        """Refresh calendar data"""
        self.load_tasks()
        self.create_calendar_widget()
