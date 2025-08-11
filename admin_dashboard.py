"""
Admin Dashboard for Task Planner License Management
Generates license keys for specific hardware IDs
"""

import tkinter as tk
from tkinter import messagebox, ttk
import customtkinter as ctk
import json
import hashlib
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List


class LicenseKeyGenerator:
    """Generate license keys for specific hardware IDs"""

    def __init__(self):
        self.license_database_file = self._get_license_database_path()
        self.licenses = self.load_license_database()

    def _get_license_database_path(self) -> str:
        """Get the path for license database in AppData directory"""
        import os
        import sys

        if sys.platform == "win32":
            # Windows: %APPDATA%/TaskPlanner/license_database.json
            app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
            app_dir = os.path.join(app_data, 'TaskPlanner')
        elif sys.platform == "darwin":
            # macOS: ~/Library/Application Support/TaskPlanner/license_database.json
            app_dir = os.path.expanduser('~/Library/Application Support/TaskPlanner')
        else:
            # Linux: ~/.config/TaskPlanner/license_database.json
            config_dir = os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
            app_dir = os.path.join(config_dir, 'TaskPlanner')

        # Create directory if it doesn't exist
        os.makedirs(app_dir, exist_ok=True)
        return os.path.join(app_dir, 'license_database.json')

    def load_license_database(self) -> Dict[str, Any]:
        """Load existing license database"""
        if os.path.exists(self.license_database_file):
            try:
                with open(self.license_database_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {"licenses": [], "next_id": 1}

    def save_license_database(self):
        """Save license database"""
        try:
            with open(self.license_database_file, 'w') as f:
                json.dump(self.licenses, f, indent=2)
        except Exception as e:
            print(f"Error saving license database: {e}")

    def generate_license_key(self, hardware_id: str, license_type: str,
                           user_name: str, duration_days: int = None) -> str:
        """Generate a license key for specific hardware ID"""
        try:
            # Create license data
            license_id = self.licenses["next_id"]
            self.licenses["next_id"] += 1

            issued_at = datetime.now()
            expires_at = None

            if duration_days:
                expires_at = issued_at + timedelta(days=duration_days)

            # Generate license key based on hardware ID and license type
            key_data = f"{license_type.upper()}{hardware_id}{license_id}"
            key_hash = hashlib.sha256(key_data.encode()).hexdigest()[:16].upper()

            # Format as XXXX-XXXX-XXXX-XXXX
            license_key = f"{key_hash[0:4]}-{key_hash[4:8]}-{key_hash[8:12]}-{key_hash[12:16]}"

            # Store license record
            license_record = {
                "id": license_id,
                "license_key": license_key,
                "hardware_id": hardware_id,
                "license_type": license_type,
                "user_name": user_name,
                "issued_at": issued_at.isoformat(),
                "expires_at": expires_at.isoformat() if expires_at else None,
                "status": "active",
                "generated_by": "admin",
                "generated_at": datetime.now().isoformat()
            }

            self.licenses["licenses"].append(license_record)
            self.save_license_database()

            return license_key

        except Exception as e:
            raise Exception(f"Failed to generate license key: {e}")

    def get_all_licenses(self) -> List[Dict[str, Any]]:
        """Get all generated licenses"""
        return self.licenses.get("licenses", [])

    def revoke_license(self, license_key: str) -> bool:
        """Revoke a license"""
        try:
            for license_record in self.licenses["licenses"]:
                if license_record["license_key"] == license_key:
                    license_record["status"] = "revoked"
                    license_record["revoked_at"] = datetime.now().isoformat()
                    self.save_license_database()
                    return True
            return False
        except:
            return False

    def delete_license(self, license_key: str) -> bool:
        """Permanently delete a license"""
        try:
            original_count = len(self.licenses["licenses"])
            self.licenses["licenses"] = [
                license_record for license_record in self.licenses["licenses"]
                if license_record["license_key"] != license_key
            ]

            if len(self.licenses["licenses"]) < original_count:
                self.save_license_database()
                return True
            return False
        except:
            return False


class AdminDashboard:
    """Admin dashboard for license management"""

    def __init__(self):
        self.generator = LicenseKeyGenerator()
        self.root = None
        self.setup_ui()

    def setup_ui(self):
        """Setup the admin dashboard UI"""
        # Configure CustomTkinter
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("Task Planner - Admin License Dashboard")
        self.root.geometry("1400x900")  # Increased from 1000x700 to 1400x900

        # Configure grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        # Title
        title_label = ctk.CTkLabel(
            self.root,
            text="🔐 Task Planner License Management Dashboard",
            font=ctk.CTkFont(size=32, weight="bold")  # Increased from 24 to 32
        )
        title_label.grid(row=0, column=0, pady=20)

        # Main content frame
        main_frame = ctk.CTkFrame(self.root)
        main_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        main_frame.grid_columnconfigure((0, 1), weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

        # License generation frame
        self.create_generation_frame(main_frame)

        # License list frame
        self.create_license_list_frame(main_frame)

        # Status bar
        self.status_label = ctk.CTkLabel(
            self.root,
            text="Ready",
            font=ctk.CTkFont(size=16)  # Increased from 12 to 16
        )
        self.status_label.grid(row=2, column=0, pady=10)

        # Load existing licenses
        self.refresh_license_list()

    def create_generation_frame(self, parent):
        """Create license generation frame"""
        gen_frame = ctk.CTkFrame(parent)
        gen_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)
        gen_frame.grid_columnconfigure(1, weight=1)

        # Title
        gen_title = ctk.CTkLabel(
            gen_frame,
            text="🔑 Generate New License",
            font=ctk.CTkFont(size=24, weight="bold")  # Increased from 18 to 24
        )
        gen_title.grid(row=0, column=0, columnspan=2, pady=10)

        # Hardware ID
        ctk.CTkLabel(gen_frame, text="Hardware ID:", font=ctk.CTkFont(size=16)).grid(row=1, column=0, padx=10, pady=8, sticky="w")
        self.hardware_id_entry = ctk.CTkEntry(gen_frame, placeholder_text="Enter hardware ID from user",
                                            font=ctk.CTkFont(size=14), height=35)
        self.hardware_id_entry.grid(row=1, column=1, padx=10, pady=8, sticky="ew")

        # User Name
        ctk.CTkLabel(gen_frame, text="User Name:", font=ctk.CTkFont(size=16)).grid(row=2, column=0, padx=10, pady=8, sticky="w")
        self.user_name_entry = ctk.CTkEntry(gen_frame, placeholder_text="Enter user name",
                                          font=ctk.CTkFont(size=14), height=35)
        self.user_name_entry.grid(row=2, column=1, padx=10, pady=8, sticky="ew")

        # License Type
        ctk.CTkLabel(gen_frame, text="License Type:", font=ctk.CTkFont(size=16)).grid(row=3, column=0, padx=10, pady=8, sticky="w")
        self.license_type_var = ctk.StringVar(value="professional")
        license_type_menu = ctk.CTkOptionMenu(
            gen_frame,
            variable=self.license_type_var,
            values=["trial", "basic", "professional", "enterprise"],
            font=ctk.CTkFont(size=14),
            height=35
        )
        license_type_menu.grid(row=3, column=1, padx=10, pady=8, sticky="ew")

        # Duration (for trial/basic)
        ctk.CTkLabel(gen_frame, text="Duration (days):", font=ctk.CTkFont(size=16)).grid(row=4, column=0, padx=10, pady=8, sticky="w")
        self.duration_entry = ctk.CTkEntry(gen_frame, placeholder_text="Leave empty for unlimited",
                                         font=ctk.CTkFont(size=14), height=35)
        self.duration_entry.grid(row=4, column=1, padx=10, pady=8, sticky="ew")

        # Generate button
        generate_btn = ctk.CTkButton(
            gen_frame,
            text="🔑 Generate License Key",
            command=self.generate_license,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40
        )
        generate_btn.grid(row=5, column=0, columnspan=2, padx=10, pady=20, sticky="ew")

        # Generated key display
        ctk.CTkLabel(gen_frame, text="Generated License Key:", font=ctk.CTkFont(size=16)).grid(row=6, column=0, padx=10, pady=8, sticky="w")
        self.generated_key_entry = ctk.CTkEntry(gen_frame, state="readonly",
                                              font=ctk.CTkFont(family="Courier", size=13), height=35)
        self.generated_key_entry.grid(row=6, column=1, padx=10, pady=8, sticky="ew")

        # Copy button
        copy_btn = ctk.CTkButton(
            gen_frame,
            text="📋 Copy Key",
            command=self.copy_generated_key,
            font=ctk.CTkFont(size=14),
            width=120,
            height=35
        )
        copy_btn.grid(row=7, column=1, padx=10, pady=8, sticky="e")

    def create_license_list_frame(self, parent):
        """Create license list frame"""
        list_frame = ctk.CTkFrame(parent)
        list_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=10)
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(2, weight=1)

        # Title
        list_title = ctk.CTkLabel(
            list_frame,
            text="📋 Generated Licenses",
            font=ctk.CTkFont(size=24, weight="bold")  # Increased from 18 to 24
        )
        list_title.grid(row=0, column=0, pady=(10, 5))

        # Instruction label
        instruction_label = ctk.CTkLabel(
            list_frame,
            text="💡 Double-click any license to copy its key to clipboard",
            font=ctk.CTkFont(size=14),  # Increased from 12 to 14
            text_color="gray"
        )
        instruction_label.grid(row=1, column=0, pady=(0, 10))

        # License list (using tkinter Treeview for better table display)
        columns = ("License Key", "User", "Type", "Hardware ID", "Status", "Expires")
        self.license_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=18)

        # Configure style for larger fonts
        style = ttk.Style()
        style.configure("Treeview", font=("TkDefaultFont", 11))
        style.configure("Treeview.Heading", font=("TkDefaultFont", 12, "bold"))

        # Configure columns with larger widths
        for col in columns:
            self.license_tree.heading(col, text=col)
            if col == "License Key":
                self.license_tree.column(col, width=200)  # Increased from 150
            elif col == "Hardware ID":
                self.license_tree.column(col, width=160)  # Increased from 120
            elif col == "User":
                self.license_tree.column(col, width=140)  # Increased from 100
            else:
                self.license_tree.column(col, width=120)  # Increased from 100

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.license_tree.yview)
        self.license_tree.configure(yscrollcommand=scrollbar.set)

        # Grid the treeview and scrollbar
        self.license_tree.grid(row=2, column=0, sticky="nsew", padx=(10, 0), pady=10)
        scrollbar.grid(row=2, column=1, sticky="ns", pady=10)

        # Bind double-click event to copy license key
        self.license_tree.bind("<Double-1>", self.on_license_double_click)

        # Bind right-click event for context menu
        self.license_tree.bind("<Button-3>", self.show_context_menu)

        # Buttons frame
        btn_frame = ctk.CTkFrame(list_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        btn_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        refresh_btn = ctk.CTkButton(btn_frame, text="🔄 Refresh", command=self.refresh_license_list,
                                  font=ctk.CTkFont(size=14), height=40)
        refresh_btn.grid(row=0, column=0, padx=5, pady=5)

        copy_key_btn = ctk.CTkButton(btn_frame, text="📋 Copy License Key", command=self.copy_selected_license_key,
                                   fg_color="#2E8B57", font=ctk.CTkFont(size=14), height=40)
        copy_key_btn.grid(row=0, column=1, padx=5, pady=5)

        revoke_btn = ctk.CTkButton(btn_frame, text="❌ Revoke Selected", command=self.revoke_selected_license,
                                 fg_color="red", font=ctk.CTkFont(size=14), height=40)
        revoke_btn.grid(row=0, column=2, padx=5, pady=5)

        delete_btn = ctk.CTkButton(btn_frame, text="🗑️ Delete Selected", command=self.delete_selected_license,
                                 fg_color="#9C27B0", font=ctk.CTkFont(size=14), height=40)
        delete_btn.grid(row=0, column=3, padx=5, pady=5)

        export_btn = ctk.CTkButton(btn_frame, text="💾 Export List", command=self.export_license_list,
                                 font=ctk.CTkFont(size=14), height=40)
        export_btn.grid(row=0, column=4, padx=5, pady=5)

    def generate_license(self):
        """Generate a new license key"""
        try:
            hardware_id = self.hardware_id_entry.get().strip()
            user_name = self.user_name_entry.get().strip()
            license_type = self.license_type_var.get()
            duration_str = self.duration_entry.get().strip()

            if not hardware_id:
                messagebox.showerror("Error", "Please enter a hardware ID")
                return

            if not user_name:
                messagebox.showerror("Error", "Please enter a user name")
                return

            # Parse duration
            duration_days = None
            if duration_str:
                try:
                    duration_days = int(duration_str)
                except ValueError:
                    messagebox.showerror("Error", "Duration must be a number")
                    return

            # Generate license key
            license_key = self.generator.generate_license_key(
                hardware_id, license_type, user_name, duration_days
            )

            # Display generated key
            self.generated_key_entry.configure(state="normal")
            self.generated_key_entry.delete(0, tk.END)
            self.generated_key_entry.insert(0, license_key)
            self.generated_key_entry.configure(state="readonly")

            # Update status
            self.status_label.configure(text=f"✅ License generated for {user_name}")

            # Refresh license list
            self.refresh_license_list()

            # Clear form
            self.hardware_id_entry.delete(0, tk.END)
            self.user_name_entry.delete(0, tk.END)
            self.duration_entry.delete(0, tk.END)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate license: {e}")

    def copy_generated_key(self):
        """Copy generated license key to clipboard"""
        try:
            key = self.generated_key_entry.get()
            if key:
                self.root.clipboard_clear()
                self.root.clipboard_append(key)
                self.root.update()
                self.status_label.configure(text="📋 License key copied to clipboard")
            else:
                messagebox.showwarning("Warning", "No license key to copy")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy to clipboard: {e}")

    def copy_selected_license_key(self):
        """Copy selected license key from the list to clipboard"""
        try:
            selection = self.license_tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a license to copy its key")
                return

            item = self.license_tree.item(selection[0])
            license_key = item["values"][0]
            user_name = item["values"][1]

            if license_key:
                self.root.clipboard_clear()
                self.root.clipboard_append(license_key)
                self.root.update()
                self.status_label.configure(text=f"📋 License key for {user_name} copied to clipboard")
            else:
                messagebox.showwarning("Warning", "No license key found")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy license key: {e}")

    def on_license_double_click(self, event):
        """Handle double-click on license list to copy license key"""
        try:
            # Get the item that was double-clicked
            item_id = self.license_tree.identify_row(event.y)
            if item_id:
                # Select the item
                self.license_tree.selection_set(item_id)
                # Copy the license key
                self.copy_selected_license_key()
        except Exception as e:
            print(f"Error handling double-click: {e}")

    def show_context_menu(self, event):
        """Show context menu on right-click"""
        try:
            # Get the item that was right-clicked
            item_id = self.license_tree.identify_row(event.y)
            if item_id:
                # Select the item
                self.license_tree.selection_set(item_id)

                # Create context menu
                context_menu = tk.Menu(self.root, tearoff=0)
                context_menu.add_command(label="📋 Copy License Key", command=self.copy_selected_license_key)
                context_menu.add_separator()
                context_menu.add_command(label="❌ Revoke License", command=self.revoke_selected_license)
                context_menu.add_command(label="🗑️ Delete License", command=self.delete_selected_license)

                # Show context menu
                context_menu.tk_popup(event.x_root, event.y_root)

        except Exception as e:
            print(f"Error showing context menu: {e}")

    def refresh_license_list(self):
        """Refresh the license list"""
        try:
            # Clear existing items
            for item in self.license_tree.get_children():
                self.license_tree.delete(item)

            # Add licenses
            licenses = self.generator.get_all_licenses()
            for license_record in reversed(licenses):  # Show newest first
                # Format expiration display
                expires_at = license_record.get("expires_at")
                if expires_at:
                    try:
                        from datetime import datetime
                        expiry_date = datetime.fromisoformat(expires_at)
                        days_remaining = (expiry_date - datetime.now()).days
                        if days_remaining > 0:
                            expiry_display = f"{days_remaining} days"
                        elif days_remaining == 0:
                            expiry_display = "Today"
                        else:
                            expiry_display = "Expired"
                    except:
                        expiry_display = "Invalid"
                else:
                    expiry_display = "Never"

                self.license_tree.insert("", "end", values=(
                    license_record.get("license_key", ""),
                    license_record.get("user_name", ""),
                    license_record.get("license_type", ""),
                    license_record.get("hardware_id", "")[:16] + "...",  # Truncate for display
                    license_record.get("status", ""),
                    expiry_display  # Show expiration instead of issued date
                ))

            self.status_label.configure(text=f"📋 {len(licenses)} licenses loaded")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh license list: {e}")

    def revoke_selected_license(self):
        """Revoke the selected license"""
        try:
            selection = self.license_tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a license to revoke")
                return

            item = self.license_tree.item(selection[0])
            license_key = item["values"][0]

            if messagebox.askyesno("Confirm", f"Are you sure you want to revoke license {license_key}?"):
                if self.generator.revoke_license(license_key):
                    self.refresh_license_list()
                    self.status_label.configure(text=f"❌ License {license_key} revoked")
                else:
                    messagebox.showerror("Error", "Failed to revoke license")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to revoke license: {e}")

    def delete_selected_license(self):
        """Permanently delete the selected license"""
        try:
            selection = self.license_tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a license to delete")
                return

            item = self.license_tree.item(selection[0])
            license_key = item["values"][0]
            user_name = item["values"][1]

            # Double confirmation for permanent deletion
            if messagebox.askyesno("Confirm Deletion",
                                 f"⚠️ PERMANENT DELETION ⚠️\n\n"
                                 f"Are you sure you want to permanently delete this license?\n\n"
                                 f"License Key: {license_key}\n"
                                 f"User: {user_name}\n\n"
                                 f"This action CANNOT be undone!"):

                if messagebox.askyesno("Final Confirmation",
                                     f"This will permanently remove the license from the database.\n\n"
                                     f"Are you absolutely sure?"):

                    if self.generator.delete_license(license_key):
                        self.refresh_license_list()
                        self.status_label.configure(text=f"🗑️ License {license_key} permanently deleted")
                    else:
                        messagebox.showerror("Error", "Failed to delete license")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete license: {e}")

    def export_license_list(self):
        """Export license list to JSON file"""
        try:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )

            if filename:
                licenses = self.generator.get_all_licenses()
                with open(filename, 'w') as f:
                    json.dump(licenses, f, indent=2)

                self.status_label.configure(text=f"💾 License list exported to {filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to export license list: {e}")

    def run(self):
        """Run the admin dashboard"""
        self.root.mainloop()


if __name__ == "__main__":
    print("Task Planner - Admin License Dashboard")
    print("=" * 50)

    # Run file migration to AppData (for compiled executables)
    if getattr(sys, 'frozen', False):
        try:
            # Simple migration for admin dashboard
            import shutil
            if os.path.exists('license_database.json'):
                # Get AppData directory
                if sys.platform == "win32":
                    app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
                    app_dir = os.path.join(app_data, 'TaskPlanner')
                else:
                    app_dir = os.path.expanduser('~/.config/TaskPlanner')

                os.makedirs(app_dir, exist_ok=True)
                dest_path = os.path.join(app_dir, 'license_database.json')

                if not os.path.exists(dest_path):
                    shutil.copy2('license_database.json', dest_path)
                    os.remove('license_database.json')
                    print("Migrated license database to AppData")
        except Exception as e:
            print(f"Migration warning: {e}")

    dashboard = AdminDashboard()
    dashboard.run()
