"""
Analytics and reporting interface for Task Planner application
"""

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from datetime import datetime, date, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.task import Task
from models.category import Category, Priority
from models.goal import Goal

class AnalyticsFrame(ctk.CTkFrame):
    """Analytics and reporting interface"""

    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.main_window = main_window
        self.tasks = []
        self.goals = []
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """Setup analytics UI"""
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Create header
        self.create_header()

        # Create sidebar with options
        self.create_sidebar()

        # Create main analytics area
        self.create_analytics_area()

    def create_header(self):
        """Create header with title and controls"""
        header_frame = ctk.CTkFrame(self)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 5))
        header_frame.grid_columnconfigure(1, weight=1)

        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="Analytics & Reports",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")

        # Time period selector
        period_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        period_frame.grid(row=0, column=2, padx=20, pady=15, sticky="e")

        period_label = ctk.CTkLabel(period_frame, text="Time Period:")
        period_label.pack(side="left", padx=(0, 10))

        self.period_var = tk.StringVar(value="last_30_days")
        period_combo = ctk.CTkComboBox(
            period_frame,
            variable=self.period_var,
            values=["last_7_days", "last_30_days", "last_90_days", "this_year", "all_time"],
            command=self.update_analytics
        )
        period_combo.pack(side="left", padx=(0, 10))

        # Refresh button
        refresh_btn = ctk.CTkButton(
            period_frame,
            text="🔄 Refresh",
            command=self.refresh_data,
            width=100
        )
        refresh_btn.pack(side="left")

    def create_sidebar(self):
        """Create analytics options sidebar"""
        sidebar_frame = ctk.CTkFrame(self)
        sidebar_frame.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=5)
        sidebar_frame.grid_rowconfigure(10, weight=1)

        # Sidebar title
        sidebar_title = ctk.CTkLabel(
            sidebar_frame,
            text="Analytics",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        sidebar_title.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")

        # Analytics options
        self.analytics_var = tk.StringVar(value="overview")

        options = [
            ("overview", "📊 Overview"),
            ("productivity", "📈 Productivity"),
            ("categories", "📋 Categories"),
            ("priorities", "⚡ Priorities"),
            ("completion", "✅ Completion Rate"),
            ("goals", "🎯 Goals Progress")
        ]

        for i, (value, text) in enumerate(options):
            radio = ctk.CTkRadioButton(
                sidebar_frame,
                text=text,
                variable=self.analytics_var,
                value=value,
                command=self.update_analytics
            )
            radio.grid(row=i+1, column=0, padx=15, pady=5, sticky="w")

        # Quick stats
        self.create_quick_stats_sidebar()

    def create_quick_stats_sidebar(self):
        """Create quick statistics in sidebar"""
        stats_frame = ctk.CTkFrame(self.grid_slaves(row=1, column=0)[0])
        stats_frame.grid(row=8, column=0, padx=15, pady=(20, 10), sticky="ew")

        stats_title = ctk.CTkLabel(
            stats_frame,
            text="Quick Stats",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        stats_title.pack(pady=(10, 5))

        # Total tasks
        self.total_tasks_label = ctk.CTkLabel(
            stats_frame,
            text="Total Tasks: 0",
            font=ctk.CTkFont(size=12)
        )
        self.total_tasks_label.pack(pady=2)

        # Completed tasks
        self.completed_tasks_label = ctk.CTkLabel(
            stats_frame,
            text="Completed: 0",
            font=ctk.CTkFont(size=12)
        )
        self.completed_tasks_label.pack(pady=2)

        # Completion rate
        self.completion_rate_label = ctk.CTkLabel(
            stats_frame,
            text="Rate: 0%",
            font=ctk.CTkFont(size=12)
        )
        self.completion_rate_label.pack(pady=(2, 10))

    def create_analytics_area(self):
        """Create main analytics display area"""
        self.analytics_frame = ctk.CTkFrame(self)
        self.analytics_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=5)
        self.analytics_frame.grid_columnconfigure(0, weight=1)
        self.analytics_frame.grid_rowconfigure(0, weight=1)

        # Initial view
        self.show_overview()

    def get_filtered_tasks(self):
        """Get tasks filtered by selected time period"""
        period = self.period_var.get()
        today = date.today()

        if period == "last_7_days":
            start_date = today - timedelta(days=7)
        elif period == "last_30_days":
            start_date = today - timedelta(days=30)
        elif period == "last_90_days":
            start_date = today - timedelta(days=90)
        elif period == "this_year":
            start_date = date(today.year, 1, 1)
        else:  # all_time
            return self.tasks

        return [t for t in self.tasks if t.created_at and t.created_at.date() >= start_date]

    def update_analytics(self, *args):
        """Update analytics display based on selection"""
        analytics_type = self.analytics_var.get()

        # Clear current display
        for widget in self.analytics_frame.winfo_children():
            widget.destroy()

        # Show selected analytics
        if analytics_type == "overview":
            self.show_overview()
        elif analytics_type == "productivity":
            self.show_productivity()
        elif analytics_type == "categories":
            self.show_categories()
        elif analytics_type == "priorities":
            self.show_priorities()
        elif analytics_type == "completion":
            self.show_completion_rate()
        elif analytics_type == "goals":
            self.show_goals_progress()

    def show_overview(self):
        """Show overview analytics"""
        # Create scrollable frame
        overview_frame = ctk.CTkScrollableFrame(self.analytics_frame)
        overview_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Title
        title_label = ctk.CTkLabel(
            overview_frame,
            text="Overview Dashboard",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(10, 20))

        # Get filtered tasks
        filtered_tasks = self.get_filtered_tasks()

        # Statistics cards
        stats_container = ctk.CTkFrame(overview_frame)
        stats_container.pack(fill="x", padx=10, pady=10)
        stats_container.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Total tasks card
        total_card = self.create_stat_card(stats_container, "Total Tasks", len(filtered_tasks), "📋")
        total_card.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # Completed tasks
        completed_tasks = [t for t in filtered_tasks if t.status == "completed"]
        completed_card = self.create_stat_card(stats_container, "Completed", len(completed_tasks), "✅")
        completed_card.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Pending tasks
        pending_tasks = [t for t in filtered_tasks if t.status == "pending"]
        pending_card = self.create_stat_card(stats_container, "Pending", len(pending_tasks), "⏳")
        pending_card.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # Overdue tasks
        overdue_tasks = Task.get_overdue()
        overdue_card = self.create_stat_card(stats_container, "Overdue", len(overdue_tasks), "🚨")
        overdue_card.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        # Charts container
        charts_frame = ctk.CTkFrame(overview_frame)
        charts_frame.pack(fill="both", expand=True, padx=10, pady=20)
        charts_frame.grid_columnconfigure((0, 1), weight=1)
        charts_frame.grid_rowconfigure(0, weight=1)

        # Task status pie chart
        self.create_status_pie_chart(charts_frame, filtered_tasks)

        # Daily completion chart
        self.create_daily_completion_chart(charts_frame, filtered_tasks)

    def create_stat_card(self, parent, title, value, icon):
        """Create a statistics card"""
        card = ctk.CTkFrame(parent)

        # Icon
        icon_label = ctk.CTkLabel(
            card,
            text=icon,
            font=ctk.CTkFont(size=24)
        )
        icon_label.pack(pady=(15, 5))

        # Value
        value_label = ctk.CTkLabel(
            card,
            text=str(value),
            font=ctk.CTkFont(size=28, weight="bold")
        )
        value_label.pack(pady=5)

        # Title
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        title_label.pack(pady=(5, 15))

        return card

    def create_status_pie_chart(self, parent, tasks):
        """Create task status pie chart"""
        chart_frame = ctk.CTkFrame(parent)
        chart_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # Chart title
        title_label = ctk.CTkLabel(
            chart_frame,
            text="Task Status Distribution",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.pack(pady=(10, 5))

        # Prepare data
        status_counts = {}
        for task in tasks:
            status_counts[task.status] = status_counts.get(task.status, 0) + 1

        if not status_counts:
            no_data_label = ctk.CTkLabel(chart_frame, text="No data available")
            no_data_label.pack(pady=50)
            return

        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(6, 4))
        fig.patch.set_facecolor('#212121')
        ax.set_facecolor('#212121')

        labels = list(status_counts.keys())
        sizes = list(status_counts.values())
        colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']

        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)

        # Style text
        for text in texts:
            text.set_color('white')
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_weight('bold')

        ax.set_title('Task Status Distribution', color='white', fontweight='bold')

        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def create_daily_completion_chart(self, parent, tasks):
        """Create daily task completion chart"""
        chart_frame = ctk.CTkFrame(parent)
        chart_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        # Chart title
        title_label = ctk.CTkLabel(
            chart_frame,
            text="Daily Completion Trend",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.pack(pady=(10, 5))

        # Prepare data for last 7 days
        today = date.today()
        dates = [today - timedelta(days=i) for i in range(6, -1, -1)]
        completions = []

        for date_item in dates:
            day_completions = len([
                t for t in tasks
                if t.completed_at and t.completed_at.date() == date_item
            ])
            completions.append(day_completions)

        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(6, 4))
        fig.patch.set_facecolor('#212121')
        ax.set_facecolor('#212121')

        ax.plot(dates, completions, marker='o', linewidth=2, markersize=6, color='#66b3ff')
        ax.fill_between(dates, completions, alpha=0.3, color='#66b3ff')

        # Style
        ax.set_title('Daily Task Completions', color='white', fontweight='bold')
        ax.set_xlabel('Date', color='white')
        ax.set_ylabel('Completed Tasks', color='white')
        ax.tick_params(colors='white')
        ax.grid(True, alpha=0.3)

        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

        plt.tight_layout()

        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def show_productivity(self):
        """Show productivity analytics"""
        productivity_frame = ctk.CTkScrollableFrame(self.analytics_frame)
        productivity_frame.pack(fill="both", expand=True, padx=10, pady=10)

        title_label = ctk.CTkLabel(
            productivity_frame,
            text="📈 Productivity Analysis",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(10, 20))

        # Get filtered tasks for analysis
        filtered_tasks = self.get_filtered_tasks()
        completed_tasks = [t for t in filtered_tasks if t.status == "completed" and t.completed_at]

        if not completed_tasks:
            no_data_label = ctk.CTkLabel(
                productivity_frame,
                text="📊 No completed tasks found for the selected period.\nComplete some tasks to see productivity insights!",
                font=ctk.CTkFont(size=14),
                text_color="gray"
            )
            no_data_label.pack(pady=50)
            return

        # Create productivity metrics cards
        self.create_productivity_metrics(productivity_frame, completed_tasks)

        # Create charts container
        charts_container = ctk.CTkFrame(productivity_frame)
        charts_container.pack(fill="both", expand=True, padx=10, pady=20)
        charts_container.grid_columnconfigure((0, 1), weight=1)
        charts_container.grid_rowconfigure((0, 1), weight=1)

        # Peak productivity hours chart
        self.create_peak_hours_chart(charts_container, completed_tasks)

        # Weekly trends chart
        self.create_weekly_trends_chart(charts_container, completed_tasks)

        # Task difficulty analysis
        self.create_difficulty_analysis(charts_container, completed_tasks)

        # Completion time trends
        self.create_completion_time_chart(charts_container, completed_tasks)

    def create_productivity_metrics(self, parent, completed_tasks):
        """Create productivity metrics cards"""
        metrics_frame = ctk.CTkFrame(parent)
        metrics_frame.pack(fill="x", padx=10, pady=10)
        metrics_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Calculate metrics
        avg_completion_time = self.calculate_average_completion_time(completed_tasks)
        peak_hour = self.calculate_peak_productivity_hour(completed_tasks)
        weekly_avg = self.calculate_weekly_average(completed_tasks)
        difficulty_score = self.calculate_difficulty_score(completed_tasks)

        # Average completion time card
        avg_time_card = self.create_metric_card(
            metrics_frame,
            "⏱️ Avg Completion Time",
            avg_completion_time,
            "Time from creation to completion"
        )
        avg_time_card.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # Peak productivity hour card
        peak_hour_card = self.create_metric_card(
            metrics_frame,
            "🌟 Peak Hour",
            peak_hour,
            "Most productive time of day"
        )
        peak_hour_card.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Weekly average card
        weekly_card = self.create_metric_card(
            metrics_frame,
            "📅 Weekly Average",
            f"{weekly_avg:.1f}",
            "Tasks completed per week"
        )
        weekly_card.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # Difficulty score card
        difficulty_card = self.create_metric_card(
            metrics_frame,
            "🎯 Difficulty Score",
            f"{difficulty_score:.1f}/10",
            "Average task complexity"
        )
        difficulty_card.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

    def create_metric_card(self, parent, title, value, description):
        """Create a metric card with title, value, and description"""
        card = ctk.CTkFrame(parent)

        # Title
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        title_label.pack(pady=(15, 5))

        # Value
        value_label = ctk.CTkLabel(
            card,
            text=str(value),
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#4CAF50"
        )
        value_label.pack(pady=5)

        # Description
        desc_label = ctk.CTkLabel(
            card,
            text=description,
            font=ctk.CTkFont(size=10),
            text_color="gray",
            wraplength=120
        )
        desc_label.pack(pady=(5, 15))

        return card

    def calculate_average_completion_time(self, completed_tasks):
        """Calculate average time from creation to completion"""
        if not completed_tasks:
            return "N/A"

        total_hours = 0
        valid_tasks = 0

        for task in completed_tasks:
            if task.created_at and task.completed_at:
                time_diff = task.completed_at - task.created_at
                total_hours += time_diff.total_seconds() / 3600
                valid_tasks += 1

        if valid_tasks == 0:
            return "N/A"

        avg_hours = total_hours / valid_tasks

        if avg_hours < 1:
            return f"{int(avg_hours * 60)}m"
        elif avg_hours < 24:
            return f"{avg_hours:.1f}h"
        else:
            return f"{avg_hours / 24:.1f}d"

    def calculate_peak_productivity_hour(self, completed_tasks):
        """Calculate the hour of day when most tasks are completed"""
        if not completed_tasks:
            return "N/A"

        hour_counts = {}
        for task in completed_tasks:
            if task.completed_at:
                hour = task.completed_at.hour
                hour_counts[hour] = hour_counts.get(hour, 0) + 1

        if not hour_counts:
            return "N/A"

        peak_hour = max(hour_counts, key=hour_counts.get)

        # Format hour in 12-hour format
        if peak_hour == 0:
            return "12 AM"
        elif peak_hour < 12:
            return f"{peak_hour} AM"
        elif peak_hour == 12:
            return "12 PM"
        else:
            return f"{peak_hour - 12} PM"

    def calculate_weekly_average(self, completed_tasks):
        """Calculate average tasks completed per week"""
        if not completed_tasks:
            return 0.0

        # Get date range
        dates = [task.completed_at.date() for task in completed_tasks if task.completed_at]
        if not dates:
            return 0.0

        min_date = min(dates)
        max_date = max(dates)

        # Calculate number of weeks
        days_diff = (max_date - min_date).days
        weeks = max(days_diff / 7, 1)  # At least 1 week

        return len(completed_tasks) / weeks

    def calculate_difficulty_score(self, completed_tasks):
        """Calculate average task difficulty based on priority and completion time"""
        if not completed_tasks:
            return 0.0

        total_score = 0
        valid_tasks = 0

        for task in completed_tasks:
            score = 5.0  # Base score

            # Priority factor (1-10 scale)
            if hasattr(task, 'priority_id') and task.priority_id:
                try:
                    from models.category import Priority
                    priority = Priority.get_by_id(task.priority_id)
                    if priority:
                        if priority.name.lower() == 'low':
                            score += 1
                        elif priority.name.lower() == 'medium':
                            score += 3
                        elif priority.name.lower() == 'high':
                            score += 5
                        elif priority.name.lower() == 'urgent':
                            score += 7
                except:
                    pass

            # Completion time factor
            if task.created_at and task.completed_at:
                time_diff = task.completed_at - task.created_at
                hours = time_diff.total_seconds() / 3600

                if hours > 168:  # More than a week
                    score += 2
                elif hours > 24:  # More than a day
                    score += 1

            # Description length factor (complexity indicator)
            if task.description and len(task.description) > 100:
                score += 1

            total_score += min(score, 10)  # Cap at 10
            valid_tasks += 1

        return total_score / valid_tasks if valid_tasks > 0 else 0.0

    def create_peak_hours_chart(self, parent, completed_tasks):
        """Create peak productivity hours chart"""
        chart_frame = ctk.CTkFrame(parent)
        chart_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # Chart title
        title_label = ctk.CTkLabel(
            chart_frame,
            text="🌟 Peak Productivity Hours",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.pack(pady=(10, 5))

        # Prepare data
        hour_counts = {}
        for task in completed_tasks:
            if task.completed_at:
                hour = task.completed_at.hour
                hour_counts[hour] = hour_counts.get(hour, 0) + 1

        if not hour_counts:
            no_data_label = ctk.CTkLabel(chart_frame, text="No completion time data")
            no_data_label.pack(pady=50)
            return

        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(6, 4))
        fig.patch.set_facecolor('#212121')
        ax.set_facecolor('#212121')

        # Prepare data for all 24 hours
        hours = list(range(24))
        counts = [hour_counts.get(hour, 0) for hour in hours]

        # Create bar chart
        bars = ax.bar(hours, counts, color='#4CAF50', alpha=0.7)

        # Highlight peak hour
        if counts:
            peak_hour = hours[counts.index(max(counts))]
            bars[peak_hour].set_color('#FF9800')

        # Style
        ax.set_title('Tasks Completed by Hour of Day', color='white', fontweight='bold')
        ax.set_xlabel('Hour of Day', color='white')
        ax.set_ylabel('Tasks Completed', color='white')
        ax.tick_params(colors='white')
        ax.grid(True, alpha=0.3)

        # Format x-axis
        ax.set_xticks(range(0, 24, 3))
        ax.set_xticklabels([f'{h}:00' for h in range(0, 24, 3)])

        plt.tight_layout()

        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def create_weekly_trends_chart(self, parent, completed_tasks):
        """Create weekly productivity trends chart"""
        chart_frame = ctk.CTkFrame(parent)
        chart_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        # Chart title
        title_label = ctk.CTkLabel(
            chart_frame,
            text="📅 Weekly Productivity Trends",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.pack(pady=(10, 5))

        # Prepare data for last 8 weeks
        today = date.today()
        weeks_data = []
        week_labels = []

        for i in range(7, -1, -1):
            week_start = today - timedelta(days=today.weekday() + 7*i)
            week_end = week_start + timedelta(days=6)

            week_tasks = [
                t for t in completed_tasks
                if t.completed_at and week_start <= t.completed_at.date() <= week_end
            ]

            weeks_data.append(len(week_tasks))
            week_labels.append(f"{week_start.strftime('%m/%d')}")

        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(6, 4))
        fig.patch.set_facecolor('#212121')
        ax.set_facecolor('#212121')

        # Create line chart
        ax.plot(week_labels, weeks_data, marker='o', linewidth=3, markersize=8, color='#2196F3')
        ax.fill_between(week_labels, weeks_data, alpha=0.3, color='#2196F3')

        # Style
        ax.set_title('Weekly Task Completion Trend', color='white', fontweight='bold')
        ax.set_xlabel('Week Starting', color='white')
        ax.set_ylabel('Tasks Completed', color='white')
        ax.tick_params(colors='white')
        ax.grid(True, alpha=0.3)

        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        plt.tight_layout()

        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def create_difficulty_analysis(self, parent, completed_tasks):
        """Create task difficulty analysis chart"""
        chart_frame = ctk.CTkFrame(parent)
        chart_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        # Chart title
        title_label = ctk.CTkLabel(
            chart_frame,
            text="🎯 Task Difficulty Distribution",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.pack(pady=(10, 5))

        # Calculate difficulty scores for each task
        difficulty_scores = []
        for task in completed_tasks:
            score = 5.0  # Base score

            # Priority factor
            if hasattr(task, 'priority_id') and task.priority_id:
                try:
                    from models.category import Priority
                    priority = Priority.get_by_id(task.priority_id)
                    if priority:
                        if priority.name.lower() == 'low':
                            score += 1
                        elif priority.name.lower() == 'medium':
                            score += 3
                        elif priority.name.lower() == 'high':
                            score += 5
                        elif priority.name.lower() == 'urgent':
                            score += 7
                except:
                    pass

            # Completion time factor
            if task.created_at and task.completed_at:
                time_diff = task.completed_at - task.created_at
                hours = time_diff.total_seconds() / 3600

                if hours > 168:  # More than a week
                    score += 2
                elif hours > 24:  # More than a day
                    score += 1

            # Description length factor
            if task.description and len(task.description) > 100:
                score += 1

            difficulty_scores.append(min(score, 10))

        if not difficulty_scores:
            no_data_label = ctk.CTkLabel(chart_frame, text="No difficulty data")
            no_data_label.pack(pady=50)
            return

        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(6, 4))
        fig.patch.set_facecolor('#212121')
        ax.set_facecolor('#212121')

        # Create histogram
        bins = [0, 2, 4, 6, 8, 10]
        counts, _, patches = ax.hist(difficulty_scores, bins=bins, color='#9C27B0', alpha=0.7, edgecolor='white')

        # Color code the bars
        colors = ['#4CAF50', '#8BC34A', '#FFC107', '#FF9800', '#F44336']
        for i, patch in enumerate(patches):
            if i < len(colors):
                patch.set_facecolor(colors[i])

        # Style
        ax.set_title('Task Difficulty Distribution', color='white', fontweight='bold')
        ax.set_xlabel('Difficulty Score', color='white')
        ax.set_ylabel('Number of Tasks', color='white')
        ax.tick_params(colors='white')
        ax.grid(True, alpha=0.3)

        # Set x-axis labels
        ax.set_xticks([1, 3, 5, 7, 9])
        ax.set_xticklabels(['Easy\n(0-2)', 'Medium\n(2-4)', 'Hard\n(4-6)', 'Very Hard\n(6-8)', 'Expert\n(8-10)'])

        plt.tight_layout()

        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def create_completion_time_chart(self, parent, completed_tasks):
        """Create completion time trends chart"""
        chart_frame = ctk.CTkFrame(parent)
        chart_frame.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

        # Chart title
        title_label = ctk.CTkLabel(
            chart_frame,
            text="⏱️ Completion Time Analysis",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.pack(pady=(10, 5))

        # Calculate completion times in hours
        completion_times = []
        for task in completed_tasks:
            if task.created_at and task.completed_at:
                time_diff = task.completed_at - task.created_at
                hours = time_diff.total_seconds() / 3600
                completion_times.append(hours)

        if not completion_times:
            no_data_label = ctk.CTkLabel(chart_frame, text="No completion time data")
            no_data_label.pack(pady=50)
            return

        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(6, 4))
        fig.patch.set_facecolor('#212121')
        ax.set_facecolor('#212121')

        # Create histogram with custom bins
        bins = [0, 1, 6, 24, 72, 168, max(completion_times) + 1]
        bin_labels = ['<1h', '1-6h', '6-24h', '1-3d', '3-7d', '>7d']

        counts, _, patches = ax.hist(completion_times, bins=bins, color='#FF5722', alpha=0.7, edgecolor='white')

        # Color code the bars
        colors = ['#4CAF50', '#8BC34A', '#FFC107', '#FF9800', '#F44336', '#9C27B0']
        for i, patch in enumerate(patches):
            if i < len(colors):
                patch.set_facecolor(colors[i])

        # Style
        ax.set_title('Task Completion Time Distribution', color='white', fontweight='bold')
        ax.set_xlabel('Completion Time', color='white')
        ax.set_ylabel('Number of Tasks', color='white')
        ax.tick_params(colors='white')
        ax.grid(True, alpha=0.3)

        # Set custom x-axis labels
        bin_centers = [(bins[i] + bins[i+1]) / 2 for i in range(len(bins)-1)]
        ax.set_xticks(bin_centers)
        ax.set_xticklabels(bin_labels)

        plt.tight_layout()

        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def show_categories(self):
        """Show category analytics"""
        categories_frame = ctk.CTkScrollableFrame(self.analytics_frame)
        categories_frame.pack(fill="both", expand=True, padx=10, pady=10)

        title_label = ctk.CTkLabel(
            categories_frame,
            text="Category Analysis",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(10, 20))

        # Get category statistics
        filtered_tasks = self.get_filtered_tasks()
        categories = Category.get_all()

        # Create category stats
        for category in categories:
            category_tasks = [t for t in filtered_tasks if t.category_id == category.id]
            completed_tasks = [t for t in category_tasks if t.status == "completed"]

            # Category card
            cat_frame = ctk.CTkFrame(categories_frame)
            cat_frame.pack(fill="x", padx=10, pady=5)
            cat_frame.grid_columnconfigure(1, weight=1)

            # Category name and color
            color_frame = ctk.CTkFrame(cat_frame, fg_color=category.color, width=20, height=50)
            color_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ns")

            # Stats
            stats_frame = ctk.CTkFrame(cat_frame, fg_color="transparent")
            stats_frame.grid(row=0, column=1, sticky="ew", padx=10, pady=10)

            name_label = ctk.CTkLabel(
                stats_frame,
                text=category.name,
                font=ctk.CTkFont(size=16, weight="bold")
            )
            name_label.pack(anchor="w")

            total_label = ctk.CTkLabel(
                stats_frame,
                text=f"Total: {len(category_tasks)} tasks",
                font=ctk.CTkFont(size=12)
            )
            total_label.pack(anchor="w")

            completed_label = ctk.CTkLabel(
                stats_frame,
                text=f"Completed: {len(completed_tasks)} tasks",
                font=ctk.CTkFont(size=12)
            )
            completed_label.pack(anchor="w")

            if len(category_tasks) > 0:
                completion_rate = (len(completed_tasks) / len(category_tasks)) * 100
                rate_label = ctk.CTkLabel(
                    stats_frame,
                    text=f"Completion Rate: {completion_rate:.1f}%",
                    font=ctk.CTkFont(size=12),
                    text_color="green" if completion_rate >= 70 else "orange" if completion_rate >= 50 else "red"
                )
                rate_label.pack(anchor="w")

    def show_priorities(self):
        """Show priority analytics"""
        priorities_frame = ctk.CTkScrollableFrame(self.analytics_frame)
        priorities_frame.pack(fill="both", expand=True, padx=10, pady=10)

        title_label = ctk.CTkLabel(
            priorities_frame,
            text="🎯 Priority Analysis",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(10, 20))

        # Get priority statistics
        filtered_tasks = self.get_filtered_tasks()
        priorities = Priority.get_all()

        if not priorities:
            no_data_label = ctk.CTkLabel(
                priorities_frame,
                text="No priorities found.\nCreate priorities to see analysis!",
                font=ctk.CTkFont(size=14),
                text_color="gray"
            )
            no_data_label.pack(pady=50)
            return

        # Create priority stats container
        stats_container = ctk.CTkFrame(priorities_frame)
        stats_container.pack(fill="x", padx=10, pady=10)
        stats_container.grid_columnconfigure((0, 1), weight=1)

        # Priority distribution chart
        self.create_priority_distribution_chart(stats_container, filtered_tasks, priorities)

        # Priority completion chart
        self.create_priority_completion_chart(stats_container, filtered_tasks, priorities)

        # Priority details list
        details_frame = ctk.CTkFrame(priorities_frame)
        details_frame.pack(fill="x", padx=10, pady=20)

        details_title = ctk.CTkLabel(
            details_frame,
            text="📊 Priority Breakdown",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        details_title.pack(pady=(15, 10))

        # Create priority stats
        for priority in priorities:
            priority_tasks = [t for t in filtered_tasks if t.priority_id == priority.id]
            completed_tasks = [t for t in priority_tasks if t.status == "completed"]

            # Priority card
            priority_frame = ctk.CTkFrame(details_frame)
            priority_frame.pack(fill="x", padx=15, pady=8)
            priority_frame.grid_columnconfigure(1, weight=1)

            # Priority color indicator
            color_frame = ctk.CTkFrame(priority_frame, fg_color=priority.color, width=20, height=60)
            color_frame.grid(row=0, column=0, padx=15, pady=15, sticky="ns")

            # Stats
            stats_frame = ctk.CTkFrame(priority_frame, fg_color="transparent")
            stats_frame.grid(row=0, column=1, sticky="ew", padx=15, pady=15)

            # Priority name with icon
            priority_icons = {
                'low': '🟢',
                'medium': '🟡',
                'high': '🟠',
                'urgent': '🔴'
            }
            icon = priority_icons.get(priority.name.lower(), '📌')

            name_label = ctk.CTkLabel(
                stats_frame,
                text=f"{icon} {priority.name}",
                font=ctk.CTkFont(size=16, weight="bold")
            )
            name_label.pack(anchor="w")

            # Task counts
            total_label = ctk.CTkLabel(
                stats_frame,
                text=f"Total: {len(priority_tasks)} tasks",
                font=ctk.CTkFont(size=12)
            )
            total_label.pack(anchor="w")

            completed_label = ctk.CTkLabel(
                stats_frame,
                text=f"Completed: {len(completed_tasks)} tasks",
                font=ctk.CTkFont(size=12)
            )
            completed_label.pack(anchor="w")

            # Completion rate
            if len(priority_tasks) > 0:
                completion_rate = (len(completed_tasks) / len(priority_tasks)) * 100
                rate_color = "#4CAF50" if completion_rate >= 70 else "#FF9800" if completion_rate >= 50 else "#F44336"
                rate_label = ctk.CTkLabel(
                    stats_frame,
                    text=f"Completion Rate: {completion_rate:.1f}%",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=rate_color
                )
                rate_label.pack(anchor="w")

                # Progress bar
                progress_bar = ctk.CTkProgressBar(stats_frame, width=200, height=8)
                progress_bar.pack(anchor="w", pady=(5, 0))
                progress_bar.set(completion_rate / 100.0)

    def create_priority_distribution_chart(self, parent, tasks, priorities):
        """Create priority distribution pie chart"""
        chart_frame = ctk.CTkFrame(parent)
        chart_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # Chart title
        title_label = ctk.CTkLabel(
            chart_frame,
            text="📊 Task Distribution by Priority",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.pack(pady=(10, 5))

        # Count tasks by priority
        priority_counts = {}
        for priority in priorities:
            count = len([t for t in tasks if t.priority_id == priority.id])
            if count > 0:  # Only include priorities with tasks
                priority_counts[priority.name] = count

        if not priority_counts:
            no_data_label = ctk.CTkLabel(chart_frame, text="No priority data")
            no_data_label.pack(pady=50)
            return

        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(5, 4))
        fig.patch.set_facecolor('#212121')
        ax.set_facecolor('#212121')

        # Create pie chart
        labels = list(priority_counts.keys())
        sizes = list(priority_counts.values())
        colors = ['#4CAF50', '#FFC107', '#FF9800', '#F44336']  # Green, Yellow, Orange, Red

        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors[:len(labels)],
                                         autopct='%1.1f%%', startangle=90)

        # Style text
        for text in texts:
            text.set_color('white')
            text.set_fontsize(10)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')

        ax.set_title('Priority Distribution', color='white', fontweight='bold', pad=20)
        plt.tight_layout()

        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def create_priority_completion_chart(self, parent, tasks, priorities):
        """Create priority completion rate bar chart"""
        chart_frame = ctk.CTkFrame(parent)
        chart_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        # Chart title
        title_label = ctk.CTkLabel(
            chart_frame,
            text="📈 Completion Rate by Priority",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.pack(pady=(10, 5))

        # Calculate completion rates
        priority_names = []
        completion_rates = []
        colors = []

        priority_colors = {
            'low': '#4CAF50',
            'medium': '#FFC107',
            'high': '#FF9800',
            'urgent': '#F44336'
        }

        for priority in priorities:
            priority_tasks = [t for t in tasks if t.priority_id == priority.id]
            if priority_tasks:  # Only include priorities with tasks
                completed = len([t for t in priority_tasks if t.status == "completed"])
                rate = (completed / len(priority_tasks)) * 100

                priority_names.append(priority.name)
                completion_rates.append(rate)
                colors.append(priority_colors.get(priority.name.lower(), '#9C27B0'))

        if not priority_names:
            no_data_label = ctk.CTkLabel(chart_frame, text="No completion data")
            no_data_label.pack(pady=50)
            return

        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(5, 4))
        fig.patch.set_facecolor('#212121')
        ax.set_facecolor('#212121')

        # Create bar chart
        bars = ax.bar(priority_names, completion_rates, color=colors, alpha=0.8, edgecolor='white')

        # Add value labels on bars
        for bar, rate in zip(bars, completion_rates):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                   f'{rate:.1f}%', ha='center', va='bottom', color='white', fontweight='bold')

        # Style
        ax.set_title('Completion Rate by Priority', color='white', fontweight='bold')
        ax.set_ylabel('Completion Rate (%)', color='white')
        ax.set_ylim(0, 105)
        ax.tick_params(colors='white')
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()

        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def show_completion_rate(self):
        """Show completion rate analytics"""
        completion_frame = ctk.CTkScrollableFrame(self.analytics_frame)
        completion_frame.pack(fill="both", expand=True, padx=10, pady=10)

        title_label = ctk.CTkLabel(
            completion_frame,
            text="📊 Completion Rate Analysis",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(10, 20))

        # Get filtered tasks
        filtered_tasks = self.get_filtered_tasks()

        if not filtered_tasks:
            no_data_label = ctk.CTkLabel(
                completion_frame,
                text="No tasks found.\nCreate some tasks to see completion analysis!",
                font=ctk.CTkFont(size=14),
                text_color="gray"
            )
            no_data_label.pack(pady=50)
            return

        # Overall completion rate card
        overall_frame = ctk.CTkFrame(completion_frame)
        overall_frame.pack(fill="x", padx=10, pady=10)

        overall_title = ctk.CTkLabel(
            overall_frame,
            text="🎯 Overall Completion Rate",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        overall_title.pack(pady=(15, 10))

        # Calculate overall stats
        completed_tasks = [t for t in filtered_tasks if t.status == "completed"]
        pending_tasks = [t for t in filtered_tasks if t.status == "pending"]
        in_progress_tasks = [t for t in filtered_tasks if t.status == "in_progress"]

        total_tasks = len(filtered_tasks)
        completion_rate = (len(completed_tasks) / total_tasks * 100) if total_tasks > 0 else 0

        # Stats grid
        stats_grid = ctk.CTkFrame(overall_frame, fg_color="transparent")
        stats_grid.pack(fill="x", padx=20, pady=10)
        stats_grid.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Total tasks
        total_card = ctk.CTkFrame(stats_grid)
        total_card.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(total_card, text="📋", font=ctk.CTkFont(size=20)).pack(pady=(10, 5))
        ctk.CTkLabel(total_card, text=str(total_tasks), font=ctk.CTkFont(size=18, weight="bold")).pack()
        ctk.CTkLabel(total_card, text="Total Tasks", font=ctk.CTkFont(size=10)).pack(pady=(0, 10))

        # Completed tasks
        completed_card = ctk.CTkFrame(stats_grid)
        completed_card.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(completed_card, text="✅", font=ctk.CTkFont(size=20)).pack(pady=(10, 5))
        ctk.CTkLabel(completed_card, text=str(len(completed_tasks)), font=ctk.CTkFont(size=18, weight="bold"), text_color="#4CAF50").pack()
        ctk.CTkLabel(completed_card, text="Completed", font=ctk.CTkFont(size=10)).pack(pady=(0, 10))

        # In progress tasks
        progress_card = ctk.CTkFrame(stats_grid)
        progress_card.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(progress_card, text="🔄", font=ctk.CTkFont(size=20)).pack(pady=(10, 5))
        ctk.CTkLabel(progress_card, text=str(len(in_progress_tasks)), font=ctk.CTkFont(size=18, weight="bold"), text_color="#2196F3").pack()
        ctk.CTkLabel(progress_card, text="In Progress", font=ctk.CTkFont(size=10)).pack(pady=(0, 10))

        # Pending tasks
        pending_card = ctk.CTkFrame(stats_grid)
        pending_card.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(pending_card, text="⏳", font=ctk.CTkFont(size=20)).pack(pady=(10, 5))
        ctk.CTkLabel(pending_card, text=str(len(pending_tasks)), font=ctk.CTkFont(size=18, weight="bold"), text_color="#FF9800").pack()
        ctk.CTkLabel(pending_card, text="Pending", font=ctk.CTkFont(size=10)).pack(pady=(0, 10))

        # Completion rate display
        rate_frame = ctk.CTkFrame(overall_frame, fg_color="transparent")
        rate_frame.pack(fill="x", padx=20, pady=15)

        rate_label = ctk.CTkLabel(
            rate_frame,
            text=f"Overall Completion Rate: {completion_rate:.1f}%",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#4CAF50" if completion_rate >= 70 else "#FF9800" if completion_rate >= 50 else "#F44336"
        )
        rate_label.pack()

        # Progress bar
        progress_bar = ctk.CTkProgressBar(rate_frame, width=300, height=20)
        progress_bar.pack(pady=10)
        progress_bar.set(completion_rate / 100.0)

        # Charts container
        charts_container = ctk.CTkFrame(completion_frame)
        charts_container.pack(fill="x", padx=10, pady=20)
        charts_container.grid_columnconfigure((0, 1), weight=1)

        # Status distribution chart
        self.create_status_distribution_chart(charts_container, filtered_tasks)

        # Weekly completion trend chart
        self.create_weekly_completion_trend(charts_container, completed_tasks)

    def create_status_distribution_chart(self, parent, tasks):
        """Create status distribution donut chart"""
        chart_frame = ctk.CTkFrame(parent)
        chart_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # Chart title
        title_label = ctk.CTkLabel(
            chart_frame,
            text="📊 Task Status Distribution",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.pack(pady=(10, 5))

        # Count tasks by status
        status_counts = {
            'Completed': len([t for t in tasks if t.status == "completed"]),
            'In Progress': len([t for t in tasks if t.status == "in_progress"]),
            'Pending': len([t for t in tasks if t.status == "pending"]),
            'Cancelled': len([t for t in tasks if t.status == "cancelled"])
        }

        # Filter out zero counts
        status_counts = {k: v for k, v in status_counts.items() if v > 0}

        if not status_counts:
            no_data_label = ctk.CTkLabel(chart_frame, text="No status data")
            no_data_label.pack(pady=50)
            return

        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(5, 4))
        fig.patch.set_facecolor('#212121')
        ax.set_facecolor('#212121')

        # Create donut chart
        labels = list(status_counts.keys())
        sizes = list(status_counts.values())
        colors = ['#4CAF50', '#2196F3', '#FF9800', '#F44336']

        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors[:len(labels)],
                                         autopct='%1.1f%%', startangle=90, pctdistance=0.85)

        # Create donut hole
        centre_circle = plt.Circle((0,0), 0.70, fc='#212121')
        fig.gca().add_artist(centre_circle)

        # Style text
        for text in texts:
            text.set_color('white')
            text.set_fontsize(10)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')

        ax.set_title('Status Distribution', color='white', fontweight='bold', pad=20)
        plt.tight_layout()

        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def create_weekly_completion_trend(self, parent, completed_tasks):
        """Create weekly completion trend line chart"""
        chart_frame = ctk.CTkFrame(parent)
        chart_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        # Chart title
        title_label = ctk.CTkLabel(
            chart_frame,
            text="📈 Weekly Completion Trend",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.pack(pady=(10, 5))

        if not completed_tasks:
            no_data_label = ctk.CTkLabel(chart_frame, text="No completion data")
            no_data_label.pack(pady=50)
            return

        # Group completions by week
        from collections import defaultdict
        weekly_counts = defaultdict(int)

        for task in completed_tasks:
            if task.completed_at:
                # Get the start of the week (Monday)
                week_start = task.completed_at.date() - timedelta(days=task.completed_at.weekday())
                weekly_counts[week_start] += 1

        if not weekly_counts:
            no_data_label = ctk.CTkLabel(chart_frame, text="No completion dates")
            no_data_label.pack(pady=50)
            return

        # Sort by date and get last 8 weeks
        sorted_weeks = sorted(weekly_counts.items())[-8:]
        weeks = [week[0] for week in sorted_weeks]
        counts = [week[1] for week in sorted_weeks]

        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(5, 4))
        fig.patch.set_facecolor('#212121')
        ax.set_facecolor('#212121')

        # Create line chart
        ax.plot(weeks, counts, marker='o', linewidth=2, markersize=6, color='#4CAF50')
        ax.fill_between(weeks, counts, alpha=0.3, color='#4CAF50')

        # Style
        ax.set_title('Weekly Completion Trend', color='white', fontweight='bold')
        ax.set_ylabel('Tasks Completed', color='white')
        ax.tick_params(colors='white')
        ax.grid(True, alpha=0.3)

        # Format x-axis dates
        ax.tick_params(axis='x', rotation=45)

        plt.tight_layout()

        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def show_goals_progress(self):
        """Show goals progress analytics"""
        goals_frame = ctk.CTkScrollableFrame(self.analytics_frame)
        goals_frame.pack(fill="both", expand=True, padx=10, pady=10)

        title_label = ctk.CTkLabel(
            goals_frame,
            text="Goals Progress",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(10, 20))

        # Show goals if any exist
        if self.goals:
            for goal in self.goals:
                goal_frame = ctk.CTkFrame(goals_frame)
                goal_frame.pack(fill="x", padx=10, pady=5)

                # Goal info
                goal_label = ctk.CTkLabel(
                    goal_frame,
                    text=goal.title,
                    font=ctk.CTkFont(size=14, weight="bold")
                )
                goal_label.pack(anchor="w", padx=15, pady=(10, 5))

                # Progress bar
                progress_bar = ctk.CTkProgressBar(goal_frame)
                progress_bar.pack(fill="x", padx=15, pady=5)
                progress_bar.set(goal.progress_percentage / 100.0)

                # Progress text
                progress_label = ctk.CTkLabel(
                    goal_frame,
                    text=f"{goal.progress_percentage:.1f}% Complete",
                    font=ctk.CTkFont(size=12)
                )
                progress_label.pack(anchor="w", padx=15, pady=(5, 10))
        else:
            no_goals_label = ctk.CTkLabel(
                goals_frame,
                text="No goals created yet.\nCreate goals to track your progress!",
                font=ctk.CTkFont(size=14),
                text_color="gray"
            )
            no_goals_label.pack(pady=50)

    def update_quick_stats(self):
        """Update quick statistics in sidebar"""
        try:
            filtered_tasks = self.get_filtered_tasks()
            completed_tasks = [t for t in filtered_tasks if t.status == "completed"]

            self.total_tasks_label.configure(text=f"Total Tasks: {len(filtered_tasks)}")
            self.completed_tasks_label.configure(text=f"Completed: {len(completed_tasks)}")

            if len(filtered_tasks) > 0:
                completion_rate = (len(completed_tasks) / len(filtered_tasks)) * 100
                self.completion_rate_label.configure(text=f"Rate: {completion_rate:.1f}%")
            else:
                self.completion_rate_label.configure(text="Rate: 0%")

        except Exception as e:
            print(f"Error updating quick stats: {e}")

    def load_data(self):
        """Load analytics data"""
        try:
            self.tasks = Task.get_all()
            self.goals = Goal.get_all()
            self.update_quick_stats()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load analytics data: {e}")

    def refresh_data(self):
        """Refresh analytics data"""
        self.load_data()
        self.update_analytics()
