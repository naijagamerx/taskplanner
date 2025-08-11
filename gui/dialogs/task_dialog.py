"""
Task creation and editing dialog
"""

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from datetime import datetime, time
from tkcalendar import DateEntry
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from models.task import Task
from models.category import Category, Priority
from gui.dialogs.help_dialog import HelpDialog


class ToolTip:
    """Simple tooltip class for widgets"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)

    def on_enter(self, event=None):
        if self.tooltip_window or not self.text:
            return
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + 25

        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        label = tk.Label(tw, text=self.text, justify='left',
                        background="#ffffe0", relief='solid', borderwidth=1,
                        font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def on_leave(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

class TaskDialog(ctk.CTkToplevel):
    """Task creation and editing dialog"""

    def __init__(self, parent, task=None):
        super().__init__(parent)
        self.parent = parent
        self.task = task
        self.result = None
        self.categories = []
        self.priorities = []

        self.setup_dialog()
        self.load_data()
        self.setup_ui()

        if self.task:
            self.populate_fields()

        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        self.focus()

    def setup_dialog(self):
        """Setup dialog window"""
        title = "Edit Task" if self.task else "Add New Task"
        self.title(title)
        self.geometry("600x750")
        self.resizable(True, True)
        self.minsize(550, 650)

        # Center dialog
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.winfo_screenheight() // 2) - (750 // 2)
        self.geometry(f"600x750+{x}+{y}")

    def load_data(self):
        """Load categories and priorities"""
        try:
            self.categories = Category.get_all()
            self.priorities = Priority.get_all()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {e}")
            self.categories = []
            self.priorities = []

    def setup_ui(self):
        """Setup dialog UI"""
        # Main frame
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title_text = "Edit Task" if self.task else "Create New Task"
        title_label = ctk.CTkLabel(
            main_frame,
            text=title_text,
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(10, 20))

        # Buttons frame (fixed at bottom)
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(10, 10), side="bottom")

        # Cancel button
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.cancel,
            width=100,
            fg_color="gray",
            hover_color="darkgray"
        )
        cancel_btn.pack(side="right", padx=(10, 0))

        # Help button
        help_btn = ctk.CTkButton(
            button_frame,
            text="❓ Help",
            command=self.show_help,
            width=80,
            fg_color="gray",
            hover_color="darkgray"
        )
        help_btn.pack(side="left")

        # Save button
        save_text = "Update" if self.task else "Create"
        save_btn = ctk.CTkButton(
            button_frame,
            text=save_text,
            command=self.save_task,
            width=100
        )
        save_btn.pack(side="right")

        # Scrollable form frame
        form_frame = ctk.CTkScrollableFrame(main_frame)
        form_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Task title
        ctk.CTkLabel(form_frame, text="Title *", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=15, pady=(15, 5))
        self.title_entry = ctk.CTkEntry(form_frame, placeholder_text="Enter task title...")
        self.title_entry.pack(fill="x", padx=15, pady=(0, 10))
        ToolTip(self.title_entry, "Give your task a clear, descriptive name")

        # Description
        ctk.CTkLabel(form_frame, text="Description", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=15, pady=(10, 5))
        self.description_text = ctk.CTkTextbox(form_frame, height=80)
        self.description_text.pack(fill="x", padx=15, pady=(0, 10))
        ToolTip(self.description_text, "Add details, notes, or steps for this task (optional)")

        # Category and Priority row
        cat_pri_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        cat_pri_frame.pack(fill="x", padx=15, pady=10)
        cat_pri_frame.grid_columnconfigure(0, weight=1)
        cat_pri_frame.grid_columnconfigure(1, weight=1)

        # Category
        ctk.CTkLabel(cat_pri_frame, text="Category", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky="w", padx=(0, 10))
        category_values = ["None"] + [cat.name for cat in self.categories]
        self.category_combo = ctk.CTkComboBox(cat_pri_frame, values=category_values)
        self.category_combo.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(5, 0))
        ToolTip(self.category_combo, "Organize your task by category")

        # Priority
        ctk.CTkLabel(cat_pri_frame, text="Priority", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, sticky="w")
        priority_values = [pri.name for pri in self.priorities]
        self.priority_combo = ctk.CTkComboBox(cat_pri_frame, values=priority_values)
        self.priority_combo.grid(row=1, column=1, sticky="ew", pady=(5, 0))
        ToolTip(self.priority_combo, "Set the importance level of this task")

        # Force update the ComboBox values after creation
        if category_values:
            self.category_combo.configure(values=category_values)
        if priority_values:
            self.priority_combo.configure(values=priority_values)

        # Due date and time row
        date_time_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        date_time_frame.pack(fill="x", padx=15, pady=10)
        date_time_frame.grid_columnconfigure(0, weight=1)
        date_time_frame.grid_columnconfigure(1, weight=1)

        # Due date
        ctk.CTkLabel(date_time_frame, text="Due Date", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.date_var = tk.StringVar()
        self.date_entry = DateEntry(
            date_time_frame,
            textvariable=self.date_var,
            date_pattern='yyyy-mm-dd',
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2
        )
        self.date_entry.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(5, 0))
        ToolTip(self.date_entry, "Set when this task should be completed (optional)")

        # Due time
        ctk.CTkLabel(date_time_frame, text="Due Time", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, sticky="w")
        self.time_entry = ctk.CTkEntry(date_time_frame, placeholder_text="HH:MM")
        self.time_entry.grid(row=1, column=1, sticky="ew", pady=(5, 0))
        ToolTip(self.time_entry, "Set when this task should be completed (24-hour format)")

        # Estimated duration
        ctk.CTkLabel(form_frame, text="Estimated Duration (minutes)", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=15, pady=(10, 5))
        self.duration_entry = ctk.CTkEntry(form_frame, placeholder_text="e.g., 30")
        self.duration_entry.pack(fill="x", padx=15, pady=(0, 10))
        ToolTip(self.duration_entry, "How long do you think this task will take? (in minutes)")

        # Status (for editing)
        if self.task:
            ctk.CTkLabel(form_frame, text="Status", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=15, pady=(10, 5))
            status_values = ["pending", "in_progress", "completed", "cancelled"]
            self.status_combo = ctk.CTkComboBox(form_frame, values=status_values)
            self.status_combo.pack(fill="x", padx=15, pady=(0, 10))

        # Recurring task options
        recurring_frame = ctk.CTkFrame(form_frame)
        recurring_frame.pack(fill="x", padx=15, pady=10)

        self.recurring_var = tk.BooleanVar()
        recurring_check = ctk.CTkCheckBox(
            recurring_frame,
            text="Recurring Task",
            variable=self.recurring_var,
            command=self.toggle_recurring_options
        )
        recurring_check.pack(anchor="w", padx=15, pady=10)

        # Recurring options (initially hidden)
        self.recurring_options_frame = ctk.CTkFrame(recurring_frame)

        # Pattern
        ctk.CTkLabel(self.recurring_options_frame, text="Pattern", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=15, pady=(10, 5))
        pattern_values = ["daily", "weekly", "monthly", "yearly"]
        self.pattern_combo = ctk.CTkComboBox(self.recurring_options_frame, values=pattern_values)
        self.pattern_combo.pack(fill="x", padx=15, pady=(0, 10))

        # Interval
        ctk.CTkLabel(self.recurring_options_frame, text="Every", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=15, pady=(5, 5))
        self.interval_entry = ctk.CTkEntry(self.recurring_options_frame, placeholder_text="1")
        self.interval_entry.pack(fill="x", padx=15, pady=(0, 15))

        # Set default values after a small delay to ensure ComboBoxes are ready
        self.after(100, self.set_default_values)

    def set_default_values(self):
        """Set default values for ComboBoxes"""
        try:
            # Set priority default
            if self.priorities and len(self.priorities) > 1:
                default_priority = self.priorities[1].name
                self.priority_combo.set(default_priority)
            elif self.priorities:
                default_priority = self.priorities[0].name
                self.priority_combo.set(default_priority)

            # Set category default
            self.category_combo.set("None")

            # Set recurring defaults
            self.pattern_combo.set("daily")
            self.interval_entry.insert(0, "1")

        except Exception:
            pass  # Silently handle any errors

    def toggle_recurring_options(self):
        """Toggle recurring task options visibility"""
        if self.recurring_var.get():
            self.recurring_options_frame.pack(fill="x", padx=15, pady=(0, 10))
        else:
            self.recurring_options_frame.pack_forget()

    def populate_fields(self):
        """Populate fields when editing a task"""
        if not self.task:
            return

        # Basic fields
        self.title_entry.insert(0, self.task.title)
        if self.task.description:
            self.description_text.insert("1.0", self.task.description)

        # Category
        if self.task.category_id:
            try:
                category = Category.get_by_id(self.task.category_id)
                if category:
                    self.category_combo.set(category.name)
            except:
                pass

        # Priority
        if self.task.priority_id:
            try:
                priority = Priority.get_by_id(self.task.priority_id)
                if priority:
                    self.priority_combo.set(priority.name)
            except:
                pass

        # Due date
        if self.task.due_date:
            self.date_entry.set_date(self.task.due_date)

        # Due time
        if self.task.due_time:
            self.time_entry.insert(0, str(self.task.due_time))

        # Duration
        if self.task.estimated_duration:
            self.duration_entry.insert(0, str(self.task.estimated_duration))

        # Status
        if hasattr(self, 'status_combo'):
            self.status_combo.set(self.task.status)

        # Recurring
        if self.task.is_recurring:
            self.recurring_var.set(True)
            self.toggle_recurring_options()
            if self.task.recurrence_pattern:
                self.pattern_combo.set(self.task.recurrence_pattern)
            if self.task.recurrence_interval:
                self.interval_entry.delete(0, tk.END)
                self.interval_entry.insert(0, str(self.task.recurrence_interval))

    def save_task(self):
        """Save task to database"""
        try:
            # Validate required fields
            title = self.title_entry.get().strip()
            if not title:
                messagebox.showerror("Error", "Task title is required!")
                return

            # Create or update task
            if self.task:
                task = self.task
            else:
                task = Task()

            # Set basic fields
            task.title = title
            task.description = self.description_text.get("1.0", tk.END).strip()

            # Category
            category_name = self.category_combo.get()
            if category_name != "None":
                category = Category.get_by_name(category_name)
                task.category_id = category.id if category else None
            else:
                task.category_id = None

            # Priority
            priority_name = self.priority_combo.get()
            for priority in self.priorities:
                if priority.name == priority_name:
                    task.priority_id = priority.id
                    break

            # Due date
            try:
                due_date_str = self.date_var.get()
                if due_date_str:
                    task.due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
                else:
                    task.due_date = None
            except ValueError:
                task.due_date = None

            # Due time
            time_str = self.time_entry.get().strip()
            if time_str:
                try:
                    task.due_time = datetime.strptime(time_str, '%H:%M').time()
                except ValueError:
                    messagebox.showerror("Error", "Invalid time format! Use HH:MM")
                    return
            else:
                task.due_time = None

            # Duration
            duration_str = self.duration_entry.get().strip()
            if duration_str:
                try:
                    task.estimated_duration = int(duration_str)
                except ValueError:
                    messagebox.showerror("Error", "Duration must be a number!")
                    return
            else:
                task.estimated_duration = None

            # Status (for editing only - new tasks should remain pending)
            if hasattr(self, 'status_combo') and self.task is not None:
                task.status = self.status_combo.get()
            elif self.task is None:
                # Ensure new tasks are always pending
                task.status = "pending"

            # Recurring options
            task.is_recurring = self.recurring_var.get()
            if task.is_recurring:
                task.recurrence_pattern = self.pattern_combo.get()
                interval_str = self.interval_entry.get().strip()
                try:
                    task.recurrence_interval = int(interval_str) if interval_str else 1
                except ValueError:
                    task.recurrence_interval = 1
            else:
                task.recurrence_pattern = None
                task.recurrence_interval = 1

            # Save task
            if task.save():
                self.result = task
                success_msg = "Task updated successfully!" if self.task else "Task created successfully!"
                messagebox.showinfo("Success", success_msg)
                self.destroy()
            else:
                messagebox.showerror("Error", "Failed to save task!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save task: {e}")

    def show_help(self):
        """Show help dialog"""
        HelpDialog(self)

    def cancel(self):
        """Cancel dialog"""
        self.result = None
        self.destroy()
