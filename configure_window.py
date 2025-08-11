"""
Window Configuration Utility for Task Planner
Allows users to set their preferred window startup behavior
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.window_config import window_config

def show_current_settings():
    """Display current window settings"""
    print("📋 Current Window Settings:")
    print("=" * 40)
    
    settings = [
        ("Startup Mode", window_config.get_setting("startup_mode")),
        ("Window Width", window_config.get_setting("window_width")),
        ("Window Height", window_config.get_setting("window_height")),
        ("Center on Startup", window_config.get_setting("center_on_startup")),
        ("Screen Percentage", f"{window_config.get_setting('screen_percentage') * 100:.0f}%"),
        ("Focus on Startup", window_config.get_setting("focus_on_startup")),
        ("Always on Top (startup)", window_config.get_setting("always_on_top_startup"))
    ]
    
    for setting, value in settings:
        print(f"  • {setting}: {value}")
    print()

def configure_startup_mode():
    """Configure window startup mode"""
    print("🖥️  Window Startup Mode Configuration")
    print("=" * 40)
    print("Choose your preferred startup mode:")
    print()
    print("1. 📏 Centered Large (90% of screen, centered)")
    print("2. 🔳 Maximized (full screen)")
    print("3. ⚙️  Custom Size (specify dimensions)")
    print("4. ↩️  Keep Current Setting")
    print()
    
    try:
        choice = input("Enter your choice (1-4): ").strip()
        
        if choice == "1":
            window_config.update_setting("startup_mode", "centered_large")
            print("✅ Set to Centered Large mode")
            
            # Ask for screen percentage
            try:
                percentage = input("Enter screen percentage (70-95, default 90): ").strip()
                if percentage:
                    pct = float(percentage) / 100
                    if 0.7 <= pct <= 0.95:
                        window_config.update_setting("screen_percentage", pct)
                        print(f"✅ Screen percentage set to {percentage}%")
                    else:
                        print("⚠️  Invalid percentage, keeping default (90%)")
            except ValueError:
                print("⚠️  Invalid input, keeping default percentage")
        
        elif choice == "2":
            window_config.update_setting("startup_mode", "maximized")
            print("✅ Set to Maximized mode")
        
        elif choice == "3":
            window_config.update_setting("startup_mode", "custom")
            print("✅ Set to Custom mode")
            
            # Configure custom dimensions
            try:
                width = input("Enter window width (800-2000, default 1200): ").strip()
                if width:
                    w = int(width)
                    if 800 <= w <= 2000:
                        window_config.update_setting("window_width", w)
                        print(f"✅ Width set to {width}")
                    else:
                        print("⚠️  Invalid width, keeping default (1200)")
            except ValueError:
                print("⚠️  Invalid width, keeping default")
            
            try:
                height = input("Enter window height (600-1200, default 800): ").strip()
                if height:
                    h = int(height)
                    if 600 <= h <= 1200:
                        window_config.update_setting("window_height", h)
                        print(f"✅ Height set to {height}")
                    else:
                        print("⚠️  Invalid height, keeping default (800)")
            except ValueError:
                print("⚠️  Invalid height, keeping default")
        
        elif choice == "4":
            print("↩️  Keeping current setting")
        
        else:
            print("❌ Invalid choice")
            return False
        
        return True
        
    except KeyboardInterrupt:
        print("\n👋 Configuration cancelled")
        return False

def configure_other_settings():
    """Configure other window settings"""
    print("\n⚙️  Other Window Settings")
    print("=" * 30)
    
    settings = [
        ("center_on_startup", "Center window on startup", "boolean"),
        ("focus_on_startup", "Focus window on startup", "boolean"),
        ("always_on_top_startup", "Show on top at startup", "boolean")
    ]
    
    for key, description, setting_type in settings:
        current = window_config.get_setting(key)
        try:
            if setting_type == "boolean":
                choice = input(f"{description} (y/n, current: {'y' if current else 'n'}): ").strip().lower()
                if choice in ['y', 'yes']:
                    window_config.update_setting(key, True)
                    print(f"✅ {description}: Enabled")
                elif choice in ['n', 'no']:
                    window_config.update_setting(key, False)
                    print(f"✅ {description}: Disabled")
                else:
                    print(f"↩️  Keeping current setting: {'Enabled' if current else 'Disabled'}")
        except KeyboardInterrupt:
            print("\n👋 Configuration cancelled")
            break

def reset_settings():
    """Reset all settings to defaults"""
    print("\n🔄 Reset Settings")
    print("=" * 20)
    
    try:
        confirm = input("Reset all window settings to defaults? (y/n): ").strip().lower()
        if confirm in ['y', 'yes']:
            if window_config.reset_to_defaults():
                print("✅ All settings reset to defaults")
                return True
            else:
                print("❌ Failed to reset settings")
                return False
        else:
            print("↩️  Reset cancelled")
            return False
    except KeyboardInterrupt:
        print("\n👋 Reset cancelled")
        return False

def test_window():
    """Test the current window settings"""
    print("\n🧪 Test Window Settings")
    print("=" * 25)
    
    try:
        test = input("Open a test window with current settings? (y/n): ").strip().lower()
        if test in ['y', 'yes']:
            print("🚀 Opening test window...")
            
            try:
                import customtkinter as ctk
                
                # Set appearance
                ctk.set_appearance_mode("light")
                ctk.set_default_color_theme("blue")
                
                # Create test window
                root = ctk.CTk()
                root.title("Task Planner - Window Test")
                
                # Apply window settings
                window_config.apply_window_settings(root)
                
                # Add test content
                label = ctk.CTkLabel(
                    root,
                    text="Window Settings Test\n\nThis is how your Task Planner\nwindow will appear on startup.",
                    font=ctk.CTkFont(size=16)
                )
                label.pack(expand=True)
                
                close_btn = ctk.CTkButton(
                    root,
                    text="Close Test Window",
                    command=root.destroy,
                    width=200,
                    height=40
                )
                close_btn.pack(pady=20)
                
                print("✅ Test window opened! Check your screen.")
                print("💡 Close the test window when done.")
                
                root.mainloop()
                
            except Exception as e:
                print(f"❌ Error opening test window: {e}")
                
    except KeyboardInterrupt:
        print("\n👋 Test cancelled")

def main():
    """Main configuration function"""
    print("=" * 50)
    print("🖥️  Task Planner Window Configuration")
    print("=" * 50)
    print()
    
    while True:
        show_current_settings()
        
        print("🔧 Configuration Options:")
        print("1. 🖥️  Configure Startup Mode")
        print("2. ⚙️  Configure Other Settings")
        print("3. 🧪 Test Current Settings")
        print("4. 🔄 Reset to Defaults")
        print("5. 💾 Save and Exit")
        print("6. ❌ Exit without Saving")
        print()
        
        try:
            choice = input("Enter your choice (1-6): ").strip()
            
            if choice == "1":
                configure_startup_mode()
            elif choice == "2":
                configure_other_settings()
            elif choice == "3":
                test_window()
            elif choice == "4":
                reset_settings()
            elif choice == "5":
                print("\n💾 Settings saved!")
                print("🚀 Your changes will take effect the next time you start Task Planner.")
                break
            elif choice == "6":
                print("\n👋 Exiting without saving changes.")
                break
            else:
                print("❌ Invalid choice. Please try again.")
            
            print()
            
        except KeyboardInterrupt:
            print("\n\n👋 Configuration cancelled.")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
