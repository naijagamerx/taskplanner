"""
Task Manager interface for Task Planner application
"""

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
# datetime imports removed as they're not used
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

class TaskManagerFrame(ctk.CTkFrame):
    """Task management interface"""

    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.main_window = main_window
        self.tasks = []
        self.filtered_tasks = []
        self.current_filter = "all"

        # Pagination variables
        self.current_page = 1
        self.page_size = 5
        self.total_pages = 1

        self.setup_ui()
        self.load_tasks()

    def setup_ui(self):
        """Setup task manager UI"""
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Create header
        self.create_header()

        # Create filter panel
        self.create_filter_panel()

        # Create task list
        self.create_task_list()

        # Create task details panel
        self.create_details_panel()

    def create_header(self):
        """Create header with title and main actions"""
        header_frame = ctk.CTkFrame(self)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 5))
        header_frame.grid_columnconfigure(1, weight=1)

        # Title and description
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, padx=20, pady=15, sticky="w")

        title_label = ctk.CTkLabel(
            title_frame,
            text="📋 Task Manager",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(anchor="w")

        desc_label = ctk.CTkLabel(
            title_frame,
            text="Create, organize, and track your tasks efficiently",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        desc_label.pack(anchor="w", pady=(2, 0))

        # Action buttons
        actions_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        actions_frame.grid(row=0, column=2, padx=20, pady=15, sticky="e")

        # Add task button
        add_btn = ctk.CTkButton(
            actions_frame,
            text="+ Add Task",
            command=self.show_add_task_dialog,
            height=35,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        add_btn.pack(side="right", padx=(10, 0))

        # Refresh button
        refresh_btn = ctk.CTkButton(
            actions_frame,
            text="🔄 Refresh",
            command=self.refresh_data,
            height=35,
            width=100
        )
        refresh_btn.pack(side="right")

    def create_filter_panel(self):
        """Create task filtering panel"""
        filter_frame = ctk.CTkFrame(self)
        filter_frame.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=5)
        filter_frame.grid_rowconfigure(10, weight=1)

        # Filter title and description
        filter_title = ctk.CTkLabel(
            filter_frame,
            text="🔍 Filters",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        filter_title.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")

        filter_desc = ctk.CTkLabel(
            filter_frame,
            text="Find tasks quickly using these filters",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        filter_desc.grid(row=0, column=0, padx=15, pady=(35, 10), sticky="w")

        # Status filters
        status_label = ctk.CTkLabel(filter_frame, text="Status:", font=ctk.CTkFont(size=12, weight="bold"))
        status_label.grid(row=1, column=0, padx=15, pady=(10, 5), sticky="w")

        self.status_var = tk.StringVar(value="all")
        status_options = ["all", "pending", "in_progress", "completed"]

        for i, status in enumerate(status_options):
            radio = ctk.CTkRadioButton(
                filter_frame,
                text=status.replace("_", " ").title(),
                variable=self.status_var,
                value=status,
                command=self.apply_filters
            )
            radio.grid(row=2+i, column=0, padx=25, pady=2, sticky="w")

        # Priority filter
        priority_label = ctk.CTkLabel(filter_frame, text="Priority:", font=ctk.CTkFont(size=12, weight="bold"))
        priority_label.grid(row=7, column=0, padx=15, pady=(15, 5), sticky="w")

        self.priority_var = tk.StringVar(value="all")
        self.priority_combo = ctk.CTkComboBox(
            filter_frame,
            variable=self.priority_var,
            values=["all"],
            command=self.apply_filters,
            width=150
        )
        self.priority_combo.grid(row=8, column=0, padx=15, pady=5, sticky="ew")

        # Category filter
        category_label = ctk.CTkLabel(filter_frame, text="Category:", font=ctk.CTkFont(size=12, weight="bold"))
        category_label.grid(row=9, column=0, padx=15, pady=(10, 5), sticky="w")

        self.category_var = tk.StringVar(value="all")
        self.category_combo = ctk.CTkComboBox(
            filter_frame,
            variable=self.category_var,
            values=["all"],
            command=self.apply_filters,
            width=150
        )
        self.category_combo.grid(row=10, column=0, padx=15, pady=5, sticky="ew")

        # Search
        search_label = ctk.CTkLabel(filter_frame, text="Search:", font=ctk.CTkFont(size=12, weight="bold"))
        search_label.grid(row=11, column=0, padx=15, pady=(15, 5), sticky="w")

        search_desc = ctk.CTkLabel(
            filter_frame,
            text="Search in task titles and descriptions",
            font=ctk.CTkFont(size=9),
            text_color="gray"
        )
        search_desc.grid(row=11, column=0, padx=15, pady=(30, 0), sticky="w")

        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self.apply_filters())

        search_entry = ctk.CTkEntry(
            filter_frame,
            textvariable=self.search_var,
            placeholder_text="e.g., 'meeting', 'project', 'urgent'...",
            width=150
        )
        search_entry.grid(row=12, column=0, padx=15, pady=5, sticky="ew")

        # Clear filters button
        clear_btn = ctk.CTkButton(
            filter_frame,
            text="Clear Filters",
            command=self.clear_filters,
            height=30,
            width=150
        )
        clear_btn.grid(row=13, column=0, padx=15, pady=(15, 10), sticky="ew")

    def create_task_list(self):
        """Create task list display"""
        list_frame = ctk.CTkFrame(self)
        list_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(1, weight=1)

        # List header
        list_header = ctk.CTkFrame(list_frame)
        list_header.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        list_header.grid_columnconfigure(1, weight=1)

        # Title and instructions
        title_info_frame = ctk.CTkFrame(list_header, fg_color="transparent")
        title_info_frame.grid(row=0, column=0, padx=15, pady=10, sticky="w")

        list_title = ctk.CTkLabel(
            title_info_frame,
            text="📝 Your Tasks",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        list_title.pack(anchor="w")

        list_desc = ctk.CTkLabel(
            title_info_frame,
            text="✅ Check to complete • ✏️ Edit • 🗑️ Delete",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        list_desc.pack(anchor="w", pady=(2, 0))

        # Pagination and task count controls
        controls_frame = ctk.CTkFrame(list_header, fg_color="transparent")
        controls_frame.grid(row=0, column=1, padx=15, pady=10, sticky="e")

        # Page size selector
        page_size_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        page_size_frame.pack(side="top", pady=(0, 5))

        ctk.CTkLabel(
            page_size_frame,
            text="Show:",
            font=ctk.CTkFont(size=11)
        ).pack(side="left", padx=(0, 5))

        self.page_size_var = tk.StringVar(value="5")
        page_size_combo = ctk.CTkComboBox(
            page_size_frame,
            variable=self.page_size_var,
            values=["5", "10", "20", "50", "100"],
            command=self.change_page_size,
            width=70,
            height=25
        )
        page_size_combo.pack(side="left", padx=(0, 5))

        ctk.CTkLabel(
            page_size_frame,
            text="per page",
            font=ctk.CTkFont(size=11)
        ).pack(side="left")

        # Task count and page info
        self.task_count_label = ctk.CTkLabel(
            controls_frame,
            text="0 tasks",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.task_count_label.pack(side="top")

        # Scrollable task list
        self.task_list_frame = ctk.CTkScrollableFrame(list_frame)
        self.task_list_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 5))
        self.task_list_frame.grid_columnconfigure(0, weight=1)

        # Pagination controls
        self.create_pagination_controls(list_frame)

    def create_pagination_controls(self, parent):
        """Create pagination navigation controls"""
        self.pagination_frame = ctk.CTkFrame(parent)
        self.pagination_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(5, 10))
        self.pagination_frame.grid_columnconfigure(1, weight=1)

        # Previous button
        self.prev_btn = ctk.CTkButton(
            self.pagination_frame,
            text="◀ Previous",
            command=self.previous_page,
            width=100,
            height=30,
            state="disabled"
        )
        self.prev_btn.grid(row=0, column=0, padx=(10, 5), pady=10)

        # Page info
        self.page_info_label = ctk.CTkLabel(
            self.pagination_frame,
            text="Page 1 of 1",
            font=ctk.CTkFont(size=12)
        )
        self.page_info_label.grid(row=0, column=1, padx=10, pady=10)

        # Next button
        self.next_btn = ctk.CTkButton(
            self.pagination_frame,
            text="Next ▶",
            command=self.next_page,
            width=100,
            height=30,
            state="disabled"
        )
        self.next_btn.grid(row=0, column=2, padx=(5, 10), pady=10)

    def create_details_panel(self):
        """Create task details panel"""
        # This will be implemented when a task is selected
        pass

    def load_tasks(self):
        """Load tasks from database"""
        try:
            self.tasks = Task.get_all()
            self.load_filter_options()
            self.apply_filters()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load tasks: {e}")

    def load_filter_options(self):
        """Load filter options from database"""
        try:
            # Load priorities
            priorities = Priority.get_all()
            priority_values = ["all"] + [p.name for p in priorities]
            self.priority_combo.configure(values=priority_values)

            # Load categories
            categories = Category.get_all()
            category_values = ["all"] + [c.name for c in categories]
            self.category_combo.configure(values=category_values)

        except Exception as e:
            print(f"Error loading filter options: {e}")

    def apply_filters(self, *args):
        """Apply current filters to task list"""
        try:
            filtered_tasks = self.tasks.copy()

            # Filter by status
            status_filter = self.status_var.get()
            if status_filter != "all":
                filtered_tasks = [t for t in filtered_tasks if t.status == status_filter]

            # Filter by priority
            priority_filter = self.priority_var.get()
            if priority_filter != "all":
                priorities = Priority.get_all()
                priority_id = None
                for p in priorities:
                    if p.name == priority_filter:
                        priority_id = p.id
                        break
                if priority_id:
                    filtered_tasks = [t for t in filtered_tasks if t.priority_id == priority_id]

            # Filter by category
            category_filter = self.category_var.get()
            if category_filter != "all":
                categories = Category.get_all()
                category_id = None
                for c in categories:
                    if c.name == category_filter:
                        category_id = c.id
                        break
                if category_id:
                    filtered_tasks = [t for t in filtered_tasks if t.category_id == category_id]

            # Filter by search term
            search_term = self.search_var.get().lower()
            if search_term:
                filtered_tasks = [
                    t for t in filtered_tasks
                    if search_term in t.title.lower() or search_term in (t.description or "").lower()
                ]

            self.filtered_tasks = filtered_tasks
            self.current_page = 1  # Reset to first page when filters change
            self.update_pagination()
            self.display_tasks()

        except Exception as e:
            print(f"Error applying filters: {e}")

    def display_tasks(self):
        """Display filtered tasks in the list with pagination"""
        # Clear existing task widgets
        for widget in self.task_list_frame.winfo_children():
            widget.destroy()

        # Calculate pagination
        total_tasks = len(self.filtered_tasks)
        start_index = (self.current_page - 1) * self.page_size
        end_index = min(start_index + self.page_size, total_tasks)

        # Get tasks for current page
        page_tasks = self.filtered_tasks[start_index:end_index]

        # Update task count and page info
        if total_tasks > 0:
            self.task_count_label.configure(
                text=f"Showing {start_index + 1}-{end_index} of {total_tasks} tasks"
            )
        else:
            self.task_count_label.configure(text="0 tasks")

        # Display tasks or empty state
        if page_tasks:
            for i, task in enumerate(page_tasks):
                self.create_task_widget(task, i)
        else:
            # Show empty state message
            empty_frame = ctk.CTkFrame(self.task_list_frame, fg_color="transparent")
            empty_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=50)

            empty_icon = ctk.CTkLabel(
                empty_frame,
                text="📝",
                font=ctk.CTkFont(size=48)
            )
            empty_icon.pack(pady=(20, 10))

            if len(self.tasks) == 0:
                # No tasks at all
                empty_title = ctk.CTkLabel(
                    empty_frame,
                    text="No tasks yet!",
                    font=ctk.CTkFont(size=18, weight="bold")
                )
                empty_title.pack(pady=5)

                empty_desc = ctk.CTkLabel(
                    empty_frame,
                    text="Click '+ Add Task' to create your first task\nand start organizing your life!",
                    font=ctk.CTkFont(size=12),
                    text_color="gray",
                    justify="center"
                )
                empty_desc.pack(pady=5)
            else:
                # Tasks exist but filtered out
                empty_title = ctk.CTkLabel(
                    empty_frame,
                    text="No tasks match your filters",
                    font=ctk.CTkFont(size=18, weight="bold")
                )
                empty_title.pack(pady=5)

                empty_desc = ctk.CTkLabel(
                    empty_frame,
                    text="Try adjusting your filters or search terms\nto find the tasks you're looking for.",
                    font=ctk.CTkFont(size=12),
                    text_color="gray",
                    justify="center"
                )
                empty_desc.pack(pady=5)

    def create_task_widget(self, task, index):
        """Create widget for individual task"""
        task_frame = ctk.CTkFrame(self.task_list_frame)
        task_frame.grid(row=index, column=0, sticky="ew", padx=5, pady=2)
        task_frame.grid_columnconfigure(1, weight=1)

        # Status checkbox - only checked for completed tasks
        is_completed = (task.status == "completed")
        status_var = tk.BooleanVar(value=is_completed)
        status_check = ctk.CTkCheckBox(
            task_frame,
            text="",
            variable=status_var,
            command=lambda t=task, v=status_var: self.toggle_task_status(t, v.get())
        )
        status_check.grid(row=0, column=0, padx=10, pady=10)



        # Task info
        info_frame = ctk.CTkFrame(task_frame, fg_color="transparent")
        info_frame.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        info_frame.grid_columnconfigure(0, weight=1)

        # Title
        title_label = ctk.CTkLabel(
            info_frame,
            text=task.title,
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        title_label.grid(row=0, column=0, sticky="ew", padx=5)

        # Description (if exists)
        if task.description:
            desc_text = task.description[:100] + "..." if len(task.description) > 100 else task.description
            desc_label = ctk.CTkLabel(
                info_frame,
                text=desc_text,
                font=ctk.CTkFont(size=11),
                text_color="gray",
                anchor="w"
            )
            desc_label.grid(row=1, column=0, sticky="ew", padx=5)

        # Due date and priority
        details_text = []
        if task.due_date:
            details_text.append(f"Due: {task.due_date}")

        # Get priority name
        try:
            priority = Priority.get_by_id(task.priority_id)
            if priority:
                details_text.append(f"Priority: {priority.name}")
        except:
            pass

        if details_text:
            details_label = ctk.CTkLabel(
                info_frame,
                text=" | ".join(details_text),
                font=ctk.CTkFont(size=10),
                text_color="gray",
                anchor="w"
            )
            details_label.grid(row=2, column=0, sticky="ew", padx=5)

        # Action buttons
        actions_frame = ctk.CTkFrame(task_frame, fg_color="transparent")
        actions_frame.grid(row=0, column=2, padx=10, pady=10)

        edit_btn = ctk.CTkButton(
            actions_frame,
            text="Edit",
            command=lambda t=task: self.edit_task(t),
            width=60,
            height=25,
            font=ctk.CTkFont(size=11)
        )
        edit_btn.pack(side="top", pady=2)

        delete_btn = ctk.CTkButton(
            actions_frame,
            text="Delete",
            command=lambda t=task: self.delete_task(t),
            width=60,
            height=25,
            font=ctk.CTkFont(size=11),
            fg_color="red",
            hover_color="darkred"
        )
        delete_btn.pack(side="top", pady=2)

    def toggle_task_status(self, task, completed):
        """Toggle task completion status"""
        try:
            if completed:
                task.mark_completed()
                # Send completion notification
                if NOTIFICATIONS_AVAILABLE and notification_manager:
                    notification_manager.send_task_completion_notification(task)
            else:
                task.status = "pending"
                task.completed_at = None
                task.save()

            self.refresh_data()
            self.main_window.update_quick_stats()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to update task status: {e}")

    def edit_task(self, task):
        """Edit selected task"""
        dialog = TaskDialog(self, task=task)
        if dialog.result:
            self.refresh_data()
            self.main_window.update_quick_stats()

    def delete_task(self, task):
        """Delete selected task"""
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{task.title}'?"):
            try:
                task.delete()
                self.refresh_data()
                self.main_window.update_quick_stats()
                messagebox.showinfo("Success", "Task deleted successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete task: {e}")

    def show_add_task_dialog(self):
        """Show add task dialog"""
        dialog = TaskDialog(self)
        if dialog.result:
            self.refresh_data()
            self.main_window.update_quick_stats()

    def clear_filters(self):
        """Clear all filters"""
        self.status_var.set("all")
        self.priority_var.set("all")
        self.category_var.set("all")
        self.search_var.set("")
        self.apply_filters()

    def update_pagination(self):
        """Update pagination controls and info"""
        total_tasks = len(self.filtered_tasks)
        self.total_pages = max(1, (total_tasks + self.page_size - 1) // self.page_size)

        # Ensure current page is valid
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages

        # Update page info label
        self.page_info_label.configure(text=f"Page {self.current_page} of {self.total_pages}")

        # Update button states
        self.prev_btn.configure(state="normal" if self.current_page > 1 else "disabled")
        self.next_btn.configure(state="normal" if self.current_page < self.total_pages else "disabled")

    def change_page_size(self, value):
        """Change the number of tasks per page"""
        try:
            self.page_size = int(value)
            self.current_page = 1  # Reset to first page
            self.update_pagination()
            self.display_tasks()
        except ValueError:
            pass

    def next_page(self):
        """Go to next page"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.update_pagination()
            self.display_tasks()

    def previous_page(self):
        """Go to previous page"""
        if self.current_page > 1:
            self.current_page -= 1
            self.update_pagination()
            self.display_tasks()

    def refresh_data(self):
        """Refresh task data"""
        self.load_tasks()
