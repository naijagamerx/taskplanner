#!/usr/bin/env python3
"""
Build script for Task Planner Admin Dashboard
Creates a standalone executable for license management
"""

import os
import sys
import shutil
import subprocess
import platform
import argparse
from pathlib import Path
from build_config import *

class AdminDashboardBuilder:
    """Builder for Task Planner Admin Dashboard"""
    
    def __init__(self):
        self.project_root = Path.cwd()
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
        for spec_file in self.project_root.glob("*Admin*.spec"):
            spec_file.unlink()
            print(f"   Removed: {spec_file}")
    
    def check_dependencies(self):
        """Check if all required dependencies are installed"""
        print("Checking dependencies...")
        
        required_packages = [
            "PyInstaller",
            "customtkinter",
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                if package == "PyInstaller":
                    import PyInstaller
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
    
    def build_pyinstaller_command(self):
        """Build PyInstaller command for admin dashboard"""
        print(f"Building Admin Dashboard for {platform.system()}...")
        
        cmd = ["py", "-m", "PyInstaller"]
        
        # Basic options
        cmd.extend([
            "--name", "TaskPlanner-Admin",
            "--onefile",
            "--windowed",
            "--clean",
            "--noconfirm",
            "--distpath", str(self.dist_dir),
            "--workpath", str(self.build_dir),
            "--specpath", "."
        ])
        
        # Add icon if available
        if IS_WINDOWS and Path(WINDOWS_ICON).exists():
            cmd.extend(["--icon", WINDOWS_ICON])
        
        # Add version file if available
        if IS_WINDOWS and Path("version_info.txt").exists():
            cmd.extend(["--version-file", "version_info.txt"])
        
        # Hidden imports for admin dashboard
        hidden_imports = [
            "customtkinter",
            "tkinter",
            "tkinter.ttk",
            "json",
            "hashlib",
            "datetime",
            "os",
            "sys",
        ]
        
        for import_name in hidden_imports:
            cmd.extend(["--hidden-import", import_name])
        
        # Exclude unnecessary modules
        exclude_modules = [
            "tkinter.test",
            "test",
            "unittest",
            "matplotlib",
            "PIL",
            "mysql.connector",
        ]
        
        for module in exclude_modules:
            cmd.extend(["--exclude-module", module])
        
        # Add the main script
        cmd.append("admin_dashboard.py")
        
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
            exe_name = "TaskPlanner-Admin.exe"
        elif IS_MACOS:
            exe_name = "TaskPlanner-Admin.app"
        else:
            exe_name = "TaskPlanner-Admin"
        
        original_path = self.dist_dir / exe_name
        
        if original_path.exists():
            # Rename to include version and platform
            platform_name = get_platform_name()
            new_name = f"TaskPlanner-Admin-v{APP_VERSION}-{platform_name}"
            if IS_WINDOWS:
                new_name += ".exe"
            elif IS_MACOS:
                new_name += ".app"
            
            new_path = self.dist_dir / new_name
            
            if original_path != new_path:
                try:
                    if new_path.exists():
                        new_path.unlink()
                    original_path.rename(new_path)
                    print(f"   Renamed: {exe_name} -> {new_name}")
                except Exception as e:
                    print(f"   Warning: Could not rename file: {e}")
                    new_path = original_path
            else:
                new_path = original_path
            
            # Get file size
            file_size = new_path.stat().st_size / (1024 * 1024)  # MB
            print(f"   Size: {file_size:.1f} MB")
            
            return new_path
        else:
            print(f"Executable not found: {original_path}")
            return None
    
    def create_installer_info(self, exe_path):
        """Create installation instructions for admin dashboard"""
        print("Creating installation instructions...")
        
        readme_content = f"""# Task Planner Admin Dashboard v{APP_VERSION}

## Installation Instructions

### For {platform.system()} Users:

1. **Download**: Download the executable file: `{exe_path.name}`

2. **Install**:
   - **Windows**: Double-click the .exe file to run
   - **macOS**: Drag the .app to your Applications folder
   - **Linux**: Make executable and run: `chmod +x {exe_path.name} && ./{exe_path.name}`

## Features:
- Generate license keys for specific hardware IDs
- Manage existing licenses (view, revoke, delete)
- Copy license keys to clipboard
- Export license database
- Professional admin interface

## Usage:
1. **Generate License**: Enter hardware ID and user details, then click "Generate License Key"
2. **Copy License**: Double-click any license in the list to copy its key
3. **Manage Licenses**: Right-click licenses for additional options
4. **Export Data**: Use "Export List" to save license information

## System Requirements:
- **Windows**: Windows 10 or later
- **macOS**: macOS 10.14 or later
- **Linux**: Ubuntu 18.04+ or equivalent
- **Memory**: 2GB RAM minimum
- **Storage**: 50MB free space

## Support:
For issues or questions, please contact the development team.

---
Built with Python and CustomTkinter
"""
        
        readme_path = self.dist_dir / "README-Admin.txt"
        readme_path.write_text(readme_content)
        print(f"   Created: {readme_path}")
    
    def build(self, clean=True):
        """Main build process for admin dashboard"""
        print(f"Building Task Planner Admin Dashboard v{APP_VERSION} for {platform.system()}")
        print("=" * 70)
        
        # Step 1: Clean previous builds
        if clean:
            self.clean_build_dirs()
        
        # Step 2: Check dependencies
        if not self.check_dependencies():
            return False
        
        # Step 3: Run PyInstaller
        if not self.run_pyinstaller():
            return False
        
        # Step 4: Post-build cleanup
        exe_path = self.post_build_cleanup()
        if not exe_path:
            return False
        
        # Step 5: Create installation instructions
        self.create_installer_info(exe_path)
        
        print("\n" + "=" * 70)
        print("ADMIN DASHBOARD BUILD COMPLETED SUCCESSFULLY!")
        print(f"Executable: {exe_path}")
        print(f"Distribution folder: {self.dist_dir}")
        print("=" * 70)
        
        return True

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Build Task Planner Admin Dashboard executable")
    parser.add_argument("--no-clean", action="store_true", help="Don't clean build directories")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    builder = AdminDashboardBuilder()
    success = builder.build(clean=not args.no_clean)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
