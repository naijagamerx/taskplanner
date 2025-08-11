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
            # Default to SQLite configuration
            return {
                'type': 'sqlite',
                'database': 'data/task_planner.db'
            }

    def show_dialog(self) -> Optional[Dict[str, Any]]:
        """Show database setup dialog"""
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title("Database Configuration")
        self.dialog.geometry("800x750")
        self.dialog.resizable(True, True)

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
        x = (self.dialog.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (750 // 2)
        self.dialog.geometry(f"800x750+{x}+{y}")

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
            text="Configure your database connection settings.\nNew to database setup? Check the 📖 Help & Tips tab for detailed guidance!",
            font=ctk.CTkFont(size=14),
            justify="center"
        )
        desc_label.pack(pady=(0, 20))

        # Quick tip
        tip_frame = ctk.CTkFrame(main_frame, fg_color="orange", corner_radius=8)
        tip_frame.pack(fill="x", pady=(0, 20), padx=20)

        ctk.CTkLabel(
            tip_frame,
            text="💡 Quick Tip: SQLite is recommended for most users - no server setup required!",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="white"
        ).pack(pady=10)

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

        help_btn = ctk.CTkButton(
            tab_button_frame,
            text="📖 Help & Tips",
            command=lambda: self.switch_tab("help"),
            width=120,
            fg_color="orange",
            hover_color="darkorange"
        )
        help_btn.pack(side="left", padx=5)

        # Tab content frame
        self.tab_content = ctk.CTkFrame(tab_frame)
        self.tab_content.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Create tab contents
        self.create_manual_tab()
        self.create_sqlite_tab()
        self.create_import_tab()
        self.create_help_tab()

        # Show appropriate tab based on current configuration
        if self.config.get('type') == 'sqlite':
            self.switch_tab("sqlite")
            # Set SQLite path from current config
            if 'database' in self.config:
                self.sqlite_path_var.set(self.config['database'])
        else:
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

    def create_help_tab(self):
        """Create help and tips tab"""
        self.help_frame = ctk.CTkScrollableFrame(self.tab_content)

        # Title
        title_frame = ctk.CTkFrame(self.help_frame)
        title_frame.pack(fill="x", padx=15, pady=15)

        ctk.CTkLabel(
            title_frame,
            text="📖 Database Configuration Help & Tips",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=15)

        # Quick Start Guide
        self.create_help_section(
            self.help_frame,
            "🚀 Quick Start Guide",
            """For most users, we recommend starting with SQLite:

1. Click the "SQLite (Portable)" tab
2. Keep the default path or choose a custom location
3. Click "Test Database Connection" to verify
4. Click "Save & Apply" to confirm

SQLite is perfect for single users and doesn't require any server setup!"""
        )

        # Database Types Comparison
        self.create_help_section(
            self.help_frame,
            "🔍 Database Types Comparison",
            """SQLite (Recommended for most users):
✅ No server setup required
✅ Portable - database travels with the app
✅ Perfect for single users
✅ Easy backup (just copy the .db file)
✅ No network configuration needed
❌ Not suitable for multiple concurrent users

MySQL (For advanced users/teams):
✅ Supports multiple concurrent users
✅ Better performance for large datasets
✅ Network accessible
✅ Advanced features and scalability
❌ Requires MySQL server installation
❌ More complex setup and maintenance"""
        )

        # MySQL Setup Guide
        self.create_help_section(
            self.help_frame,
            "🔧 MySQL Setup Guide",
            """If you choose MySQL, follow these steps:

1. Install MySQL Server:
   • Download from: https://dev.mysql.com/downloads/mysql/
   • Or use XAMPP/WAMP for easy installation
   • Make sure MySQL service is running

2. Create Database:
   • Open MySQL command line or phpMyAdmin
   • Create a new database: CREATE DATABASE task_planner;
   • Create a user (optional): CREATE USER 'taskuser'@'localhost' IDENTIFIED BY 'password';
   • Grant permissions: GRANT ALL PRIVILEGES ON task_planner.* TO 'taskuser'@'localhost';

3. Configure Connection:
   • Host: Usually 'localhost' for local installations
   • Port: Default is 3306
   • Username: 'root' or your custom user
   • Password: Your MySQL password
   • Database: 'task_planner' (or your database name)"""
        )

        # SQLite Setup Guide
        self.create_help_section(
            self.help_frame,
            "📁 SQLite Setup Guide",
            """SQLite is the easiest option:

1. Choose Database Location:
   • Default: 'data/task_planner.db' (recommended)
   • Custom: Click "Browse" to select any location
   • The folder will be created automatically if it doesn't exist

2. File Path Tips:
   • Use relative paths for portability (e.g., 'data/mydb.db')
   • Use absolute paths for fixed locations (e.g., 'C:\\MyApp\\database.db')
   • Avoid spaces in file names for compatibility

3. Backup & Sharing:
   • Simply copy the .db file to backup your data
   • Share the entire app folder to share with others
   • No server configuration needed!"""
        )

        # Troubleshooting Section
        self.create_help_section(
            self.help_frame,
            "🔧 Troubleshooting Common Issues",
            """Connection Failed Errors:

MySQL Issues:
• "Access denied" → Check username/password
• "Can't connect to server" → Ensure MySQL service is running
• "Unknown database" → Create the database first
• "Connection timeout" → Check host and port settings

SQLite Issues:
• "Permission denied" → Check folder write permissions
• "File not found" → Ensure the directory exists
• "Database locked" → Close other applications using the file

General Tips:
• Always test the connection before saving
• Check firewall settings for MySQL connections
• Use "localhost" instead of "127.0.0.1" for local connections
• Restart the application after changing database type"""
        )

        # Import/Export Section
        self.create_help_section(
            self.help_frame,
            "📤 Import/Export Configuration",
            """Configuration Files:

Export Current Settings:
• Click "Export Current Configuration" to save your settings
• Creates a JSON file with all connection details
• Useful for backup or sharing configurations

Import Settings:
• Click "Import Config" tab to load saved configurations
• Select a previously exported JSON file
• All fields will be automatically filled

Use Cases:
• Backup your database settings
• Share configurations with team members
• Quickly switch between different database setups
• Deploy the same configuration to multiple computers"""
        )

        # Security Section
        self.create_help_section(
            self.help_frame,
            "🔒 Security Best Practices",
            """Keep Your Data Safe:

Password Security:
• Use strong passwords for MySQL connections
• Don't share configuration files with passwords
• Consider using environment variables for sensitive data

File Permissions:
• Ensure SQLite database files have proper permissions
• Restrict access to configuration files
• Regular backups are essential

Network Security:
• Use localhost for local MySQL connections
• Configure firewall rules for remote connections
• Use SSL/TLS for production environments
• Limit database user privileges to minimum required"""
        )

        # Contact and Support Section
        self.create_help_section(
            self.help_frame,
            "💬 Need More Help?",
            """Still having trouble? Here's how to get support:

Documentation:
• Check the application's user manual
• Visit our online documentation
• Review the FAQ section

Community Support:
• Join our user community forum
• Search for similar issues
• Ask questions and share solutions

Technical Support:
• Contact our support team for technical issues
• Include your configuration details (without passwords)
• Describe the exact error messages you're seeing

Remember: SQLite is recommended for most users and requires no additional setup!"""
        )

    def create_help_section(self, parent, title, content):
        """Create a help section with title and content"""
        section_frame = ctk.CTkFrame(parent)
        section_frame.pack(fill="x", padx=15, pady=10)

        # Title
        ctk.CTkLabel(
            section_frame,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))

        # Content
        ctk.CTkLabel(
            section_frame,
            text=content,
            font=ctk.CTkFont(size=11),
            justify="left",
            anchor="w"
        ).pack(anchor="w", padx=15, pady=(0, 15), fill="x")

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
        elif tab_name == "help":
            self.help_frame.pack(fill="both", expand=True)

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

        # Display configuration based on type
        if self.config.get('type') == 'sqlite':
            config_text = f"""Type: SQLite Database
Database File: {self.config.get('database', 'N/A')}
Status: ✅ Portable & Self-contained"""
        else:
            config_text = f"""Type: MySQL Database
Host: {self.config.get('host', 'N/A')}
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
            print("Testing database connection...")

            if self.tab_var.get() == "sqlite":
                # Test SQLite
                try:
                    import sqlite3
                    db_path = self.sqlite_path_var.get().strip()

                    if not db_path:
                        messagebox.showerror("Error", "Please specify a database path")
                        return

                    # Ensure directory exists
                    db_dir = os.path.dirname(db_path)
                    if db_dir:
                        os.makedirs(db_dir, exist_ok=True)

                    # Test connection
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
                    cursor.close()
                    conn.close()

                    print("SQLite connection test successful")
                    messagebox.showinfo("Success", "SQLite database connection successful!")

                except sqlite3.Error as e:
                    print(f"SQLite error: {e}")
                    messagebox.showerror("SQLite Error", f"SQLite connection failed:\n{str(e)}")
                except Exception as e:
                    print(f"SQLite unexpected error: {e}")
                    messagebox.showerror("Error", f"SQLite test failed:\n{str(e)}")
            else:
                # Test MySQL
                try:
                    # Validate input fields
                    host = self.host_var.get().strip()
                    port_str = self.port_var.get().strip()
                    user = self.user_var.get().strip()
                    password = self.password_var.get()
                    database = self.database_var.get().strip()

                    if not host:
                        messagebox.showerror("Error", "Please specify a host")
                        return
                    if not port_str:
                        messagebox.showerror("Error", "Please specify a port")
                        return
                    if not user:
                        messagebox.showerror("Error", "Please specify a username")
                        return
                    if not database:
                        messagebox.showerror("Error", "Please specify a database name")
                        return

                    try:
                        port = int(port_str)
                        if port <= 0 or port > 65535:
                            raise ValueError("Port must be between 1 and 65535")
                    except ValueError as e:
                        messagebox.showerror("Error", f"Invalid port number: {e}")
                        return

                    config = {
                        'host': host,
                        'port': port,
                        'user': user,
                        'password': password,
                        'database': database,
                        'connect_timeout': 10,  # 10 second timeout
                        'autocommit': True
                    }

                    print(f"Testing MySQL connection to {host}:{port}")

                    # Import mysql.connector
                    try:
                        import mysql.connector
                        from mysql.connector import Error
                    except ImportError:
                        messagebox.showerror("Error",
                                           "MySQL connector not available.\n\n"
                                           "Please install it with:\n"
                                           "pip install mysql-connector-python")
                        return

                    # Test connection
                    connection = mysql.connector.connect(**config)

                    if connection.is_connected():
                        # Test basic query
                        cursor = connection.cursor()
                        cursor.execute("SELECT 1")
                        cursor.fetchone()
                        cursor.close()
                        connection.close()

                        print("MySQL connection test successful")
                        messagebox.showinfo("Success",
                                          f"MySQL database connection successful!\n\n"
                                          f"Host: {host}:{port}\n"
                                          f"Database: {database}\n"
                                          f"User: {user}")
                    else:
                        messagebox.showerror("Error", "Failed to establish MySQL connection")

                except mysql.connector.Error as e:
                    print(f"MySQL connector error: {e}")
                    error_msg = f"MySQL connection failed:\n\n{str(e)}"
                    if "Access denied" in str(e):
                        error_msg += "\n\nPlease check your username and password."
                    elif "Can't connect" in str(e):
                        error_msg += "\n\nPlease check if MySQL server is running and the host/port are correct."
                    messagebox.showerror("MySQL Error", error_msg)
                except Exception as e:
                    print(f"MySQL unexpected error: {e}")
                    messagebox.showerror("Error", f"MySQL test failed:\n{str(e)}")

        except Exception as e:
            print(f"Test connection unexpected error: {e}")
            messagebox.showerror("Error", f"Connection test failed:\n{str(e)}")
            # Don't re-raise the exception to prevent app crash

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
