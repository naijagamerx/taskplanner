"""
Database Setup Dialog for Task Planner
Allows users to configure database connection settings
"""

import tkinter as tk
from tkinter import messagebox, filedialog
import customtkinter as ctk
import json
import os
import sys
import mysql.connector
from typing import Dict, Any, Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class DatabaseSetupDialog:
    """Database configuration dialog"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.result = None
        self.dialog = None
        self.config = self.load_current_config()
        
    def load_current_config(self) -> Dict[str, Any]:
        """Load current database configuration"""
        try:
            from config.database_config import DatabaseConfig
            db_config = DatabaseConfig()
            return db_config.get_config()
        except:
            return {
                'host': 'localhost',
                'port': 3306,
                'user': 'root',
                'password': '',
                'database': 'task_planner'
            }
    
    def show_dialog(self) -> Optional[Dict[str, Any]]:
        """Show database setup dialog"""
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title("Database Configuration")
        self.dialog.geometry("600x700")
        self.dialog.resizable(False, False)
        
        # Make dialog modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.center_dialog()
        
        self.create_widgets()
        
        # Wait for dialog to close
        self.dialog.wait_window()
        
        return self.result
    
    def center_dialog(self):
        """Center dialog on screen"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (700 // 2)
        self.dialog.geometry(f"600x700+{x}+{y}")
    
    def create_widgets(self):
        """Create dialog widgets"""
        # Main container
        main_frame = ctk.CTkScrollableFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="🗄️ Database Configuration",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Description
        desc_label = ctk.CTkLabel(
            main_frame,
            text="Configure your database connection settings.\nChoose from the options below:",
            font=ctk.CTkFont(size=14),
            justify="center"
        )
        desc_label.pack(pady=(0, 30))
        
        # Configuration options
        self.create_option_tabs(main_frame)
        
        # Current configuration display
        self.create_current_config_display(main_frame)
        
        # Test connection section
        self.create_test_section(main_frame)
        
        # Buttons
        self.create_buttons(main_frame)
    
    def create_option_tabs(self, parent):
        """Create configuration option tabs"""
        # Tab frame
        tab_frame = ctk.CTkFrame(parent)
        tab_frame.pack(fill="x", pady=(0, 20))
        
        # Tab buttons
        self.tab_var = tk.StringVar(value="manual")
        
        tab_button_frame = ctk.CTkFrame(tab_frame)
        tab_button_frame.pack(fill="x", padx=10, pady=10)
        
        manual_btn = ctk.CTkButton(
            tab_button_frame,
            text="Manual Setup",
            command=lambda: self.switch_tab("manual"),
            width=120
        )
        manual_btn.pack(side="left", padx=5)
        
        sqlite_btn = ctk.CTkButton(
            tab_button_frame,
            text="SQLite (Portable)",
            command=lambda: self.switch_tab("sqlite"),
            width=120
        )
        sqlite_btn.pack(side="left", padx=5)
        
        import_btn = ctk.CTkButton(
            tab_button_frame,
            text="Import Config",
            command=lambda: self.switch_tab("import"),
            width=120
        )
        import_btn.pack(side="left", padx=5)
        
        # Tab content frame
        self.tab_content = ctk.CTkFrame(tab_frame)
        self.tab_content.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Create tab contents
        self.create_manual_tab()
        self.create_sqlite_tab()
        self.create_import_tab()
        
        # Show default tab
        self.switch_tab("manual")
    
    def create_manual_tab(self):
        """Create manual configuration tab"""
        self.manual_frame = ctk.CTkFrame(self.tab_content)
        
        # Manual configuration form
        form_frame = ctk.CTkFrame(self.manual_frame)
        form_frame.pack(fill="x", padx=15, pady=15)
        
        # Host
        ctk.CTkLabel(form_frame, text="Host:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        self.host_var = tk.StringVar(value=self.config.get('host', 'localhost'))
        self.host_entry = ctk.CTkEntry(form_frame, textvariable=self.host_var, placeholder_text="localhost")
        self.host_entry.pack(fill="x", padx=10, pady=(0, 10))
        
        # Port
        ctk.CTkLabel(form_frame, text="Port:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(0, 5))
        self.port_var = tk.StringVar(value=str(self.config.get('port', 3306)))
        self.port_entry = ctk.CTkEntry(form_frame, textvariable=self.port_var, placeholder_text="3306")
        self.port_entry.pack(fill="x", padx=10, pady=(0, 10))
        
        # Username
        ctk.CTkLabel(form_frame, text="Username:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(0, 5))
        self.user_var = tk.StringVar(value=self.config.get('user', 'root'))
        self.user_entry = ctk.CTkEntry(form_frame, textvariable=self.user_var, placeholder_text="root")
        self.user_entry.pack(fill="x", padx=10, pady=(0, 10))
        
        # Password
        ctk.CTkLabel(form_frame, text="Password:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(0, 5))
        self.password_var = tk.StringVar(value=self.config.get('password', ''))
        self.password_entry = ctk.CTkEntry(form_frame, textvariable=self.password_var, show="*", placeholder_text="Enter password")
        self.password_entry.pack(fill="x", padx=10, pady=(0, 10))
        
        # Database name
        ctk.CTkLabel(form_frame, text="Database Name:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(0, 5))
        self.database_var = tk.StringVar(value=self.config.get('database', 'task_planner'))
        self.database_entry = ctk.CTkEntry(form_frame, textvariable=self.database_var, placeholder_text="task_planner")
        self.database_entry.pack(fill="x", padx=10, pady=(0, 15))
    
    def create_sqlite_tab(self):
        """Create SQLite configuration tab"""
        self.sqlite_frame = ctk.CTkFrame(self.tab_content)
        
        info_frame = ctk.CTkFrame(self.sqlite_frame)
        info_frame.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkLabel(
            info_frame,
            text="🗃️ SQLite Database (Recommended for Portability)",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        ctk.CTkLabel(
            info_frame,
            text="SQLite creates a local database file that travels with your app.\n"
                 "Perfect for single-user installations and easy distribution.",
            font=ctk.CTkFont(size=12),
            justify="center"
        ).pack(pady=10)
        
        # SQLite file location
        file_frame = ctk.CTkFrame(info_frame)
        file_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(file_frame, text="Database File Location:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        location_frame = ctk.CTkFrame(file_frame, fg_color="transparent")
        location_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.sqlite_path_var = tk.StringVar(value="data/task_planner.db")
        self.sqlite_path_entry = ctk.CTkEntry(location_frame, textvariable=self.sqlite_path_var)
        self.sqlite_path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        browse_btn = ctk.CTkButton(
            location_frame,
            text="Browse",
            command=self.browse_sqlite_file,
            width=80
        )
        browse_btn.pack(side="right")
        
        # Benefits
        benefits_text = """✅ No server setup required
✅ Portable - database travels with app
✅ Perfect for single users
✅ Easy backup and sharing
✅ No network configuration needed"""
        
        ctk.CTkLabel(
            info_frame,
            text=benefits_text,
            font=ctk.CTkFont(size=11),
            justify="left"
        ).pack(pady=10)
    
    def create_import_tab(self):
        """Create import configuration tab"""
        self.import_frame = ctk.CTkFrame(self.tab_content)
        
        info_frame = ctk.CTkFrame(self.import_frame)
        info_frame.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkLabel(
            info_frame,
            text="📁 Import Configuration",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        ctk.CTkLabel(
            info_frame,
            text="Import database configuration from a JSON file.",
            font=ctk.CTkFont(size=12)
        ).pack(pady=5)
        
        import_btn = ctk.CTkButton(
            info_frame,
            text="📂 Select Configuration File",
            command=self.import_config_file,
            height=40
        )
        import_btn.pack(pady=20)
        
        # Export current config
        export_btn = ctk.CTkButton(
            info_frame,
            text="💾 Export Current Configuration",
            command=self.export_config_file,
            height=40,
            fg_color="gray",
            hover_color="darkgray"
        )
        export_btn.pack(pady=10)
    
    def switch_tab(self, tab_name):
        """Switch between configuration tabs"""
        # Hide all tabs
        for widget in self.tab_content.winfo_children():
            widget.pack_forget()
        
        # Show selected tab
        if tab_name == "manual":
            self.manual_frame.pack(fill="both", expand=True)
        elif tab_name == "sqlite":
            self.sqlite_frame.pack(fill="both", expand=True)
        elif tab_name == "import":
            self.import_frame.pack(fill="both", expand=True)
        
        self.tab_var.set(tab_name)
    
    def browse_sqlite_file(self):
        """Browse for SQLite database file"""
        filename = filedialog.asksaveasfilename(
            title="Select SQLite Database File",
            defaultextension=".db",
            filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")]
        )
        if filename:
            self.sqlite_path_var.set(filename)
    
    def import_config_file(self):
        """Import configuration from JSON file"""
        filename = filedialog.askopenfilename(
            title="Select Configuration File",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r') as f:
                    config = json.load(f)
                
                # Update form fields
                self.host_var.set(config.get('host', 'localhost'))
                self.port_var.set(str(config.get('port', 3306)))
                self.user_var.set(config.get('user', 'root'))
                self.password_var.set(config.get('password', ''))
                self.database_var.set(config.get('database', 'task_planner'))
                
                messagebox.showinfo("Success", "Configuration imported successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import configuration: {e}")
    
    def export_config_file(self):
        """Export current configuration to JSON file"""
        filename = filedialog.asksaveasfilename(
            title="Save Configuration File",
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if filename:
            try:
                config = {
                    'host': self.host_var.get(),
                    'port': int(self.port_var.get()),
                    'user': self.user_var.get(),
                    'password': self.password_var.get(),
                    'database': self.database_var.get()
                }
                
                with open(filename, 'w') as f:
                    json.dump(config, f, indent=2)
                
                messagebox.showinfo("Success", "Configuration exported successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export configuration: {e}")
    
    def create_current_config_display(self, parent):
        """Create current configuration display"""
        config_frame = ctk.CTkFrame(parent)
        config_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            config_frame,
            text="Current Configuration",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))
        
        config_text = f"""Host: {self.config.get('host', 'N/A')}
Port: {self.config.get('port', 'N/A')}
User: {self.config.get('user', 'N/A')}
Database: {self.config.get('database', 'N/A')}"""
        
        self.config_display = ctk.CTkLabel(
            config_frame,
            text=config_text,
            font=ctk.CTkFont(size=11),
            justify="left"
        )
        self.config_display.pack(pady=(0, 10))
    
    def create_test_section(self, parent):
        """Create test connection section"""
        test_frame = ctk.CTkFrame(parent)
        test_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            test_frame,
            text="Test Connection",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))
        
        test_btn = ctk.CTkButton(
            test_frame,
            text="🔍 Test Database Connection",
            command=self.test_connection,
            height=40,
            font=ctk.CTkFont(size=12)
        )
        test_btn.pack(pady=(0, 10))
    
    def create_buttons(self, parent):
        """Create dialog buttons"""
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(fill="x", pady=20)
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.cancel,
            width=100,
            fg_color="gray",
            hover_color="darkgray"
        )
        cancel_btn.pack(side="right", padx=(10, 0))
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="Save & Apply",
            command=self.save_config,
            width=120
        )
        save_btn.pack(side="right")
    
    def test_connection(self):
        """Test database connection with current settings"""
        try:
            if self.tab_var.get() == "sqlite":
                # Test SQLite
                import sqlite3
                db_path = self.sqlite_path_var.get()
                os.makedirs(os.path.dirname(db_path), exist_ok=True)
                conn = sqlite3.connect(db_path)
                conn.close()
                messagebox.showinfo("Success", "SQLite database connection successful!")
            else:
                # Test MySQL
                config = {
                    'host': self.host_var.get(),
                    'port': int(self.port_var.get()),
                    'user': self.user_var.get(),
                    'password': self.password_var.get(),
                    'database': self.database_var.get()
                }
                
                connection = mysql.connector.connect(**config)
                if connection.is_connected():
                    connection.close()
                    messagebox.showinfo("Success", "MySQL database connection successful!")
                
        except Exception as e:
            messagebox.showerror("Connection Failed", f"Database connection failed:\n{str(e)}")
    
    def save_config(self):
        """Save configuration and close dialog"""
        try:
            if self.tab_var.get() == "sqlite":
                # SQLite configuration
                self.result = {
                    'type': 'sqlite',
                    'database': self.sqlite_path_var.get()
                }
            else:
                # MySQL configuration
                self.result = {
                    'type': 'mysql',
                    'host': self.host_var.get(),
                    'port': int(self.port_var.get()),
                    'user': self.user_var.get(),
                    'password': self.password_var.get(),
                    'database': self.database_var.get()
                }
            
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Invalid configuration: {e}")
    
    def cancel(self):
        """Cancel dialog"""
        self.result = None
        self.dialog.destroy()
