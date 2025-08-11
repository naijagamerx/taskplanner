#!/usr/bin/env python3
"""
Enhanced Analytics Dashboard for Task Planner
"""

import tkinter as tk
import customtkinter as ctk
from typing import Dict, Any, List
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

try:
    from services.analytics_manager import analytics_manager
    from services.theme_manager import theme_manager
    ANALYTICS_AVAILABLE = True
except ImportError:
    ANALYTICS_AVAILABLE = False

class EnhancedAnalytics(ctk.CTkFrame):
    """Enhanced analytics dashboard with charts and insights"""
    
    def __init__(self, parent, main_window=None):
        super().__init__(parent)
        self.main_window = main_window
        self.current_period = 30  # days
        
        if not ANALYTICS_AVAILABLE:
            self.show_unavailable_message()
            return
        
        self.setup_ui()
        self.load_analytics_data()
    
    def show_unavailable_message(self):
        """Show message when analytics are not available"""
        message_label = ctk.CTkLabel(
            self,
            text="📊 Enhanced Analytics\n\nAnalytics features are not available.\nPlease ensure all required dependencies are installed.",
            font=ctk.CTkFont(size=16),
            justify="center"
        )
        message_label.pack(expand=True, fill="both", padx=50, pady=50)
    
    def setup_ui(self):
        """Setup the analytics dashboard UI"""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header with controls
        self.create_header()
        
        # Main content with tabs
        self.create_content_tabs()
    
    def create_header(self):
        """Create header with period selection and refresh"""
        header_frame = ctk.CTkFrame(self, height=60)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="📊 Analytics Dashboard",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        # Controls frame
        controls_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        controls_frame.grid(row=0, column=2, padx=20, pady=15, sticky="e")
        
        # Period selection
        period_label = ctk.CTkLabel(controls_frame, text="Period:")
        period_label.pack(side="left", padx=(0, 5))
        
        self.period_var = tk.StringVar(value="30 days")
        period_combo = ctk.CTkComboBox(
            controls_frame,
            variable=self.period_var,
            values=["7 days", "30 days", "90 days", "1 year"],
            command=self.on_period_change,
            width=100
        )
        period_combo.pack(side="left", padx=(0, 10))
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            controls_frame,
            text="🔄 Refresh",
            command=self.refresh_data,
            width=80,
            height=30
        )
        refresh_btn.pack(side="left")
    
    def create_content_tabs(self):
        """Create tabbed content area"""
        # Tab view
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        # Create tabs
        self.overview_tab = self.tab_view.add("📈 Overview")
        self.productivity_tab = self.tab_view.add("⚡ Productivity")
        self.categories_tab = self.tab_view.add("📁 Categories")
        self.time_tab = self.tab_view.add("⏰ Time Analysis")
        self.goals_tab = self.tab_view.add("🎯 Goals")
        
        # Setup tab content
        self.setup_overview_tab()
        self.setup_productivity_tab()
        self.setup_categories_tab()
        self.setup_time_tab()
        self.setup_goals_tab()
    
    def setup_overview_tab(self):
        """Setup overview tab with key metrics"""
        # Scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(self.overview_tab)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Metrics cards container
        self.metrics_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        self.metrics_frame.pack(fill="x", pady=(0, 20))
        
        # Chart container
        self.overview_chart_frame = ctk.CTkFrame(scroll_frame)
        self.overview_chart_frame.pack(fill="both", expand=True)
    
    def setup_productivity_tab(self):
        """Setup productivity analysis tab"""
        # Main container
        main_frame = ctk.CTkFrame(self.productivity_tab, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        
        # Productivity summary
        self.productivity_summary_frame = ctk.CTkFrame(main_frame)
        self.productivity_summary_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        # Productivity chart
        self.productivity_chart_frame = ctk.CTkFrame(main_frame)
        self.productivity_chart_frame.grid(row=1, column=0, sticky="nsew")
    
    def setup_categories_tab(self):
        """Setup categories analysis tab"""
        # Split layout
        main_frame = ctk.CTkFrame(self.categories_tab, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        
        # Category stats
        self.category_stats_frame = ctk.CTkFrame(main_frame)
        self.category_stats_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        # Category chart
        self.category_chart_frame = ctk.CTkFrame(main_frame)
        self.category_chart_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
    
    def setup_time_tab(self):
        """Setup time analysis tab"""
        self.time_analysis_frame = ctk.CTkScrollableFrame(self.time_tab)
        self.time_analysis_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    def setup_goals_tab(self):
        """Setup goals analysis tab"""
        self.goals_analysis_frame = ctk.CTkScrollableFrame(self.goals_tab)
        self.goals_analysis_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    def load_analytics_data(self):
        """Load and display analytics data"""
        if not ANALYTICS_AVAILABLE:
            return
        
        try:
            # Get period in days
            period_text = self.period_var.get()
            if "7 days" in period_text:
                self.current_period = 7
            elif "30 days" in period_text:
                self.current_period = 30
            elif "90 days" in period_text:
                self.current_period = 90
            else:
                self.current_period = 365
            
            # Load data
            self.productivity_data = analytics_manager.get_productivity_overview(self.current_period)
            self.category_data = analytics_manager.get_category_analytics()
            self.time_data = analytics_manager.get_time_analytics()
            self.goals_data = analytics_manager.get_goal_progress_analytics()
            
            # Update displays
            self.update_overview_display()
            self.update_productivity_display()
            self.update_categories_display()
            self.update_time_display()
            self.update_goals_display()
            
        except Exception as e:
            print(f"Error loading analytics data: {e}")
    
    def update_overview_display(self):
        """Update overview tab display"""
        # Clear existing widgets
        for widget in self.metrics_frame.winfo_children():
            widget.destroy()
        
        # Create metric cards
        metrics = [
            ("📋 Total Tasks", self.productivity_data.get('total_tasks', 0), ""),
            ("✅ Completed", self.productivity_data.get('completed_tasks', 0), ""),
            ("📈 Completion Rate", f"{self.productivity_data.get('completion_rate', 0):.1f}", "%"),
            ("⚠️ Overdue", self.productivity_data.get('overdue_tasks', 0), ""),
            ("⏱️ Time Tracked", f"{self.productivity_data.get('total_actual_time', 0) / 60:.1f}", "hrs"),
            ("📊 Trend", self.productivity_data.get('productivity_trend', 'stable').title(), "")
        ]
        
        # Create grid of metric cards
        for i, (title, value, unit) in enumerate(metrics):
            self.create_metric_card(self.metrics_frame, title, value, unit, i)
        
        # Create overview chart
        self.create_overview_chart()
    
    def create_metric_card(self, parent, title, value, unit, index):
        """Create a metric card widget"""
        row = index // 3
        col = index % 3
        
        card = ctk.CTkFrame(parent)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
        parent.grid_columnconfigure(col, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        title_label.pack(pady=(15, 5))
        
        # Value
        value_text = f"{value}{unit}"
        value_label = ctk.CTkLabel(
            card,
            text=value_text,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=theme_manager.get_color('primary') if ANALYTICS_AVAILABLE else "#1f538d"
        )
        value_label.pack(pady=(0, 15))
    
    def create_overview_chart(self):
        """Create overview productivity chart"""
        # Clear existing chart
        for widget in self.overview_chart_frame.winfo_children():
            widget.destroy()
        
        if not self.productivity_data.get('daily_stats'):
            return
        
        # Create matplotlib figure
        fig = Figure(figsize=(10, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        # Prepare data
        daily_stats = self.productivity_data['daily_stats']
        dates = [stat['date'] for stat in daily_stats]
        completed = [stat['completed_tasks'] for stat in daily_stats]
        created = [stat['created_tasks'] for stat in daily_stats]
        
        # Create chart
        x = range(len(dates))
        ax.bar([i - 0.2 for i in x], created, 0.4, label='Created', alpha=0.7, color='#3b82f6')
        ax.bar([i + 0.2 for i in x], completed, 0.4, label='Completed', alpha=0.7, color='#10b981')
        
        ax.set_xlabel('Date')
        ax.set_ylabel('Tasks')
        ax.set_title('Daily Task Activity')
        ax.legend()
        
        # Format x-axis
        if len(dates) <= 30:
            step = max(1, len(dates) // 10)
            ax.set_xticks(range(0, len(dates), step))
            ax.set_xticklabels([dates[i][-5:] for i in range(0, len(dates), step)], rotation=45)
        
        fig.tight_layout()
        
        # Add to GUI
        canvas = FigureCanvasTkAgg(fig, self.overview_chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
    
    def update_productivity_display(self):
        """Update productivity tab display"""
        # Implementation for productivity charts and analysis
        pass
    
    def update_categories_display(self):
        """Update categories tab display"""
        # Implementation for category analysis
        pass
    
    def update_time_display(self):
        """Update time analysis tab display"""
        # Implementation for time analysis
        pass
    
    def update_goals_display(self):
        """Update goals tab display"""
        # Implementation for goals analysis
        pass
    
    def on_period_change(self, value):
        """Handle period selection change"""
        self.load_analytics_data()
    
    def refresh_data(self):
        """Refresh analytics data"""
        self.load_analytics_data()
    
    def refresh_data(self):
        """Refresh all analytics data"""
        self.load_analytics_data()
