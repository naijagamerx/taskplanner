#!/usr/bin/env python3
"""
Cross-platform build script for Task Planner application
Generates executable files for Windows, macOS, and Linux
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path
import argparse

# Import build configuration
from build_config import *

class TaskPlannerBuilder:
    """Main builder class for Task Planner application"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.build_dir = self.project_root / BUILD_DIR
        self.dist_dir = self.project_root / DIST_DIR

    def clean_build_dirs(self):
        """Clean previous build directories"""
        print("Cleaning previous build directories...")

        for dir_path in [self.build_dir, self.dist_dir]:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"   Removed: {dir_path}")

        # Remove spec files
        for spec_file in self.project_root.glob("*.spec"):
            spec_file.unlink()
            print(f"   Removed: {spec_file}")

    def check_dependencies(self):
        """Check if all required dependencies are installed"""
        print("Checking dependencies...")

        required_packages = [
            "PyInstaller",
            "mysql-connector-python",
            "customtkinter",
            "tkcalendar",
            "matplotlib",
            "Pillow"
        ]

        missing_packages = []

        for package in required_packages:
            try:
                if package == "PyInstaller":
                    import PyInstaller
                elif package == "mysql-connector-python":
                    import mysql.connector
                elif package == "Pillow":
                    import PIL
                else:
                    __import__(package.replace("-", "_").lower())
                print(f"   OK {package}")
            except ImportError:
                missing_packages.append(package)
                print(f"   MISSING {package}")

        if missing_packages:
            print(f"\nMissing packages: {', '.join(missing_packages)}")
            print("Install them with: pip install -r requirements.txt")
            return False

        print("All dependencies are installed!")
        return True

    def create_icons(self):
        """Create application icons if they don't exist"""
        print("Checking application icons...")

        icons_dir = self.project_root / ICONS_DIR
        icons_dir.mkdir(parents=True, exist_ok=True)

        # Check for required icon files
        required_icons = {
            "Windows": WINDOWS_ICON,
            "macOS": MACOS_ICON,
            "Linux": LINUX_ICON
        }

        missing_icons = []
        for platform_name, icon_path in required_icons.items():
            if not Path(icon_path).exists():
                missing_icons.append(f"{platform_name}: {icon_path}")
            else:
                print(f"   OK {platform_name} icon found")

        if missing_icons:
            print("Missing icon files:")
            for icon in missing_icons:
                print(f"   MISSING {icon}")
            print("\nNote: Icons are optional but recommended for professional appearance")

        return True

    def build_pyinstaller_command(self):
        """Build PyInstaller command based on platform"""
        print(f"Building for {platform.system()}...")

        cmd = ["py", "-m", "PyInstaller"]

        # Add basic options
        for key, value in PYINSTALLER_CONFIG.items():
            if key == "script":
                continue  # Handle script separately
            elif key == "add_data":
                for data_pair in value:
                    cmd.extend(["--add-data", data_pair])
            elif key == "hidden_imports":
                for import_name in value:
                    cmd.extend(["--hidden-import", import_name])
            elif key == "exclude_modules":
                for module in value:
                    cmd.extend(["--exclude-module", module])
            elif isinstance(value, bool):
                if value:
                    cmd.append(f"--{key.replace('_', '-')}")
            else:
                cmd.extend([f"--{key.replace('_', '-')}", str(value)])

        # Add the main script
        cmd.append(PYINSTALLER_CONFIG["script"])

        return cmd

    def run_pyinstaller(self):
        """Run PyInstaller to create executable"""
        print("Running PyInstaller...")

        cmd = self.build_pyinstaller_command()
        print(f"Command: {' '.join(cmd)}")

        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("PyInstaller completed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"PyInstaller failed with error code {e.returncode}")
            print(f"Error output: {e.stderr}")
            return False

    def post_build_cleanup(self):
        """Perform post-build cleanup and organization"""
        print("Post-build cleanup...")

        # Find the generated executable
        if IS_WINDOWS:
            exe_name = f"{APP_NAME}.exe"
        elif IS_MACOS:
            exe_name = f"{APP_NAME}.app"
        else:
            exe_name = APP_NAME

        original_path = self.dist_dir / exe_name

        if original_path.exists():
            # Rename to include version and platform
            new_name = get_output_filename()
            new_path = self.dist_dir / new_name

            if original_path != new_path:
                original_path.rename(new_path)
                print(f"   Renamed: {exe_name} -> {new_name}")

            # Get file size
            file_size = new_path.stat().st_size / (1024 * 1024)  # MB
            print(f"   Size: {file_size:.1f} MB")

            return new_path
        else:
            print(f"Executable not found: {original_path}")
            return None

    def create_installer_info(self, exe_path):
        """Create installation instructions"""
        print("Creating installation instructions...")

        readme_content = f"""# Task Planner v{APP_VERSION}

## Installation Instructions

### For {platform.system()} Users:

1. **Download**: Download the executable file: `{exe_path.name}`

2. **Install**:
   - **Windows**: Double-click the .exe file to run
   - **macOS**: Drag the .app to your Applications folder
   - **Linux**: Make executable and run: `chmod +x {exe_path.name} && ./{exe_path.name}`

3. **Database Setup**:
   - Install MySQL Server on your computer
   - Create a database named 'task_planner'
   - Update database connection settings in the app

## Features:
- Task Management with Categories and Priorities
- Calendar Integration
- Analytics and Reports
- Advanced Search and Filtering
- MySQL Database Storage
- Modern UI with Dark/Light Themes

## System Requirements:
- **Windows**: Windows 10 or later
- **macOS**: macOS 10.14 or later
- **Linux**: Ubuntu 18.04+ or equivalent
- **Database**: MySQL 5.7+ or MariaDB 10.3+
- **Memory**: 4GB RAM minimum
- **Storage**: 100MB free space

## Support:
For issues or questions, please contact the development team.

---
Built with Python and CustomTkinter
"""

        readme_path = self.dist_dir / "README.txt"
        readme_path.write_text(readme_content)
        print(f"   Created: {readme_path}")

    def build(self, clean=True):
        """Main build process"""
        print(f"Building Task Planner v{APP_VERSION} for {platform.system()}")
        print("=" * 60)

        # Step 1: Clean previous builds
        if clean:
            self.clean_build_dirs()

        # Step 2: Check dependencies
        if not self.check_dependencies():
            return False

        # Step 3: Check icons
        self.create_icons()

        # Step 4: Run PyInstaller
        if not self.run_pyinstaller():
            return False

        # Step 5: Post-build cleanup
        exe_path = self.post_build_cleanup()
        if not exe_path:
            return False

        # Step 6: Create installation instructions
        self.create_installer_info(exe_path)

        print("\n" + "=" * 60)
        print("BUILD COMPLETED SUCCESSFULLY!")
        print(f"Executable: {exe_path}")
        print(f"Distribution folder: {self.dist_dir}")
        print("=" * 60)

        return True

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Build Task Planner executable")
    parser.add_argument("--no-clean", action="store_true", help="Don't clean build directories")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()

    # Update config for debug mode
    if args.debug:
        PYINSTALLER_CONFIG["console"] = True
        OPTIMIZATION_CONFIG["debug"] = True

    builder = TaskPlannerBuilder()
    success = builder.build(clean=not args.no_clean)

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
