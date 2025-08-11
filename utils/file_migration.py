"""
File Migration Utility for Task Planner
Moves configuration and data files from executable directory to AppData
"""

import os
import sys
import shutil
import json
from typing import List, Tuple


class FileMigration:
    """Handles migration of files from executable directory to AppData"""

    def __init__(self):
        self.app_name = "TaskPlanner"
        self.appdata_dir = self._get_appdata_directory()
        self.executable_dir = self._get_executable_directory()

    def _get_appdata_directory(self) -> str:
        """Get the AppData directory for the application"""
        if sys.platform == "win32":
            # Windows: %APPDATA%/TaskPlanner
            app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
            app_dir = os.path.join(app_data, self.app_name)
        elif sys.platform == "darwin":
            # macOS: ~/Library/Application Support/TaskPlanner
            app_dir = os.path.expanduser(f'~/Library/Application Support/{self.app_name}')
        else:
            # Linux: ~/.config/TaskPlanner
            config_dir = os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
            app_dir = os.path.join(config_dir, self.app_name)

        # Create directory if it doesn't exist
        os.makedirs(app_dir, exist_ok=True)
        return app_dir

    def _get_executable_directory(self) -> str:
        """Get the directory where the executable is located"""
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            return os.path.dirname(sys.executable)
        else:
            # Running as script - use project root
            return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def get_files_to_migrate(self) -> List[Tuple[str, str]]:
        """Get list of files that should be migrated to AppData"""
        files_to_migrate = []

        # Files that should be in AppData
        migration_files = [
            'settings.json',
            'window_settings.json',
            'license_database.json',
            'app_config.json',
            'user_preferences.json'
        ]

        for filename in migration_files:
            source_path = os.path.join(self.executable_dir, filename)
            dest_path = os.path.join(self.appdata_dir, filename)

            # Only migrate if source exists and destination doesn't
            if os.path.exists(source_path) and not os.path.exists(dest_path):
                files_to_migrate.append((source_path, dest_path))

        return files_to_migrate

    def migrate_files(self) -> bool:
        """Migrate files from executable directory to AppData"""
        try:
            files_to_migrate = self.get_files_to_migrate()

            if not files_to_migrate:
                print("No files need migration")
                return True

            print(f"Migrating {len(files_to_migrate)} files to AppData...")

            for source_path, dest_path in files_to_migrate:
                try:
                    # Copy file to AppData
                    shutil.copy2(source_path, dest_path)
                    print(f"  Migrated: {os.path.basename(source_path)}")

                    # Remove original file from executable directory
                    os.remove(source_path)
                    print(f"  Removed: {source_path}")

                except Exception as e:
                    print(f"  Error migrating {os.path.basename(source_path)}: {e}")
                    continue

            print("File migration completed successfully!")
            return True

        except Exception as e:
            print(f"Error during file migration: {e}")
            return False

    def cleanup_executable_directory(self) -> bool:
        """Remove any configuration files from executable directory"""
        try:
            cleanup_files = [
                'settings.json',
                'window_settings.json',
                'license_database.json',
                'app_config.json',
                'user_preferences.json',
                'debug.log',
                'error.log'
            ]

            removed_count = 0
            for filename in cleanup_files:
                file_path = os.path.join(self.executable_dir, filename)
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        print(f"  Cleaned up: {filename}")
                        removed_count += 1
                    except Exception as e:
                        print(f"  Could not remove {filename}: {e}")

            if removed_count > 0:
                print(f"Cleaned up {removed_count} files from executable directory")

            return True

        except Exception as e:
            print(f"Error during cleanup: {e}")
            return False

    def verify_appdata_structure(self) -> bool:
        """Verify that AppData directory structure is correct"""
        try:
            # Ensure AppData directory exists
            if not os.path.exists(self.appdata_dir):
                os.makedirs(self.appdata_dir, exist_ok=True)
                print(f"Created AppData directory: {self.appdata_dir}")

            # Check if directory is writable
            test_file = os.path.join(self.appdata_dir, 'test_write.tmp')
            try:
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                print("AppData directory is writable")
            except Exception as e:
                print(f"AppData directory is not writable: {e}")
                return False

            return True

        except Exception as e:
            print(f"Error verifying AppData structure: {e}")
            return False

    def get_appdata_path(self) -> str:
        """Get the AppData path for external use"""
        return self.appdata_dir

    def run_migration(self) -> bool:
        """Run complete migration process"""
        print("Starting file migration to AppData...")
        print(f"AppData directory: {self.appdata_dir}")
        print(f"Executable directory: {self.executable_dir}")

        # Step 1: Verify AppData structure
        if not self.verify_appdata_structure():
            print("Failed to verify AppData structure")
            return False

        # Step 2: Migrate files
        if not self.migrate_files():
            print("Failed to migrate files")
            return False

        # Step 3: Cleanup executable directory
        if not self.cleanup_executable_directory():
            print("Failed to cleanup executable directory")
            return False

        print("Migration completed successfully!")
        print(f"Configuration files are now stored in: {self.appdata_dir}")
        return True


def run_migration():
    """Convenience function to run migration"""
    migration = FileMigration()
    return migration.run_migration()


if __name__ == "__main__":
    # Run migration when script is executed directly
    success = run_migration()
    sys.exit(0 if success else 1)
