"""
Help dialog for Task Planner application
"""

import tkinter as tk
import customtkinter as ctk

class HelpDialog(ctk.CTkToplevel):
    """Help and instructions dialog"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        # Configure dialog
        self.title("Task Planner - Help & Instructions")
        self.geometry("800x600")
        self.resizable(True, True)
        
        # Center the dialog
        self.transient(parent)
        self.grab_set()
        
        # Setup UI
        self.setup_ui()
        
        # Center on parent
        self.center_on_parent(parent)
    
    def center_on_parent(self, parent):
        """Center dialog on parent window"""
        self.update_idletasks()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        x = parent_x + (parent_width - self.winfo_width()) // 2
        y = parent_y + (parent_height - self.winfo_height()) // 2
        
        self.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        """Setup help dialog UI"""
        # Main frame
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="📚 Task Planner Help & Instructions",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(20, 30))
        
        # Close button (fixed at bottom)
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(10, 20), side="bottom")
        
        close_btn = ctk.CTkButton(
            button_frame,
            text="Got it! Close Help",
            command=self.destroy,
            width=150,
            height=35,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        close_btn.pack(side="right")
        
        # Scrollable content frame
        content_frame = ctk.CTkScrollableFrame(main_frame)
        content_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Help content
        self.create_help_content(content_frame)
    
    def create_help_content(self, parent):
        """Create help content sections"""
        
        # Getting Started
        self.create_section(parent, "🚀 Getting Started", [
            "Welcome to Task Planner! This app helps you organize and track your tasks efficiently.",
            "",
            "• Click '+ Add Task' to create your first task",
            "• Use the sidebar to navigate between different views",
            "• Check the Quick Stats to see your task overview",
            "• Use filters to find specific tasks quickly"
        ])
        
        # Creating Tasks
        self.create_section(parent, "📝 Creating Tasks", [
            "When creating a new task, you can set:",
            "",
            "• Title: Give your task a clear, descriptive name",
            "• Description: Add details, notes, or steps (optional)",
            "• Category: Organize tasks by type (Work, Personal, etc.)",
            "• Priority: Set importance level (Low, Medium, High, Critical)",
            "• Due Date: When the task needs to be completed",
            "• Due Time: Specific time for the task (format: HH:MM)",
            "• Duration: How long you estimate the task will take (in minutes)",
            "• Recurring: Make the task repeat automatically"
        ])
        
        # Managing Tasks
        self.create_section(parent, "✅ Managing Tasks", [
            "In the task list, you can:",
            "",
            "• ✅ Check the checkbox to mark tasks as completed",
            "• ✏️ Click 'Edit' to modify task details",
            "• 🗑️ Click 'Delete' to remove tasks (with confirmation)",
            "• Use filters on the left to find specific tasks",
            "• Search by typing in task titles or descriptions"
        ])
        
        # Filters and Search
        self.create_section(parent, "🔍 Filters and Search", [
            "Use the filter panel to quickly find tasks:",
            "",
            "• Status: Filter by pending, in progress, or completed",
            "• Priority: Show only tasks with specific priority levels",
            "• Category: Filter by task categories",
            "• Search: Type keywords to search in titles and descriptions",
            "• Clear Filters: Reset all filters to show all tasks"
        ])
        
        # Navigation
        self.create_section(parent, "🧭 Navigation", [
            "Use the sidebar to access different views:",
            "",
            "• 📋 Tasks: Main task management interface",
            "• 📅 Calendar: View tasks in calendar format",
            "• 📊 Analytics: Track your productivity statistics",
            "• ⚙️ Settings: Configure app preferences"
        ])
        
        # Tips and Tricks
        self.create_section(parent, "💡 Tips and Tricks", [
            "Make the most of Task Planner:",
            "",
            "• Use clear, action-oriented task titles (e.g., 'Call dentist', 'Review project proposal')",
            "• Set realistic time estimates to improve planning",
            "• Use categories to group related tasks",
            "• Set priorities to focus on what's most important",
            "• Use recurring tasks for regular activities",
            "• Check the Quick Stats regularly to track progress",
            "• Use the search function to quickly find specific tasks"
        ])
        
        # Keyboard Shortcuts
        self.create_section(parent, "⌨️ Quick Actions", [
            "Speed up your workflow:",
            "",
            "• Use the '+ Add Task' button in the sidebar for quick task creation",
            "• Use the 'Refresh' button to update task data",
            "• The search filter updates automatically as you type",
            "• Task completion status updates immediately when checked"
        ])
    
    def create_section(self, parent, title, content_lines):
        """Create a help section with title and content"""
        # Section frame
        section_frame = ctk.CTkFrame(parent)
        section_frame.pack(fill="x", padx=15, pady=(0, 20))
        
        # Section title
        title_label = ctk.CTkLabel(
            section_frame,
            text=title,
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w"
        )
        title_label.pack(fill="x", padx=20, pady=(15, 10))
        
        # Section content
        content_text = "\n".join(content_lines)
        content_label = ctk.CTkLabel(
            section_frame,
            text=content_text,
            font=ctk.CTkFont(size=12),
            anchor="w",
            justify="left",
            wraplength=700
        )
        content_label.pack(fill="x", padx=20, pady=(0, 15))
