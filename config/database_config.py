"""
Enhanced Database configuration for Task Planner application
Supports MySQL, SQLite, and custom configurations
"""

import os
import sys
import json
from typing import Dict, Any, Optional

# Default MySQL configuration
DEFAULT_MYSQL_CONFIG = {
    'type': 'mysql',
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '',
    'database': 'task_planner',
    'charset': 'utf8mb4',
    'autocommit': True
}

# Default SQLite configuration
def get_default_sqlite_path():
    """Get default SQLite database path relative to the application"""
    # Get the directory where the script is located
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        app_dir = os.path.dirname(sys.executable)
    else:
        # Running as script
        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    return os.path.join(app_dir, 'data', 'task_planner.db')

DEFAULT_SQLITE_CONFIG = {
    'type': 'sqlite',
    'database': get_default_sqlite_path()
}

class DatabaseConfig:
    """Enhanced database configuration manager"""

    def __init__(self):
        self.config_file = os.path.join(os.path.dirname(__file__), 'db_config.json')
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """Load database configuration from file, environment, or defaults"""
        # Try to load from config file first
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Validate and return
                    if self.validate_config(config):
                        return config
            except Exception as e:
                print(f"Error loading config file: {e}")

        # Try environment variables
        env_config = self.load_from_env()
        if env_config:
            return env_config

        # Return default SQLite config for distribution (no server required)
        return DEFAULT_SQLITE_CONFIG.copy()

    def load_from_env(self) -> Optional[Dict[str, Any]]:
        """Load database configuration from environment variables"""
        # Check for SQLite first
        sqlite_path = os.getenv('DB_SQLITE_PATH')
        if sqlite_path:
            return {
                'type': 'sqlite',
                'database': sqlite_path
            }

        # Check for MySQL environment variables
        env_mapping = {
            'DB_HOST': 'host',
            'DB_PORT': 'port',
            'DB_USER': 'user',
            'DB_PASSWORD': 'password',
            'DB_NAME': 'database'
        }

        config = DEFAULT_MYSQL_CONFIG.copy()
        has_env_vars = False

        for env_var, config_key in env_mapping.items():
            value = os.getenv(env_var)
            if value:
                has_env_vars = True
                if config_key == 'port':
                    config[config_key] = int(value)
                else:
                    config[config_key] = value

        return config if has_env_vars else None

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate database configuration"""
        if not isinstance(config, dict):
            return False

        db_type = config.get('type', 'mysql')

        if db_type == 'mysql':
            required_fields = ['host', 'port', 'user', 'database']
            return all(field in config for field in required_fields)
        elif db_type == 'sqlite':
            return 'database' in config

        return False

    def save_config(self, config: Dict[str, Any]) -> bool:
        """Save database configuration to file"""
        try:
            if not self.validate_config(config):
                raise ValueError("Invalid configuration")

            # Ensure config directory exists
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)

            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)

            self.config = config
            return True

        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def get_config(self) -> Dict[str, Any]:
        """Get database configuration"""
        return self.config.copy()

    def get_database_type(self) -> str:
        """Get database type (mysql or sqlite)"""
        return self.config.get('type', 'mysql')

    def is_mysql(self) -> bool:
        """Check if using MySQL"""
        return self.get_database_type() == 'mysql'

    def is_sqlite(self) -> bool:
        """Check if using SQLite"""
        return self.get_database_type() == 'sqlite'

    def get_connection_string(self) -> str:
        """Get connection string for display"""
        if self.is_mysql():
            return f"mysql://{self.config.get('user')}@{self.config.get('host')}:{self.config.get('port')}/{self.config.get('database')}"
        elif self.is_sqlite():
            return f"sqlite:///{self.config.get('database')}"
        return "Unknown"

    def test_config(self, test_config: Dict[str, Any]) -> bool:
        """Test a configuration without saving it"""
        try:
            if not self.validate_config(test_config):
                return False

            # Import here to avoid circular imports
            import mysql.connector
            import sqlite3

            if test_config.get('type') == 'mysql':
                # Test MySQL connection
                temp_config = {k: v for k, v in test_config.items() if k != 'type'}
                connection = mysql.connector.connect(**temp_config)
                if connection.is_connected():
                    connection.close()
                    return True
                return False

            elif test_config.get('type') == 'sqlite':
                # Test SQLite connection
                db_path = test_config.get('database')
                # Ensure directory exists
                os.makedirs(os.path.dirname(db_path), exist_ok=True)
                connection = sqlite3.connect(db_path)
                connection.close()
                return True

        except Exception as e:
            print(f"Configuration test failed: {e}")
            return False

        return False

    def reset_to_defaults(self, db_type: str = 'sqlite'):
        """Reset configuration to defaults"""
        if db_type == 'sqlite':
            self.config = DEFAULT_SQLITE_CONFIG.copy()
        else:
            self.config = DEFAULT_MYSQL_CONFIG.copy()

        # Remove config file
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
