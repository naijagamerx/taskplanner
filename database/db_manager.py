"""
Enhanced Database manager for Task Planner application
Handles MySQL and SQLite database connections and operations
"""

import mysql.connector
from mysql.connector import Error as MySQLError
import sqlite3
import logging
from typing import Optional, List, Dict, Any, Tuple, Union
from contextlib import contextmanager
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.database_config import DatabaseConfig

class DatabaseManager:
    """Enhanced database manager supporting MySQL and SQLite"""

    def __init__(self):
        self.config = DatabaseConfig()
        self.connection = None
        self.db_type = self.config.get_database_type()
        self.setup_logging()

    def setup_logging(self):
        """Setup logging for database operations"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def connect(self) -> bool:
        """Establish database connection based on configuration"""
        try:
            if self.config.is_mysql():
                return self._connect_mysql()
            elif self.config.is_sqlite():
                return self._connect_sqlite()
            else:
                self.logger.error("Unknown database type")
                return False
        except Exception as e:
            self.logger.error(f"Error connecting to database: {e}")
            return False

    def _connect_mysql(self) -> bool:
        """Connect to MySQL database"""
        try:
            db_config = self.config.get_config()
            # Remove type field for mysql.connector
            mysql_config = {k: v for k, v in db_config.items() if k != 'type'}

            # First connect without database to create it if needed
            temp_config = mysql_config.copy()
            database_name = temp_config.pop('database')

            self.connection = mysql.connector.connect(**temp_config)

            if self.connection.is_connected():
                cursor = self.connection.cursor()
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                cursor.close()
                self.connection.close()

                # Now connect to the specific database
                self.connection = mysql.connector.connect(**mysql_config)
                self.logger.info("Successfully connected to MySQL database")
                return True

        except MySQLError as e:
            self.logger.error(f"Error connecting to MySQL: {e}")
            return False

    def _connect_sqlite(self) -> bool:
        """Connect to SQLite database"""
        try:
            db_path = self.config.get_config()['database']

            # Ensure directory exists
            os.makedirs(os.path.dirname(db_path), exist_ok=True)

            # Check if database exists and has tables
            db_exists = os.path.exists(db_path)
            needs_initialization = False

            if db_exists:
                # Check if database has tables
                temp_conn = sqlite3.connect(db_path)
                cursor = temp_conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                temp_conn.close()
                needs_initialization = len(tables) == 0
            else:
                needs_initialization = True

            # Use check_same_thread=False to allow multi-threading
            self.connection = sqlite3.connect(db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row  # Enable dict-like access

            # Enable foreign key constraints
            self.connection.execute("PRAGMA foreign_keys = ON")

            # Initialize database if needed
            if needs_initialization:
                self.logger.info("Database needs initialization, creating schema...")
                self.initialize_database()

            self.logger.info(f"Successfully connected to SQLite database: {db_path}")
            return True

        except sqlite3.Error as e:
            self.logger.error(f"Error connecting to SQLite: {e}")
            return False

    def disconnect(self):
        """Close database connection"""
        if self.connection:
            if self.config.is_mysql() and self.connection.is_connected():
                self.connection.close()
                self.logger.info("MySQL connection closed")
            elif self.config.is_sqlite():
                self.connection.close()
                self.logger.info("SQLite connection closed")

    def _is_connected(self) -> bool:
        """Check if database is connected"""
        if not self.connection:
            return False

        if self.config.is_mysql():
            return self.connection.is_connected()
        elif self.config.is_sqlite():
            try:
                self.connection.execute("SELECT 1")
                return True
            except:
                return False
        return False

    @contextmanager
    def get_cursor(self):
        """Context manager for database cursor"""
        cursor = None
        try:
            if not self._is_connected():
                self.connect()

            if self.config.is_mysql():
                cursor = self.connection.cursor(dictionary=True)
            elif self.config.is_sqlite():
                cursor = self.connection.cursor()

            yield cursor

        except (MySQLError, sqlite3.Error) as e:
            self.logger.error(f"Database error: {e}")
            if self.connection:
                self.connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()

    def execute_script_file(self, script_path: str) -> bool:
        """Execute SQL script file"""
        try:
            with open(script_path, 'r', encoding='utf-8') as file:
                script = file.read()

            # Split script into individual statements
            statements = [stmt.strip() for stmt in script.split(';') if stmt.strip()]

            with self.get_cursor() as cursor:
                for statement in statements:
                    if statement:
                        # For SQLite, use executescript for better handling of special characters
                        if self.config.is_sqlite():
                            # Execute each statement individually to handle %% properly
                            cursor.execute(statement)
                        else:
                            cursor.execute(statement)
                self.connection.commit()

            self.logger.info(f"Successfully executed script: {script_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error executing script {script_path}: {e}")
            return False

    def initialize_database(self) -> bool:
        """Initialize database with appropriate schema"""
        if self.config.is_sqlite():
            schema_path = os.path.join(os.path.dirname(__file__), 'schema_sqlite.sql')
        else:
            schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')

        return self.execute_script_file(schema_path)

    def execute_query(self, query: str, params: Optional[Tuple] = None) -> Optional[int]:
        """Execute INSERT/UPDATE/DELETE query and return last insert ID or affected rows"""
        try:
            # Convert MySQL-style placeholders to SQLite-style for SQLite
            if self.config.is_sqlite() and '%s' in query:
                query = query.replace('%s', '?')

            with self.get_cursor() as cursor:
                cursor.execute(query, params or ())
                self.connection.commit()

                # Return lastrowid for INSERT operations, rowcount for others
                if query.strip().upper().startswith('INSERT'):
                    return cursor.lastrowid
                else:
                    return cursor.rowcount

        except (MySQLError, sqlite3.Error) as e:
            self.logger.error(f"Error executing query: {e}")
            return None

    def fetch_all(self, query: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
        """Execute SELECT query and return all results"""
        try:
            # Convert MySQL-style placeholders to SQLite-style for SQLite
            if self.config.is_sqlite() and '%s' in query:
                query = query.replace('%s', '?')

            with self.get_cursor() as cursor:
                cursor.execute(query, params or ())

                if self.config.is_mysql():
                    return cursor.fetchall()
                elif self.config.is_sqlite():
                    # Convert sqlite3.Row to dict
                    return [dict(row) for row in cursor.fetchall()]

        except (MySQLError, sqlite3.Error) as e:
            self.logger.error(f"Error executing query: {e}")
            return []

    def fetch_one(self, query: str, params: Optional[Tuple] = None) -> Optional[Dict[str, Any]]:
        """Execute SELECT query and return one result"""
        try:
            # Convert MySQL-style placeholders to SQLite-style for SQLite
            if self.config.is_sqlite() and '%s' in query:
                query = query.replace('%s', '?')

            with self.get_cursor() as cursor:
                cursor.execute(query, params or ())

                if self.config.is_mysql():
                    result = cursor.fetchone()
                    return result
                elif self.config.is_sqlite():
                    # Convert sqlite3.Row to dict
                    result = cursor.fetchone()
                    return dict(result) if result else None

        except (MySQLError, sqlite3.Error) as e:
            self.logger.error(f"Error executing query: {e}")
            return None

    def execute_update(self, query: str, params: Optional[Tuple] = None) -> int:
        """Execute INSERT/UPDATE/DELETE query and return affected rows"""
        try:
            # Convert MySQL-style placeholders to SQLite-style for SQLite
            if self.config.is_sqlite() and '%s' in query:
                query = query.replace('%s', '?')

            with self.get_cursor() as cursor:
                cursor.execute(query, params or ())
                self.connection.commit()
                return cursor.rowcount
        except (MySQLError, sqlite3.Error) as e:
            self.logger.error(f"Error executing update: {e}")
            return 0

    def execute_insert(self, query: str, params: Optional[Tuple] = None) -> Optional[int]:
        """Execute INSERT query and return last insert ID"""
        try:
            # Convert MySQL-style placeholders to SQLite-style for SQLite
            if self.config.is_sqlite() and '%s' in query:
                query = query.replace('%s', '?')

            with self.get_cursor() as cursor:
                cursor.execute(query, params or ())
                self.connection.commit()
                return cursor.lastrowid
        except (MySQLError, sqlite3.Error) as e:
            self.logger.error(f"Error executing insert: {e}")
            return None

    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            print("Testing database connection via db_manager...")

            if self.connect():
                with self.get_cursor() as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    success = result is not None

                    if success:
                        print("Database connection test successful")
                    else:
                        print("Database connection test failed - no result")

                    return success
            else:
                print("Database connection failed - could not connect")
                return False

        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            print(f"Database connection test error: {e}")
            return False

    def update_configuration(self, new_config: Dict[str, Any]) -> bool:
        """Update database configuration"""
        try:
            # Close current connection
            self.disconnect()

            # Save new configuration
            if self.config.save_config(new_config):
                # Reload configuration
                self.config = DatabaseConfig()
                self.db_type = self.config.get_database_type()

                # Test new connection
                if self.test_connection():
                    self.logger.info("Database configuration updated successfully")
                    return True
                else:
                    self.logger.error("New database configuration failed connection test")
                    return False
            else:
                self.logger.error("Failed to save new database configuration")
                return False

        except Exception as e:
            self.logger.error(f"Error updating database configuration: {e}")
            return False

    def get_connection_info(self) -> Dict[str, Any]:
        """Get current connection information for display"""
        config = self.config.get_config()

        if self.config.is_mysql():
            return {
                'type': 'MySQL',
                'host': config.get('host', 'N/A'),
                'port': config.get('port', 'N/A'),
                'database': config.get('database', 'N/A'),
                'user': config.get('user', 'N/A'),
                'connection_string': self.config.get_connection_string()
            }
        elif self.config.is_sqlite():
            return {
                'type': 'SQLite',
                'database': config.get('database', 'N/A'),
                'connection_string': self.config.get_connection_string()
            }
        else:
            return {
                'type': 'Unknown',
                'connection_string': 'Not configured'
            }

# Global database manager instance
db_manager = DatabaseManager()
