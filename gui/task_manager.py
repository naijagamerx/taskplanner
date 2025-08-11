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

        # Bulk selection variables
        self.selected_tasks = set()
        self.task_checkboxes = {}

        # Filter panel state
        self.filter_panel_collapsed = False

        # Register with font manager
        try:
            from services.font_manager import register_for_font_updates, get_current_font_size
            register_for_font_updates(self)
            self.current_font_size = get_current_font_size()
        except ImportError:
            self.current_font_size = 12

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
        """Create task filtering panel with collapsible functionality"""
        self.filter_frame = ctk.CTkFrame(self)
        self.filter_frame.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=5)
        self.filter_frame.grid_rowconfigure(10, weight=1)

        # Filter header with collapse/expand button
        filter_header = ctk.CTkFrame(self.filter_frame, fg_color="transparent")
        filter_header.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 10))
        filter_header.grid_columnconfigure(0, weight=1)

        # Left side - Title and description
        title_section = ctk.CTkFrame(filter_header, fg_color="transparent")
        title_section.grid(row=0, column=0, sticky="w")

        filter_title = ctk.CTkLabel(
            title_section,
            text="🔍 Filters",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        filter_title.pack(anchor="w")

        filter_desc = ctk.CTkLabel(
            title_section,
            text="Find tasks quickly using these filters",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        filter_desc.pack(anchor="w", pady=(2, 0))

        # Right side - Collapse/Expand button
        self.collapse_btn = ctk.CTkButton(
            filter_header,
            text="◀ Hide",
            command=self.toggle_filter_panel,
            width=80,
            height=30,
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color="#6b7280",
            hover_color="#4b5563",
            corner_radius=6
        )
        self.collapse_btn.grid(row=0, column=1, sticky="e")

        # Container for all filter content (collapsible)
        self.filter_content = ctk.CTkFrame(self.filter_frame, fg_color="transparent")
        self.filter_content.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        self.filter_content.grid_rowconfigure(9, weight=1)

        # Status filters
        status_label = ctk.CTkLabel(self.filter_content, text="Status:", font=ctk.CTkFont(size=12, weight="bold"))
        status_label.grid(row=0, column=0, padx=0, pady=(10, 5), sticky="w")

        self.status_var = tk.StringVar(value="all")
        status_options = ["all", "pending", "in_progress", "completed"]

        for i, status in enumerate(status_options):
            radio = ctk.CTkRadioButton(
                self.filter_content,
                text=status.replace("_", " ").title(),
                variable=self.status_var,
                value=status,
                command=self.apply_filters
            )
            radio.grid(row=1+i, column=0, padx=20, pady=2, sticky="w")

        # Priority filter
        priority_label = ctk.CTkLabel(self.filter_content, text="Priority:", font=ctk.CTkFont(size=12, weight="bold"))
        priority_label.grid(row=5, column=0, padx=0, pady=(15, 5), sticky="w")

        self.priority_var = tk.StringVar(value="all")
        self.priority_combo = ctk.CTkComboBox(
            self.filter_content,
            variable=self.priority_var,
            values=["all"],
            command=self.apply_filters,
            width=150
        )
        self.priority_combo.grid(row=6, column=0, padx=0, pady=5, sticky="ew")

        # Category filter
        category_label = ctk.CTkLabel(self.filter_content, text="Category:", font=ctk.CTkFont(size=12, weight="bold"))
        category_label.grid(row=7, column=0, padx=0, pady=(10, 5), sticky="w")

        self.category_var = tk.StringVar(value="all")
        self.category_combo = ctk.CTkComboBox(
            self.filter_content,
            variable=self.category_var,
            values=["all"],
            command=self.apply_filters,
            width=150
        )
        self.category_combo.grid(row=8, column=0, padx=0, pady=5, sticky="ew")

        # Enhanced Search Section
        search_section = ctk.CTkFrame(self.filter_content)
        search_section.grid(row=9, column=0, padx=0, pady=(15, 5), sticky="ew")
        search_section.grid_columnconfigure(0, weight=1)

        # Search header with icon
        search_header = ctk.CTkFrame(search_section, fg_color="transparent")
        search_header.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))

        search_label = ctk.CTkLabel(
            search_header,
            text="🔍 Smart Search",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        search_label.pack(side="left")

        # Search input with clear button
        search_input_frame = ctk.CTkFrame(search_section, fg_color="transparent")
        search_input_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        search_input_frame.grid_columnconfigure(0, weight=1)

        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self.on_search_change())

        self.search_entry = ctk.CTkEntry(
            search_input_frame,
            textvariable=self.search_var,
            placeholder_text="Search tasks, categories, priorities...",
            height=35,
            font=ctk.CTkFont(size=12)
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        # Bind keyboard shortcuts
        self.search_entry.bind("<Control-a>", lambda e: self.search_entry.select_range(0, 'end'))
        self.search_entry.bind("<Escape>", lambda e: self.clear_search())
        self.search_entry.bind("<Return>", lambda e: self.apply_filters())

        # Clear search button
        self.clear_search_btn = ctk.CTkButton(
            search_input_frame,
            text="✕",
            width=35,
            height=35,
            command=self.clear_search,
            font=ctk.CTkFont(size=14),
            fg_color="gray",
            hover_color="darkgray"
        )
        self.clear_search_btn.grid(row=0, column=1)

        # Search options
        search_options_frame = ctk.CTkFrame(search_section, fg_color="transparent")
        search_options_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 5))

        # Search scope checkboxes
        self.search_titles = tk.BooleanVar(value=True)
        self.search_descriptions = tk.BooleanVar(value=True)
        self.search_categories = tk.BooleanVar(value=True)

        scope_frame = ctk.CTkFrame(search_options_frame, fg_color="transparent")
        scope_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(
            scope_frame,
            text="Search in:",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        ).pack(side="left", padx=(0, 10))

        ctk.CTkCheckBox(
            scope_frame,
            text="Titles",
            variable=self.search_titles,
            command=self.apply_filters,
            font=ctk.CTkFont(size=9),
            width=60
        ).pack(side="left", padx=2)

        ctk.CTkCheckBox(
            scope_frame,
            text="Descriptions",
            variable=self.search_descriptions,
            command=self.apply_filters,
            font=ctk.CTkFont(size=9),
            width=80
        ).pack(side="left", padx=2)

        ctk.CTkCheckBox(
            scope_frame,
            text="Categories",
            variable=self.search_categories,
            command=self.apply_filters,
            font=ctk.CTkFont(size=9),
            width=70
        ).pack(side="left", padx=2)

        # Search results info
        self.search_results_label = ctk.CTkLabel(
            search_section,
            text="",
            font=ctk.CTkFont(size=9),
            text_color="gray"
        )
        self.search_results_label.grid(row=3, column=0, padx=10, pady=(0, 10))

        # Clear filters button
        clear_btn = ctk.CTkButton(
            self.filter_content,
            text="🗑️ Clear All Filters",
            command=self.clear_filters,
            height=35,
            width=150,
            font=ctk.CTkFont(size=12),
            fg_color="orange",
            hover_color="darkorange"
        )
        clear_btn.grid(row=10, column=0, padx=0, pady=(15, 10), sticky="ew")

    def create_task_list(self):
        """Create task list display"""
        list_frame = ctk.CTkFrame(self)
        list_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(1, weight=1)

        # Enhanced List header with better visual design
        list_header = ctk.CTkFrame(list_frame, corner_radius=12)
        list_header.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        list_header.grid_columnconfigure(1, weight=1)

        # Top row - Title and main actions
        top_row = ctk.CTkFrame(list_header, fg_color="transparent")
        top_row.grid(row=0, column=0, columnspan=3, sticky="ew", padx=20, pady=(15, 10))
        top_row.grid_columnconfigure(1, weight=1)

        # Left side - Title and description
        title_section = ctk.CTkFrame(top_row, fg_color="transparent")
        title_section.grid(row=0, column=0, sticky="w")

        list_title = ctk.CTkLabel(
            title_section,
            text="📝 Your Tasks",
            font=ctk.CTkFont(size=max(16, self.current_font_size + 4), weight="bold")
        )
        list_title.pack(anchor="w")

        list_desc = ctk.CTkLabel(
            title_section,
            text="Manage and organize your tasks efficiently",
            font=ctk.CTkFont(size=max(10, self.current_font_size - 2)),
            text_color="gray"
        )
        list_desc.pack(anchor="w", pady=(2, 0))

        # Right side - View controls
        view_controls = ctk.CTkFrame(top_row, fg_color="transparent")
        view_controls.grid(row=0, column=2, sticky="e")

        # Page size selector with better styling
        page_size_container = ctk.CTkFrame(view_controls, corner_radius=8)
        page_size_container.pack(side="right", padx=(10, 0))

        page_size_inner = ctk.CTkFrame(page_size_container, fg_color="transparent")
        page_size_inner.pack(padx=12, pady=8)

        ctk.CTkLabel(
            page_size_inner,
            text="📄 Show:",
            font=ctk.CTkFont(size=11, weight="bold")
        ).pack(side="left", padx=(0, 8))

        self.page_size_var = tk.StringVar(value="5")
        page_size_combo = ctk.CTkComboBox(
            page_size_inner,
            variable=self.page_size_var,
            values=["5", "10", "20", "50", "100"],
            command=self.change_page_size,
            width=80,
            height=32,
            font=ctk.CTkFont(size=11),
            dropdown_font=ctk.CTkFont(size=11)
        )
        page_size_combo.pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            page_size_inner,
            text="per page",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        ).pack(side="left")

        # Task count display with better styling
        count_container = ctk.CTkFrame(view_controls, corner_radius=8)
        count_container.pack(side="right")

        self.task_count_label = ctk.CTkLabel(
            count_container,
            text="0 tasks",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="gray"
        )
        self.task_count_label.pack(padx=15, pady=8)

        # Middle row - Selection and bulk actions
        middle_row = ctk.CTkFrame(list_header, fg_color="transparent")
        middle_row.grid(row=1, column=0, columnspan=3, sticky="ew", padx=20, pady=(0, 15))
        middle_row.grid_columnconfigure(1, weight=1)

        # Left side - Selection controls
        selection_section = ctk.CTkFrame(middle_row, fg_color="transparent")
        selection_section.grid(row=0, column=0, sticky="w")

        # Bulk selection checkbox with better styling
        selection_container = ctk.CTkFrame(selection_section, corner_radius=8)
        selection_container.pack(side="left")

        selection_inner = ctk.CTkFrame(selection_container, fg_color="transparent")
        selection_inner.pack(padx=12, pady=8)

        self.select_all_var = tk.BooleanVar()
        self.select_all_checkbox = ctk.CTkCheckBox(
            selection_inner,
            text="Select All",
            variable=self.select_all_var,
            command=self.toggle_select_all,
            font=ctk.CTkFont(size=11, weight="bold"),
            checkbox_width=20,
            checkbox_height=20
        )
        self.select_all_checkbox.pack(side="left")

        # Instructions
        instructions_label = ctk.CTkLabel(
            selection_section,
            text="☑️ Select • ✅ Complete • ✏️ Edit • 🗑️ Delete",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        instructions_label.pack(side="left", padx=(15, 0))

        # Right side - Bulk actions with enhanced styling
        self.bulk_actions_frame = ctk.CTkFrame(middle_row, corner_radius=10)
        self.bulk_actions_frame.grid(row=0, column=2, sticky="e")

        bulk_inner = ctk.CTkFrame(self.bulk_actions_frame, fg_color="transparent")
        bulk_inner.pack(padx=15, pady=10)

        # Bulk actions title
        bulk_title = ctk.CTkLabel(
            bulk_inner,
            text="⚡ Bulk Actions:",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="gray"
        )
        bulk_title.pack(side="left", padx=(0, 10))

        # Enhanced bulk action buttons
        self.bulk_complete_btn = ctk.CTkButton(
            bulk_inner,
            text="✅ Complete",
            command=lambda: self.bulk_change_status("completed"),
            width=90,
            height=32,
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color="#22c55e",
            hover_color="#16a34a",
            corner_radius=8
        )
        self.bulk_complete_btn.pack(side="left", padx=3)

        self.bulk_pending_btn = ctk.CTkButton(
            bulk_inner,
            text="⏳ Pending",
            command=lambda: self.bulk_change_status("pending"),
            width=90,
            height=32,
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color="#f59e0b",
            hover_color="#d97706",
            corner_radius=8
        )
        self.bulk_pending_btn.pack(side="left", padx=3)

        self.bulk_progress_btn = ctk.CTkButton(
            bulk_inner,
            text="🔄 In Progress",
            command=lambda: self.bulk_change_status("in_progress"),
            width=100,
            height=32,
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color="#3b82f6",
            hover_color="#2563eb",
            corner_radius=8
        )
        self.bulk_progress_btn.pack(side="left", padx=3)

        # Initially hide bulk actions
        self.bulk_actions_frame.grid_remove()

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

    def on_search_change(self):
        """Handle search input changes with debouncing"""
        # Cancel any existing timer
        if hasattr(self, '_search_timer'):
            self.after_cancel(self._search_timer)

        # Set a new timer for 300ms delay
        self._search_timer = self.after(300, self.apply_filters)

    def clear_search(self):
        """Clear search input"""
        self.search_var.set("")
        self.search_entry.focus()

    def get_category_name(self, category_id):
        """Get category name by ID"""
        if not category_id:
            return ""
        try:
            categories = Category.get_all()
            for category in categories:
                if category.id == category_id:
                    return category.name
        except:
            pass
        return ""

    def get_priority_name(self, priority_id):
        """Get priority name by ID"""
        if not priority_id:
            return ""
        try:
            priorities = Priority.get_all()
            for priority in priorities:
                if priority.id == priority_id:
                    return priority.name
        except:
            pass
        return ""

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

            # Enhanced search functionality
            search_term = self.search_var.get().lower().strip()
            if search_term:
                search_filtered = []
                for task in filtered_tasks:
                    match_found = False

                    # Search in titles
                    if hasattr(self, 'search_titles') and self.search_titles.get():
                        if search_term in task.title.lower():
                            match_found = True

                    # Search in descriptions
                    if not match_found and hasattr(self, 'search_descriptions') and self.search_descriptions.get():
                        if task.description and search_term in task.description.lower():
                            match_found = True

                    # Search in categories
                    if not match_found and hasattr(self, 'search_categories') and self.search_categories.get():
                        category_name = self.get_category_name(task.category_id)
                        if category_name and search_term in category_name.lower():
                            match_found = True

                    # Search in priorities
                    if not match_found:
                        priority_name = self.get_priority_name(task.priority_id)
                        if priority_name and search_term in priority_name.lower():
                            match_found = True

                    # Search in status
                    if not match_found and search_term in task.status.lower():
                        match_found = True

                    if match_found:
                        search_filtered.append(task)

                filtered_tasks = search_filtered

            self.filtered_tasks = filtered_tasks
            self.current_page = 1  # Reset to first page when filters change
            self.update_pagination()
            self.update_search_results_info()
            self.display_tasks()

        except Exception as e:
            print(f"Error applying filters: {e}")

    def update_search_results_info(self):
        """Update search results information"""
        if not hasattr(self, 'search_results_label'):
            return

        search_term = self.search_var.get().strip()
        total_tasks = len(self.tasks)
        filtered_count = len(self.filtered_tasks)

        if search_term:
            if filtered_count == 0:
                self.search_results_label.configure(
                    text=f"❌ No results for '{search_term}'",
                    text_color="red"
                )
            elif filtered_count == total_tasks:
                self.search_results_label.configure(
                    text=f"✅ All {total_tasks} tasks match '{search_term}'",
                    text_color="green"
                )
            else:
                self.search_results_label.configure(
                    text=f"🔍 Found {filtered_count} of {total_tasks} tasks for '{search_term}'",
                    text_color="blue"
                )
        else:
            # No search term, show filter info
            if filtered_count < total_tasks:
                self.search_results_label.configure(
                    text=f"📋 Showing {filtered_count} of {total_tasks} tasks (filtered)",
                    text_color="gray"
                )
            else:
                self.search_results_label.configure(text="", text_color="gray")

    def display_tasks(self):
        """Display filtered tasks in the list with pagination"""
        # Clear existing task widgets and checkboxes
        for widget in self.task_list_frame.winfo_children():
            widget.destroy()
        self.task_checkboxes.clear()

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
        """Create widget for individual task with enhanced visual design"""
        # Enhanced task frame with better styling
        task_frame = ctk.CTkFrame(self.task_list_frame, corner_radius=10)
        task_frame.grid(row=index, column=0, sticky="ew", padx=8, pady=4)
        task_frame.grid_columnconfigure(2, weight=1)

        # Left section - Checkboxes with better spacing
        checkbox_section = ctk.CTkFrame(task_frame, fg_color="transparent")
        checkbox_section.grid(row=0, column=0, padx=15, pady=12, sticky="ns")

        # Bulk selection checkbox with enhanced styling
        task_selected = task.id in self.selected_tasks
        select_var = tk.BooleanVar(value=task_selected)
        select_check = ctk.CTkCheckBox(
            checkbox_section,
            text="",
            variable=select_var,
            command=lambda t=task, v=select_var: self.toggle_task_selection(t, v.get()),
            width=22,
            height=22,
            checkbox_width=22,
            checkbox_height=22,
            corner_radius=4
        )
        select_check.pack(side="top", pady=(0, 8))
        self.task_checkboxes[task.id] = select_var

        # Status checkbox with enhanced styling and tooltip-like behavior
        is_completed = (task.status == "completed")
        status_var = tk.BooleanVar(value=is_completed)
        status_check = ctk.CTkCheckBox(
            checkbox_section,
            text="",
            variable=status_var,
            command=lambda t=task, v=status_var: self.toggle_task_status(t, v.get()),
            width=22,
            height=22,
            checkbox_width=22,
            checkbox_height=22,
            corner_radius=4,
            fg_color="#22c55e" if is_completed else None,
            hover_color="#16a34a" if is_completed else None
        )
        status_check.pack(side="top")

        # Add visual indicator for checkbox purposes
        checkbox_labels = ctk.CTkFrame(checkbox_section, fg_color="transparent")
        checkbox_labels.pack(side="bottom", pady=(8, 0))

        ctk.CTkLabel(
            checkbox_labels,
            text="☑️",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        ).pack()

        ctk.CTkLabel(
            checkbox_labels,
            text="✅",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        ).pack(pady=(2, 0))



        # Task info section with enhanced visual design
        info_frame = ctk.CTkFrame(task_frame, fg_color="transparent")
        info_frame.grid(row=0, column=2, sticky="ew", padx=15, pady=15)
        info_frame.grid_columnconfigure(0, weight=1)

        # Priority indicator bar
        try:
            from services.theme_manager import theme_manager
            priority_colors = theme_manager.get_priority_colors()
            priority_name = "medium"  # default

            # Get priority name
            if task.priority_id:
                priorities = Priority.get_all()
                for p in priorities:
                    if p.id == task.priority_id:
                        priority_name = p.name.lower()
                        break

            priority_color = priority_colors.get(priority_name, "#3b82f6")

            # Priority indicator
            priority_indicator = ctk.CTkFrame(
                info_frame,
                height=3,
                fg_color=priority_color,
                corner_radius=2
            )
            priority_indicator.grid(row=0, column=0, sticky="ew", pady=(0, 5))

        except ImportError:
            pass  # Skip enhanced priority indicator if theme manager not available

        # Title with search highlighting
        title_text = task.title
        search_term = self.search_var.get().strip().lower()

        # Highlight search term in title
        if search_term and search_term in title_text.lower():
            title_color = "#FFD700"  # Gold color for highlighted text
        else:
            title_color = None

        title_label = ctk.CTkLabel(
            info_frame,
            text=title_text,
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
            text_color=title_color
        )
        title_label.grid(row=0, column=0, sticky="ew", padx=5)

        # Description (if exists) with search highlighting
        if task.description:
            desc_text = task.description[:100] + "..." if len(task.description) > 100 else task.description

            # Highlight search term in description
            desc_color = "gray"
            if search_term and search_term in desc_text.lower():
                desc_color = "#FFA500"  # Orange color for highlighted description

            desc_label = ctk.CTkLabel(
                info_frame,
                text=desc_text,
                font=ctk.CTkFont(size=11),
                text_color=desc_color,
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

        # Enable drag and drop for task
        try:
            from services.drag_drop_manager import drag_drop_manager
            drag_drop_manager.enable_task_drag_drop(
                task_frame,
                task.id,
                refresh_callback=self.refresh_data
            )
        except ImportError:
            pass  # Skip drag and drop if not available

        # Enhanced action buttons section
        actions_frame = ctk.CTkFrame(task_frame, fg_color="transparent")
        actions_frame.grid(row=0, column=3, padx=15, pady=15, sticky="ns")

        # Status indicator badge
        status_colors = {
            "pending": ("#f59e0b", "⏳"),
            "in_progress": ("#3b82f6", "🔄"),
            "completed": ("#22c55e", "✅")
        }

        status_color, status_icon = status_colors.get(task.status, ("#6b7280", "❓"))

        status_badge = ctk.CTkFrame(actions_frame, corner_radius=12, fg_color=status_color)
        status_badge.pack(side="top", pady=(0, 8))

        status_label = ctk.CTkLabel(
            status_badge,
            text=f"{status_icon} {task.status.replace('_', ' ').title()}",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color="white"
        )
        status_label.pack(padx=8, pady=4)

        # Enhanced action buttons
        edit_btn = ctk.CTkButton(
            actions_frame,
            text="✏️ Edit",
            command=lambda t=task: self.edit_task(t),
            width=70,
            height=30,
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color="#6366f1",
            hover_color="#4f46e5",
            corner_radius=8
        )
        edit_btn.pack(side="top", pady=2)

        delete_btn = ctk.CTkButton(
            actions_frame,
            text="🗑️ Delete",
            command=lambda t=task: self.delete_task(t),
            width=70,
            height=30,
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color="#ef4444",
            hover_color="#dc2626",
            corner_radius=8
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
        # Wait for dialog to close
        self.wait_window(dialog)

        # Check if task was created successfully
        if dialog.result:
            self.refresh_data()
            self.main_window.update_quick_stats()

    def clear_filters(self):
        """Clear all filters and search"""
        self.status_var.set("all")
        self.priority_var.set("all")
        self.category_var.set("all")
        self.search_var.set("")

        # Reset search options to default
        if hasattr(self, 'search_titles'):
            self.search_titles.set(True)
        if hasattr(self, 'search_descriptions'):
            self.search_descriptions.set(True)
        if hasattr(self, 'search_categories'):
            self.search_categories.set(True)

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
        # Update bulk selection state after refresh
        self.update_select_all_state()
        self.update_bulk_actions_visibility()

    def toggle_filter_panel(self):
        """Toggle the visibility of the filter panel content"""
        if self.filter_panel_collapsed:
            # Expand the panel
            self.filter_content.grid()
            self.collapse_btn.configure(text="◀ Hide")
            self.filter_panel_collapsed = False
            # Restore normal width
            self.grid_columnconfigure(0, weight=0, minsize=250)
        else:
            # Collapse the panel
            self.filter_content.grid_remove()
            self.collapse_btn.configure(text="▶ Show")
            self.filter_panel_collapsed = True
            # Minimize width
            self.grid_columnconfigure(0, weight=0, minsize=120)

    def toggle_task_selection(self, task, selected):
        """Toggle task selection for bulk operations"""
        if selected:
            self.selected_tasks.add(task.id)
        else:
            self.selected_tasks.discard(task.id)

        self.update_bulk_actions_visibility()
        self.update_select_all_state()

    def toggle_select_all(self):
        """Toggle selection of all visible tasks"""
        select_all = self.select_all_var.get()

        # Get current page tasks
        total_tasks = len(self.filtered_tasks)
        start_index = (self.current_page - 1) * self.page_size
        end_index = min(start_index + self.page_size, total_tasks)
        page_tasks = self.filtered_tasks[start_index:end_index]

        for task in page_tasks:
            if select_all:
                self.selected_tasks.add(task.id)
            else:
                self.selected_tasks.discard(task.id)

            # Update checkbox if it exists
            if task.id in self.task_checkboxes:
                self.task_checkboxes[task.id].set(select_all)

        self.update_bulk_actions_visibility()

    def update_select_all_state(self):
        """Update the select all checkbox state"""
        # Get current page tasks
        total_tasks = len(self.filtered_tasks)
        start_index = (self.current_page - 1) * self.page_size
        end_index = min(start_index + self.page_size, total_tasks)
        page_tasks = self.filtered_tasks[start_index:end_index]

        if not page_tasks:
            self.select_all_var.set(False)
            return

        # Check if all page tasks are selected
        all_selected = all(task.id in self.selected_tasks for task in page_tasks)
        self.select_all_var.set(all_selected)

    def update_bulk_actions_visibility(self):
        """Show/hide bulk actions based on selection"""
        if self.selected_tasks:
            self.bulk_actions_frame.grid()
            # Update select all text to show count
            count = len(self.selected_tasks)
            self.select_all_checkbox.configure(text=f"Selected ({count})")
        else:
            self.bulk_actions_frame.grid_remove()
            self.select_all_checkbox.configure(text="Select All")

    def bulk_change_status(self, new_status):
        """Change status of all selected tasks"""
        if not self.selected_tasks:
            messagebox.showwarning("No Selection", "Please select tasks to update.")
            return

        selected_count = len(self.selected_tasks)
        status_text = {
            "completed": "completed",
            "pending": "pending",
            "in_progress": "in progress"
        }.get(new_status, new_status)

        if messagebox.askyesno("Confirm Bulk Update",
                              f"Mark {selected_count} selected task(s) as {status_text}?"):
            try:
                updated_count = 0
                for task_id in list(self.selected_tasks):
                    task = next((t for t in self.tasks if t.id == task_id), None)
                    if task:
                        if new_status == "completed":
                            task.mark_completed()
                        else:
                            task.status = new_status
                            if new_status != "completed":
                                task.completed_at = None
                            task.save()
                        updated_count += 1

                # Clear selection
                self.selected_tasks.clear()
                self.task_checkboxes.clear()

                # Refresh display
                self.refresh_data()
                self.main_window.update_quick_stats()

                messagebox.showinfo("Success",
                                  f"Successfully updated {updated_count} task(s) to {status_text}!")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to update tasks: {e}")

    def update_fonts(self, font_size):
        """Update fonts throughout the task manager (called by font manager)"""
        try:
            self.current_font_size = font_size

            # Update all widgets recursively
            self.update_widget_fonts_recursive(self, font_size)

            # Refresh the task list to apply new fonts to task widgets
            self.display_tasks()

            print(f"Task manager fonts updated to {font_size}px")

        except Exception as e:
            print(f"Error updating task manager fonts: {e}")

    def update_widget_fonts_recursive(self, widget, font_size):
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
                self.update_widget_fonts_recursive(child, font_size)

        except Exception as e:
            pass  # Ignore errors for widgets that don't support font changes
