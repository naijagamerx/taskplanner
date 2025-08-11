"""
License Activation Window for Task Planner
Shows hardware ID and allows license key entry
"""

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from typing import Optional

# Simple clipboard utility
def copy_to_clipboard(text: str, root_widget):
    """Copy text to clipboard"""
    try:
        root_widget.clipboard_clear()
        root_widget.clipboard_append(text)
        root_widget.update()  # Required for clipboard to work
        return True
    except Exception:
        return False


class LicenseActivationWindow:
    """License activation dialog"""

    def __init__(self, parent, license_manager):
        self.parent = parent
        self.license_manager = license_manager
        self.result = False
        self.window = None

        # Get hardware info
        self.hardware_info = license_manager.get_hardware_info()
        self.hardware_id = license_manager.get_hardware_id()

    def show(self) -> bool:
        """Show license activation window and return result"""
        self.create_window()
        self.window.wait_window()
        return self.result

    def create_window(self):
        """Create the license activation window"""
        self.window = ctk.CTkToplevel(self.parent)
        self.window.title("Task Planner - License Activation")
        self.window.geometry("600x700")
        self.window.resizable(False, False)

        # Center the window on screen
        self.center_window()

        # Make window modal
        self.window.transient(self.parent)
        self.window.grab_set()

        # Bring window to front
        self.window.lift()
        self.window.focus_force()
        self.window.attributes('-topmost', True)
        self.window.after(100, lambda: self.window.attributes('-topmost', False))

        # Configure grid
        self.window.grid_columnconfigure(0, weight=1)

        # Main frame
        main_frame = ctk.CTkFrame(self.window)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)

        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="🔐 License Activation Required",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=(20, 10))

        # Description
        desc_text = (
            "Welcome to Task Planner!\n\n"
            "To activate your license, please follow these steps:\n"
            "1. Copy your Hardware ID below\n"
            "2. Send it to your administrator\n"
            "3. Enter the license key you receive"
        )
        desc_label = ctk.CTkLabel(
            main_frame,
            text=desc_text,
            font=ctk.CTkFont(size=14),
            justify="left"
        )
        desc_label.grid(row=1, column=0, pady=10, padx=20)

        # Hardware ID Section
        hw_frame = ctk.CTkFrame(main_frame)
        hw_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        hw_frame.grid_columnconfigure(1, weight=1)

        hw_label = ctk.CTkLabel(
            hw_frame,
            text="Hardware ID:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        hw_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.hw_entry = ctk.CTkEntry(
            hw_frame,
            font=ctk.CTkFont(size=12, family="Courier"),
            state="readonly"
        )
        self.hw_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.hw_entry.configure(state="normal")
        self.hw_entry.insert(0, self.hardware_id)
        self.hw_entry.configure(state="readonly")

        copy_btn = ctk.CTkButton(
            hw_frame,
            text="📋 Copy",
            width=80,
            command=self.copy_hardware_id
        )
        copy_btn.grid(row=0, column=2, padx=10, pady=10)

        # System Info Section
        info_frame = ctk.CTkFrame(main_frame)
        info_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=10)
        info_frame.grid_columnconfigure(0, weight=1)

        info_label = ctk.CTkLabel(
            info_frame,
            text="System Information:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        info_label.grid(row=0, column=0, pady=(10, 5), sticky="w", padx=10)

        system_info = (
            f"System: {self.hardware_info['system']}\n"
            f"Machine: {self.hardware_info['machine']}\n"
            f"Processor: {self.hardware_info['processor'][:50]}..."
        )

        info_text = ctk.CTkLabel(
            info_frame,
            text=system_info,
            font=ctk.CTkFont(size=12),
            justify="left"
        )
        info_text.grid(row=1, column=0, pady=(0, 10), padx=10, sticky="w")

        # License Key Section
        license_frame = ctk.CTkFrame(main_frame)
        license_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=10)
        license_frame.grid_columnconfigure(0, weight=1)

        license_label = ctk.CTkLabel(
            license_frame,
            text="Enter License Key:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        license_label.grid(row=0, column=0, pady=(10, 5), sticky="w", padx=10)

        self.license_entry = ctk.CTkEntry(
            license_frame,
            placeholder_text="XXXX-XXXX-XXXX-XXXX",
            font=ctk.CTkFont(size=14, family="Courier")
        )
        self.license_entry.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        # User Name Section
        name_label = ctk.CTkLabel(
            license_frame,
            text="User Name (Optional):",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        name_label.grid(row=2, column=0, pady=(5, 5), sticky="w", padx=10)

        self.name_entry = ctk.CTkEntry(
            license_frame,
            placeholder_text="Enter your name"
        )
        self.name_entry.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="ew")

        # Buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.grid(row=5, column=0, sticky="ew", padx=20, pady=10)
        button_frame.grid_columnconfigure((0, 1, 2), weight=1)

        trial_btn = ctk.CTkButton(
            button_frame,
            text="🆓 Start Trial (30 days)",
            command=self.start_trial,
            fg_color="orange",
            hover_color="darkorange"
        )
        trial_btn.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        activate_btn = ctk.CTkButton(
            button_frame,
            text="✅ Activate License",
            command=self.activate_license
        )
        activate_btn.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        exit_btn = ctk.CTkButton(
            button_frame,
            text="❌ Exit",
            command=self.exit_application,
            fg_color="red",
            hover_color="darkred"
        )
        exit_btn.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

        # Status label
        self.status_label = ctk.CTkLabel(
            main_frame,
            text="",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.grid(row=6, column=0, pady=10)

        # Focus on license entry
        self.license_entry.focus()

        # Bind Enter key
        self.license_entry.bind("<Return>", lambda e: self.activate_license())

    def center_window(self):
        """Center the window on the screen"""
        self.window.update_idletasks()

        # Get window dimensions
        window_width = 600
        window_height = 700

        # Get screen dimensions
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        # Calculate center position
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)

        # Set window position
        self.window.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

    def copy_hardware_id(self):
        """Copy hardware ID to clipboard"""
        try:
            if copy_to_clipboard(self.hardware_id, self.window):
                self.status_label.configure(
                    text="✅ Hardware ID copied to clipboard!",
                    text_color="green"
                )
                self.window.after(3000, lambda: self.status_label.configure(text=""))
            else:
                raise Exception("Clipboard operation failed")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy to clipboard: {e}")

    def start_trial(self):
        """Start trial license"""
        try:
            user_name = self.name_entry.get().strip() or "Trial User"

            # Check if trial already used
            if self.license_manager.current_license and self.license_manager.current_license.get('license_type') == 'trial':
                # Check if trial is still valid
                if self.license_manager.is_license_valid():
                    license_info = self.license_manager.get_license_info()
                    days_remaining = license_info.get('days_remaining', 0)
                    messagebox.showinfo(
                        "Trial Active",
                        f"Trial license is already active!\n\n"
                        f"Days remaining: {days_remaining}\n"
                        f"User: {license_info.get('user_name', 'Trial User')}"
                    )
                    self.result = True
                    self.window.destroy()
                    return
                else:
                    # Trial has expired
                    messagebox.showwarning(
                        "Trial Expired",
                        "🕐 Your 30-day trial period has expired.\n\n"
                        "✨ Thank you for trying Task Planner!\n\n"
                        "To continue using Task Planner:\n"
                        "• Contact your administrator for a license key\n"
                        "• Or purchase a license from our website\n\n"
                        "💡 All your data has been saved and will be available\n"
                        "   when you activate a full license."
                    )
                    # Don't return - allow user to enter a license key
                    # Clear the expired trial license
                    self.license_manager.deactivate_license()

            success, message = self.license_manager.start_trial(user_name)

            if success:
                license_info = self.license_manager.get_license_info()
                days_remaining = license_info.get('days_remaining', 30)
                messagebox.showinfo(
                    "Trial Started",
                    f"🎉 Trial license activated successfully!\n\n"
                    f"✅ You have {days_remaining} days to evaluate Task Planner\n"
                    f"👤 User: {user_name}\n\n"
                    f"💡 You can purchase a license anytime during the trial period."
                )
                self.result = True
                self.window.destroy()
            else:
                messagebox.showerror("Trial Failed", message)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to start trial: {e}")

    def activate_license(self):
        """Activate license with provided key"""
        try:
            license_key = self.license_entry.get().strip()
            user_name = self.name_entry.get().strip()

            if not license_key:
                messagebox.showerror("Error", "Please enter a license key")
                return

            self.status_label.configure(
                text="🔄 Activating license...",
                text_color="blue"
            )
            self.window.update()

            success, message = self.license_manager.activate_license(license_key, user_name)

            if success:
                license_info = self.license_manager.get_license_info()

                # Format expiration info properly
                expires_text = "Never"
                if license_info.get('expires_at'):
                    days_remaining = license_info.get('days_remaining', 0)
                    if days_remaining > 0:
                        expires_text = f"{days_remaining} days"
                    else:
                        expires_text = "Expired"

                messagebox.showinfo(
                    "License Activated",
                    f"License activated successfully!\n\n"
                    f"License Type: {license_info['license_type'].title()}\n"
                    f"User: {license_info['user_name']}\n"
                    f"Expires: {expires_text}"
                )
                self.result = True
                self.window.destroy()
            else:
                self.status_label.configure(
                    text=f"❌ {message}",
                    text_color="red"
                )

        except Exception as e:
            self.status_label.configure(
                text=f"❌ Error: {e}",
                text_color="red"
            )

    def exit_application(self):
        """Exit the application"""
        if messagebox.askyesno(
            "Exit Application",
            "Are you sure you want to exit Task Planner?\n\n"
            "You will need a valid license to use the application."
        ):
            self.result = False
            self.window.destroy()


if __name__ == "__main__":
    # Test the license activation window
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

    from auth.license_manager import LicenseManager

    root = ctk.CTk()
    root.withdraw()

    license_manager = LicenseManager()
    window = LicenseActivationWindow(root, license_manager)
    result = window.show()

    print(f"Activation result: {result}")
    root.destroy()
