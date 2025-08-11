#!/usr/bin/env python3
"""
Task Planner Web Application - Production Version
Optimized for online deployment with proper security and configuration
"""

import os
import sys
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime, date, timedelta
from decimal import Decimal

# Add parent directory to path to access desktop models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Custom JSON encoder to handle datetime, timedelta, and other objects
class CustomJSONEncoder:
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, date):
            return obj.isoformat()
        elif isinstance(obj, timedelta):
            # Convert timedelta to string format (HH:MM:SS)
            total_seconds = int(obj.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        elif isinstance(obj, Decimal):
            return float(obj)
        return str(obj)

# Import desktop models (reuse existing database models)
try:
    from models.task import Task
    from models.category import Category
    from models.goal import Goal
    from database.db_manager import DatabaseManager
    MODELS_AVAILABLE = True
    print("✅ Desktop models imported successfully")
except ImportError as e:
    print(f"Warning: Desktop models not available: {e}")
    MODELS_AVAILABLE = False

# Production database configuration
class ProductionDatabaseManager:
    """Production database manager with environment variable support"""
    
    def __init__(self):
        self.db_type = os.environ.get('DB_TYPE', 'sqlite')
        self.connection = None
        
        if self.db_type == 'mysql':
            self.host = os.environ.get('DB_HOST', 'localhost')
            self.port = int(os.environ.get('DB_PORT', 3306))
            self.database = os.environ.get('DB_NAME', 'task_planner')
            self.username = os.environ.get('DB_USER', 'root')
            self.password = os.environ.get('DB_PASSWORD', '')
        else:
            self.db_path = os.environ.get('DB_PATH', 'task_planner.db')
    
    def connect(self):
        """Connect to database based on configuration"""
        try:
            if self.db_type == 'mysql':
                import mysql.connector
                self.connection = mysql.connector.connect(
                    host=self.host,
                    port=self.port,
                    database=self.database,
                    user=self.username,
                    password=self.password
                )
                return True
            else:
                self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
                self.connection.row_factory = sqlite3.Row
                self.connection.execute("PRAGMA foreign_keys = ON")
                return True
        except Exception as e:
            print(f"Database connection error: {e}")
            return False
    
    def convert_query(self, query):
        """Convert SQLite-style query to MySQL-style query if needed"""
        if self.db_type == 'mysql':
            # Replace ? placeholders with %s for MySQL
            mysql_query = query.replace('?', '%s')
            # Replace SQLite datetime functions with MySQL equivalents
            mysql_query = mysql_query.replace("datetime('now')", "NOW()")
            mysql_query = mysql_query.replace("CURRENT_TIMESTAMP", "NOW()")
            return mysql_query
        return query
    
    def execute_query(self, query, params=None):
        """Execute a query and return lastrowid for inserts"""
        if not self.connection:
            self.connect()
        try:
            converted_query = self.convert_query(query)
            if self.db_type == 'mysql':
                cursor = self.connection.cursor()
                cursor.execute(converted_query, params or ())
                self.connection.commit()
                return cursor.lastrowid if query.strip().upper().startswith('INSERT') else cursor.rowcount
            else:
                cursor = self.connection.cursor()
                cursor.execute(converted_query, params or ())
                self.connection.commit()
                return cursor.lastrowid if query.strip().upper().startswith('INSERT') else cursor.rowcount
        except Exception as e:
            print(f"Query execution error: {e}")
            return None
    
    def fetch_all(self, query, params=None):
        """Fetch all results from query"""
        if not self.connection:
            self.connect()
        try:
            converted_query = self.convert_query(query)
            if self.db_type == 'mysql':
                cursor = self.connection.cursor(dictionary=True)
                cursor.execute(converted_query, params or ())
                return cursor.fetchall()
            else:
                cursor = self.connection.cursor()
                cursor.execute(converted_query, params or ())
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Fetch all error: {e}")
            return []
    
    def fetch_one(self, query, params=None):
        """Fetch one result from query"""
        if not self.connection:
            self.connect()
        try:
            converted_query = self.convert_query(query)
            if self.db_type == 'mysql':
                cursor = self.connection.cursor(dictionary=True)
                cursor.execute(converted_query, params or ())
                return cursor.fetchone()
            else:
                cursor = self.connection.cursor()
                cursor.execute(converted_query, params or ())
                result = cursor.fetchone()
                return dict(result) if result else None
        except Exception as e:
            print(f"Fetch one error: {e}")
            return None
    
    def get_db_info(self):
        """Get database information"""
        if self.db_type == 'mysql':
            return {
                'type': 'MySQL',
                'location': f"{self.database}@{self.host}:{self.port}",
                'size': 'Unknown',
                'lastModified': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        else:
            return {
                'type': 'SQLite',
                'location': self.db_path,
                'size': 'Unknown',
                'lastModified': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

# Initialize Flask app with production settings
app = Flask(__name__)

# Production configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'production_secret_key_change_this')
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
app.config['ENV'] = os.environ.get('FLASK_ENV', 'production')

# Configure JSON encoder
app.json_encoder = CustomJSONEncoder

# Enable CORS for API access
CORS(app, origins=os.environ.get('ALLOWED_ORIGINS', '*').split(','))

# Initialize database
db_manager = ProductionDatabaseManager()
if db_manager.connect():
    print("✅ Database connection established")
else:
    print("❌ Database connection failed")
    db_manager = None

# Import routes from main app
try:
    from app import *
    print("✅ Routes imported successfully")
except Exception as e:
    print(f"❌ Error importing routes: {e}")

if __name__ == '__main__':
    # Production server configuration
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"🌐 Starting Task Planner Web Application (Production)")
    print(f"📍 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"🐛 Debug: {debug}")
    print(f"🗄️  Database: {db_manager.db_type if db_manager else 'None'}")
    
    app.run(host=host, port=port, debug=debug)
