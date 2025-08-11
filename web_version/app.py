#!/usr/bin/env python3
"""
Task Planner Web Application
Flask-based web version of the desktop Task Planner
"""

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import sys
import os
import sqlite3
from datetime import datetime, date, timedelta
import json

# Add parent directory to path to access desktop models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

# Simple web database manager
class WebDatabaseManager:
    """Simple database manager for web version using local SQLite"""

    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), 'task_planner.db')
        self.db_path = db_path
        self.connection = None

    def connect(self):
        """Connect to SQLite database"""
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            self.connection.execute("PRAGMA foreign_keys = ON")
            return True
        except Exception as e:
            print(f"Database connection error: {e}")
            return False

    def execute_query(self, query, params=None):
        """Execute a query and return lastrowid for inserts"""
        if not self.connection:
            self.connect()
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
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
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Fetch all error: {e}")
            return []

    def fetch_one(self, query, params=None):
        """Fetch one result from query"""
        if not self.connection:
            self.connect()
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            result = cursor.fetchone()
            return dict(result) if result else None
        except Exception as e:
            print(f"Fetch one error: {e}")
            return None

    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None

    def get_db_info(self):
        """Get database information"""
        return {
            'type': 'SQLite',
            'location': self.db_path,
            'size': self._get_file_size(),
            'lastModified': self._get_last_modified()
        }

    def _get_file_size(self):
        """Get database file size"""
        try:
            if os.path.exists(self.db_path):
                size_bytes = os.path.getsize(self.db_path)
                size_mb = round(size_bytes / (1024 * 1024), 2)
                return f"{size_mb} MB"
            return "Unknown"
        except:
            return "Unknown"

    def _get_last_modified(self):
        """Get last modified time"""
        try:
            if os.path.exists(self.db_path):
                timestamp = os.path.getmtime(self.db_path)
                return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            return "Unknown"
        except:
            return "Unknown"


class MySQLDatabaseManager:
    """MySQL database manager for web version"""

    def __init__(self, host, port, database, username, password):
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.connection = None
        self.db_type = 'mysql'

    def connect(self):
        """Connect to MySQL database"""
        try:
            import mysql.connector
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.username,
                password=self.password
            )
            return True
        except Exception as e:
            print(f"MySQL connection error: {e}")
            return False

    def execute_query(self, query, params=None):
        """Execute a query and return lastrowid for inserts"""
        if not self.connection or not self.connection.is_connected():
            self.connect()
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            self.connection.commit()
            return cursor.lastrowid if query.strip().upper().startswith('INSERT') else cursor.rowcount
        except Exception as e:
            print(f"MySQL query execution error: {e}")
            return None

    def fetch_all(self, query, params=None):
        """Fetch all results from query"""
        if not self.connection or not self.connection.is_connected():
            self.connect()
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            return cursor.fetchall()
        except Exception as e:
            print(f"MySQL fetch all error: {e}")
            return []

    def fetch_one(self, query, params=None):
        """Fetch one result from query"""
        if not self.connection or not self.connection.is_connected():
            self.connect()
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            return cursor.fetchone()
        except Exception as e:
            print(f"MySQL fetch one error: {e}")
            return None

    def close(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            self.connection = None

    def get_db_info(self):
        """Get database information"""
        return {
            'type': 'MySQL',
            'location': f"{self.database}@{self.host}:{self.port}",
            'size': self._get_database_size(),
            'lastModified': self._get_last_modified()
        }

    def _get_database_size(self):
        """Get MySQL database size"""
        try:
            query = """
                SELECT ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS size_mb
                FROM information_schema.tables
                WHERE table_schema = %s
            """
            result = self.fetch_one(query, (self.database,))
            if result and result['size_mb']:
                return f"{result['size_mb']} MB"
            return "Unknown"
        except:
            return "Unknown"

    def _get_last_modified(self):
        """Get last modified time"""
        try:
            query = """
                SELECT MAX(UPDATE_TIME) as last_modified
                FROM information_schema.tables
                WHERE table_schema = %s
            """
            result = self.fetch_one(query, (self.database,))
            if result and result['last_modified']:
                return result['last_modified'].strftime('%Y-%m-%d %H:%M:%S')
            return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        except:
            return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def initialize_tables(self):
        """Initialize MySQL tables"""
        try:
            # Convert SQLite schema to MySQL
            tables = [
                """
                CREATE TABLE IF NOT EXISTS categories (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL UNIQUE,
                    description TEXT,
                    color VARCHAR(7) DEFAULT '#007bff',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS priority_levels (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(50) NOT NULL UNIQUE,
                    level INT NOT NULL UNIQUE,
                    color VARCHAR(7) DEFAULT '#6c757d',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT DEFAULT 1,
                    category_id INT,
                    priority_id INT DEFAULT 2,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    due_date DATE,
                    due_time TIME,
                    estimated_duration INT,
                    actual_duration INT,
                    status VARCHAR(20) DEFAULT 'pending',
                    is_recurring BOOLEAN DEFAULT 0,
                    recurrence_pattern VARCHAR(20),
                    recurrence_interval INT,
                    recurrence_end_date DATE,
                    parent_task_id INT,
                    reminder_time INT DEFAULT 15,
                    completed_at TIMESTAMP NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
                    FOREIGN KEY (priority_id) REFERENCES priority_levels(id) ON DELETE SET NULL,
                    FOREIGN KEY (parent_task_id) REFERENCES tasks(id) ON DELETE CASCADE
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS user_settings (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT DEFAULT 1,
                    setting_key TEXT NOT NULL,
                    setting_value TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    UNIQUE KEY unique_user_setting (user_id, setting_key(255))
                )
                """
            ]

            for table_sql in tables:
                self.execute_query(table_sql)

            # Insert default data if tables are empty
            self._insert_default_data()

        except Exception as e:
            print(f"Error initializing MySQL tables: {e}")
            raise

    def _insert_default_data(self):
        """Insert default priorities and categories if they don't exist"""
        try:
            # Check if priorities exist
            priorities_count = self.fetch_one("SELECT COUNT(*) as count FROM priority_levels")
            if priorities_count['count'] == 0:
                priorities = [
                    ('Low', 1, '#28a745'),
                    ('Medium', 2, '#ffc107'),
                    ('High', 3, '#fd7e14'),
                    ('Critical', 4, '#dc3545')
                ]
                for name, level, color in priorities:
                    self.execute_query(
                        "INSERT INTO priority_levels (name, level, color) VALUES (%s, %s, %s)",
                        (name, level, color)
                    )

            # Check if categories exist
            categories_count = self.fetch_one("SELECT COUNT(*) as count FROM categories")
            if categories_count['count'] == 0:
                categories = [
                    ('Work', 'Work-related tasks', '#007bff'),
                    ('Personal', 'Personal tasks', '#28a745'),
                    ('Shopping', 'Shopping and errands', '#ffc107'),
                    ('Health', 'Health and fitness', '#dc3545')
                ]
                for name, description, color in categories:
                    self.execute_query(
                        "INSERT INTO categories (name, description, color) VALUES (%s, %s, %s)",
                        (name, description, color)
                    )
        except Exception as e:
            print(f"Error inserting default data: {e}")


# Initialize database with fallback options
def initialize_database():
    """Initialize database connection with multiple fallback options"""
    global db_manager

    try:
        # Try local web version database first
        web_db_path = os.path.join(os.path.dirname(__file__), 'task_planner.db')
        if os.path.exists(web_db_path):
            print(f"✅ Found web database: {web_db_path}")
            db_manager = WebDatabaseManager(web_db_path)
            if db_manager.connect():
                print("✅ Connected to web database successfully")
                return True

        # Try to use existing desktop database
        desktop_db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'task_planner.db')
        if os.path.exists(desktop_db_path):
            print(f"✅ Found desktop database: {desktop_db_path}")
            db_manager = WebDatabaseManager(desktop_db_path)
            if db_manager.connect():
                print("✅ Connected to desktop database successfully")
                return True

        # Create new database for web version
        print("📝 Creating new database for web version...")
        db_manager = WebDatabaseManager()
        if db_manager.connect():
            create_sample_data()
            return True

        return False

    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def create_sample_data():
    """Create sample categories and priorities for new database"""
    try:
        # Create all necessary tables first
        print("📋 Creating database tables...")

        # Create categories table
        db_manager.execute_query("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL UNIQUE,
                description TEXT,
                color VARCHAR(7) DEFAULT '#007bff',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create priority_levels table
        db_manager.execute_query("""
            CREATE TABLE IF NOT EXISTS priority_levels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(50) NOT NULL UNIQUE,
                level INTEGER NOT NULL UNIQUE,
                color VARCHAR(7) DEFAULT '#6c757d',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create tasks table
        db_manager.execute_query("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT 1,
                category_id INTEGER,
                priority_id INTEGER DEFAULT 2,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                due_date DATE,
                due_time TIME,
                estimated_duration INTEGER,
                actual_duration INTEGER,
                status VARCHAR(20) DEFAULT 'pending',
                is_recurring BOOLEAN DEFAULT 0,
                recurrence_pattern VARCHAR(20),
                recurrence_interval INTEGER,
                recurrence_end_date DATE,
                parent_task_id INTEGER,
                reminder_time INTEGER DEFAULT 15,
                completed_at TIMESTAMP NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
                FOREIGN KEY (priority_id) REFERENCES priority_levels(id) ON DELETE SET NULL,
                FOREIGN KEY (parent_task_id) REFERENCES tasks(id) ON DELETE CASCADE
            )
        """)

        # Create user_settings table
        db_manager.execute_query("""
            CREATE TABLE IF NOT EXISTS user_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT 1,
                setting_key TEXT NOT NULL,
                setting_value TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, setting_key)
            )
        """)
        print("✅ Database tables created")

        # Create default priority levels
        priorities = [
            {'name': 'Low', 'level': 1, 'color': '#28a745'},
            {'name': 'Medium', 'level': 2, 'color': '#ffc107'},
            {'name': 'High', 'level': 3, 'color': '#fd7e14'},
            {'name': 'Critical', 'level': 4, 'color': '#dc3545'}
        ]

        for priority_data in priorities:
            db_manager.execute_query(
                "INSERT OR IGNORE INTO priority_levels (name, level, color) VALUES (?, ?, ?)",
                (priority_data['name'], priority_data['level'], priority_data['color'])
            )
        print("✅ Priority levels created")

        # Create default categories
        categories = [
            {'name': 'Work', 'description': 'Work-related tasks', 'color': '#007bff'},
            {'name': 'Personal', 'description': 'Personal tasks', 'color': '#28a745'},
            {'name': 'Shopping', 'description': 'Shopping and errands', 'color': '#ffc107'},
            {'name': 'Health', 'description': 'Health and fitness', 'color': '#dc3545'}
        ]

        for cat_data in categories:
            db_manager.execute_query(
                "INSERT OR IGNORE INTO categories (name, description, color) VALUES (?, ?, ?)",
                (cat_data['name'], cat_data['description'], cat_data['color'])
            )
        print("✅ Sample categories created")

        # Create sample task
        db_manager.execute_query("""
            INSERT OR IGNORE INTO tasks (title, description, category_id, priority_id, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, 'pending', datetime('now'), datetime('now'))
        """, (
            "Welcome to Task Planner Web!",
            "This is a sample task. You can edit or delete it and create your own tasks.",
            1,  # Work category
            2   # Medium priority
        ))
        print("✅ Sample task created")

        # Create default settings
        default_settings = [
            ('theme', 'light'),
            ('notifications_enabled', 'true'),
            ('reminder_minutes', '15'),
            ('default_priority', '2'),
            ('notification_check_interval', '60'),
            ('sound_alerts_enabled', 'true')
        ]

        for key, value in default_settings:
            db_manager.execute_query(
                "INSERT OR IGNORE INTO user_settings (user_id, setting_key, setting_value) VALUES (1, ?, ?)",
                (key, value)
            )

        print("✅ Default settings created")

    except Exception as e:
        print(f"Warning: Could not create sample data: {e}")

app = Flask(__name__)
app.secret_key = 'task_planner_web_secret_key_2025'
CORS(app)  # Enable CORS for API access

# Initialize database (always try, regardless of desktop models availability)
db_manager = None
if initialize_database():
    print("✅ Database connection established for web version")
else:
    print("❌ Database connection failed")
    db_manager = None

@app.route('/')
def index():
    """Main web application page"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard page"""
    return render_template('dashboard.html')

@app.route('/calendar')
def calendar():
    """Calendar page - using fixed version"""
    return render_template('calendar_fixed.html')

@app.route('/calendar-fixed')
def calendar_fixed():
    """Fixed calendar page with self-contained JavaScript"""
    return render_template('calendar_fixed.html')

@app.route('/recurring')
def recurring():
    """Recurring Tasks page"""
    return render_template('recurring.html')

@app.route('/settings')
def settings():
    """Settings page"""
    return render_template('settings.html')

# API Routes
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks"""
    if not db_manager:
        return jsonify({'error': 'Database not available'}), 500

    try:
        # Get filter parameters
        status_filter = request.args.get('status')
        category_filter = request.args.get('category')
        priority_filter = request.args.get('priority')

        # Build query with filters
        query = """
            SELECT t.*, c.name as category_name, c.color as category_color,
                   p.name as priority_name, p.color as priority_color
            FROM tasks t
            LEFT JOIN categories c ON t.category_id = c.id
            LEFT JOIN priority_levels p ON t.priority_id = p.id
            WHERE 1=1
        """
        params = []

        if status_filter:
            query += " AND t.status = ?"
            params.append(status_filter)
        if category_filter:
            query += " AND t.category_id = ?"
            params.append(category_filter)
        if priority_filter:
            query += " AND t.priority_id = ?"
            params.append(priority_filter)

        query += " ORDER BY t.created_at DESC"

        tasks = db_manager.fetch_all(query, tuple(params) if params else None)
        return jsonify({'tasks': tasks})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Create a new task"""
    if not db_manager:
        return jsonify({'error': 'Database not available'}), 500

    try:
        data = request.get_json()

        # Parse due_date if provided
        due_date = None
        if data.get('due_date'):
            due_date = data['due_date']

        # Parse due_time if provided
        due_time = None
        if data.get('due_time'):
            due_time = data['due_time']

        # Insert task into database
        query = """
            INSERT INTO tasks (title, description, category_id, priority_id, due_date, due_time,
                             estimated_duration, status, is_recurring, recurrence_pattern,
                             recurrence_interval, recurrence_end_date, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """

        params = (
            data['title'],
            data.get('description', ''),
            data.get('category_id'),
            data.get('priority_id', 2),  # Default to medium priority
            due_date,
            due_time,
            data.get('estimated_duration'),
            data.get('status', 'pending'),
            data.get('is_recurring', False),
            data.get('recurrence_pattern'),
            data.get('recurrence_interval'),
            data.get('recurrence_end_date')
        )

        task_id = db_manager.execute_query(query, params)

        if task_id:
            return jsonify({
                'success': True,
                'task_id': task_id,
                'message': 'Task created successfully'
            })
        else:
            return jsonify({'error': 'Failed to save task'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Update an existing task"""
    if not db_manager:
        return jsonify({'error': 'Database not available'}), 500

    try:
        # First check if task exists
        existing_task = db_manager.fetch_one("SELECT * FROM tasks WHERE id = ?", (task_id,))
        if not existing_task:
            return jsonify({'error': 'Task not found'}), 404

        data = request.get_json()

        # Build update query dynamically based on provided fields
        update_fields = []
        params = []

        if 'title' in data:
            update_fields.append("title = ?")
            params.append(data['title'])
        if 'description' in data:
            update_fields.append("description = ?")
            params.append(data['description'])
        if 'status' in data:
            update_fields.append("status = ?")
            params.append(data['status'])
            if data['status'] == 'completed':
                update_fields.append("completed_at = ?")
                params.append(datetime.now().isoformat())
        if 'priority_id' in data:
            update_fields.append("priority_id = ?")
            params.append(data['priority_id'])
        if 'category_id' in data:
            update_fields.append("category_id = ?")
            params.append(data['category_id'])
        if 'due_date' in data:
            update_fields.append("due_date = ?")
            params.append(data['due_date'])
        if 'due_time' in data:
            update_fields.append("due_time = ?")
            params.append(data['due_time'])
        if 'estimated_duration' in data:
            update_fields.append("estimated_duration = ?")
            params.append(data['estimated_duration'])
        if 'actual_duration' in data:
            update_fields.append("actual_duration = ?")
            params.append(data['actual_duration'])
        if 'is_recurring' in data:
            update_fields.append("is_recurring = ?")
            params.append(data['is_recurring'])
        if 'recurrence_pattern' in data:
            update_fields.append("recurrence_pattern = ?")
            params.append(data['recurrence_pattern'])
        if 'recurrence_interval' in data:
            update_fields.append("recurrence_interval = ?")
            params.append(data['recurrence_interval'])
        if 'recurrence_end_date' in data:
            update_fields.append("recurrence_end_date = ?")
            params.append(data['recurrence_end_date'])

        # Always update the updated_at field
        update_fields.append("updated_at = ?")
        params.append(datetime.now().isoformat())

        # Add task_id for WHERE clause
        params.append(task_id)

        query = f"UPDATE tasks SET {', '.join(update_fields)} WHERE id = ?"

        result = db_manager.execute_query(query, params)

        if result is not None:
            return jsonify({
                'success': True,
                'message': 'Task updated successfully'
            })
        else:
            return jsonify({'error': 'Failed to update task'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task"""
    if not db_manager:
        return jsonify({'error': 'Database not available'}), 500

    try:
        # First check if task exists
        existing_task = db_manager.fetch_one("SELECT * FROM tasks WHERE id = ?", (task_id,))
        if not existing_task:
            return jsonify({'error': 'Task not found'}), 404

        # Delete the task
        result = db_manager.execute_query("DELETE FROM tasks WHERE id = ?", (task_id,))

        if result is not None and result > 0:
            return jsonify({
                'success': True,
                'message': 'Task deleted successfully'
            })
        else:
            return jsonify({'error': 'Failed to delete task'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks/recurring', methods=['GET'])
def get_recurring_tasks():
    """Get all recurring tasks"""
    if not db_manager:
        return jsonify({'error': 'Database not available'}), 500

    try:
        query = """
            SELECT t.*, c.name as category_name, c.color as category_color,
                   p.name as priority_name, p.color as priority_color
            FROM tasks t
            LEFT JOIN categories c ON t.category_id = c.id
            LEFT JOIN priority_levels p ON t.priority_id = p.id
            WHERE t.is_recurring = 1
            ORDER BY t.created_at DESC
        """

        recurring_tasks = db_manager.fetch_all(query)
        return jsonify({'tasks': recurring_tasks})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks/calendar/<date_str>', methods=['GET'])
def get_tasks_for_date(date_str):
    """Get tasks for a specific date"""
    if not db_manager:
        return jsonify({'error': 'Database not available'}), 500

    try:
        query = """
            SELECT t.*, c.name as category_name, c.color as category_color,
                   p.name as priority_name, p.color as priority_color
            FROM tasks t
            LEFT JOIN categories c ON t.category_id = c.id
            LEFT JOIN priority_levels p ON t.priority_id = p.id
            WHERE t.due_date = ?
            ORDER BY t.due_time ASC, t.created_at DESC
        """

        tasks = db_manager.fetch_all(query, (date_str,))
        return jsonify({'tasks': tasks})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get all categories"""
    if not db_manager:
        return jsonify({'error': 'Database not available'}), 500

    try:
        categories = db_manager.fetch_all("SELECT * FROM categories ORDER BY name")
        return jsonify({'success': True, 'categories': categories})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/categories', methods=['POST'])
def create_category():
    """Create a new category"""
    if not db_manager:
        return jsonify({'success': False, 'error': 'Database not available'}), 500

    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        name = data.get('name', '').strip()
        if not name:
            return jsonify({'success': False, 'error': 'Category name is required'}), 400

        color = data.get('color', '#3498db')
        description = data.get('description', '').strip()

        # Check if category with same name already exists
        existing = db_manager.fetch_one("SELECT id FROM categories WHERE name = ?", (name,))
        if existing:
            return jsonify({'success': False, 'error': 'Category with this name already exists'}), 400

        # Insert new category
        category_id = db_manager.execute_query(
            "INSERT INTO categories (name, description, color) VALUES (?, ?, ?)",
            (name, description, color)
        )

        if category_id:
            return jsonify({
                'success': True,
                'category_id': category_id,
                'message': 'Category created successfully'
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to create category'}), 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    """Delete a category"""
    if not db_manager:
        return jsonify({'success': False, 'error': 'Database not available'}), 500

    try:
        # Check if category exists
        existing = db_manager.fetch_one("SELECT * FROM categories WHERE id = ?", (category_id,))
        if not existing:
            return jsonify({'success': False, 'error': 'Category not found'}), 404

        # Check if category is being used by any tasks
        tasks_using_category = db_manager.fetch_one(
            "SELECT COUNT(*) as count FROM tasks WHERE category_id = ?",
            (category_id,)
        )

        if tasks_using_category and tasks_using_category['count'] > 0:
            return jsonify({
                'success': False,
                'error': f'Cannot delete category. It is being used by {tasks_using_category["count"]} task(s).'
            }), 400

        # Delete the category
        result = db_manager.execute_query("DELETE FROM categories WHERE id = ?", (category_id,))

        if result is not None:
            return jsonify({
                'success': True,
                'message': 'Category deleted successfully'
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to delete category'}), 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/priorities', methods=['GET'])
def get_priorities():
    """Get all priorities"""
    if not db_manager:
        return jsonify({'error': 'Database not available'}), 500

    try:
        priorities = db_manager.fetch_all("SELECT * FROM priority_levels ORDER BY level")
        return jsonify({'priorities': priorities})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/goals', methods=['GET'])
def get_goals():
    """Get all goals"""
    if not MODELS_AVAILABLE:
        return jsonify({'error': 'Database not available'}), 500

    try:
        goals = Goal.get_all()
        goals_data = []

        for goal in goals:
            goal_data = {
                'id': goal.id,
                'title': goal.title,
                'description': goal.description,
                'status': goal.status,
                'progress_percentage': goal.progress_percentage,
                'target_date': goal.target_date.isoformat() if goal.target_date else None,
                'created_at': goal.created_at.isoformat() if goal.created_at else None
            }
            goals_data.append(goal_data)

        return jsonify({'goals': goals_data})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/overview', methods=['GET'])
def get_analytics_overview():
    """Get analytics overview"""
    if not MODELS_AVAILABLE:
        return jsonify({'error': 'Database not available'}), 500

    try:
        # Get basic statistics
        all_tasks = Task.get_all()
        total_tasks = len(all_tasks)
        completed_tasks = len([t for t in all_tasks if t.status == 'completed'])
        pending_tasks = len([t for t in all_tasks if t.status == 'pending'])
        in_progress_tasks = len([t for t in all_tasks if t.status == 'in_progress'])

        # Calculate completion rate
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

        # Get today's tasks
        today = date.today()
        today_tasks = [t for t in all_tasks if t.due_date == today]

        # Get overdue tasks
        overdue_tasks = [t for t in all_tasks if t.due_date and t.due_date < today and t.status != 'completed']

        analytics_data = {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'pending_tasks': pending_tasks,
            'in_progress_tasks': in_progress_tasks,
            'completion_rate': round(completion_rate, 1),
            'today_tasks': len(today_tasks),
            'overdue_tasks': len(overdue_tasks)
        }

        return jsonify(analytics_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search', methods=['GET'])
def search():
    """Search across tasks, categories, and goals"""
    if not MODELS_AVAILABLE:
        return jsonify({'error': 'Database not available'}), 500

    try:
        query = request.args.get('q', '').strip().lower()
        if len(query) < 2:
            return jsonify({'results': []})

        results = []

        # Search tasks
        tasks = Task.get_all()
        for task in tasks:
            if (query in task.title.lower() or
                (task.description and query in task.description.lower())):
                results.append({
                    'type': 'task',
                    'id': task.id,
                    'title': task.title,
                    'description': task.description or '',
                    'status': task.status
                })

        # Search categories
        categories = Category.get_all()
        for category in categories:
            if query in category.name.lower():
                results.append({
                    'type': 'category',
                    'id': category.id,
                    'title': category.name,
                    'description': category.description or '',
                    'color': category.color
                })

        return jsonify({'results': results[:20]})  # Limit to 20 results

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Settings API Routes
@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Get user settings"""
    if not db_manager:
        return jsonify({'error': 'Database not available'}), 500

    try:
        # Get settings from database or return defaults
        settings = db_manager.fetch_all("SELECT * FROM user_settings WHERE user_id = 1")

        if settings:
            # Convert to key-value pairs
            settings_dict = {setting['setting_key']: setting['setting_value'] for setting in settings}
        else:
            # Return default settings
            settings_dict = {
                'theme': 'light',
                'notifications_enabled': True,
                'reminder_minutes': 15,
                'default_priority': 2
            }

        return jsonify({'settings': settings_dict})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings', methods=['POST'])
def save_settings():
    """Save user settings"""
    if not db_manager:
        return jsonify({'error': 'Database not available'}), 500

    try:
        data = request.get_json()
        settings = data.get('settings', {})

        # Save each setting
        for key, value in settings.items():
            # Check if setting exists
            existing = db_manager.fetch_one(
                "SELECT id FROM user_settings WHERE user_id = 1 AND setting_key = ?",
                (key,)
            )

            if existing:
                # Update existing setting
                db_manager.execute_query(
                    "UPDATE user_settings SET setting_value = ?, updated_at = datetime('now') WHERE user_id = 1 AND setting_key = ?",
                    (str(value), key)
                )
            else:
                # Insert new setting
                db_manager.execute_query(
                    "INSERT INTO user_settings (user_id, setting_key, setting_value, created_at, updated_at) VALUES (1, ?, ?, datetime('now'), datetime('now'))",
                    (key, str(value))
                )

        return jsonify({'success': True, 'message': 'Settings saved successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/database/info', methods=['GET'])
def get_database_info():
    """Get database information"""
    if not db_manager:
        return jsonify({'error': 'Database not available'}), 500

    try:
        # Use the database manager's get_db_info method
        db_info = db_manager.get_db_info()

        return jsonify({
            'success': True,
            'type': db_info['type'],
            'location': db_info['location'],
            'size': db_info['size'],
            'lastModified': db_info['lastModified']
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/database/test', methods=['GET'])
def test_database():
    """Test database connection"""
    if not db_manager:
        return jsonify({'success': False, 'error': 'Database not available'})

    try:
        # Simple test query
        result = db_manager.fetch_one("SELECT COUNT(*) as count FROM tasks")
        return jsonify({
            'success': True,
            'message': f'Connection successful. Found {result["count"]} tasks.'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/database/optimize', methods=['POST'])
def optimize_database():
    """Optimize database"""
    if not db_manager:
        return jsonify({'success': False, 'error': 'Database not available'})

    try:
        # Run VACUUM to optimize SQLite database
        db_manager.execute_query("VACUUM")
        return jsonify({
            'success': True,
            'message': 'Database optimized successfully'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/database/export', methods=['GET'])
def export_database():
    """Export database file"""
    if not db_manager:
        return jsonify({'success': False, 'error': 'Database not available'})

    try:
        import shutil
        from flask import send_file

        db_path = db_manager.db_path
        if not os.path.exists(db_path):
            return jsonify({'success': False, 'error': 'Database file not found'})

        # Create a temporary copy for download
        temp_path = db_path + '.backup'
        shutil.copy2(db_path, temp_path)

        return send_file(
            temp_path,
            as_attachment=True,
            download_name=f'task_planner_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db',
            mimetype='application/octet-stream'
        )

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/database/configure', methods=['POST'])
def configure_database():
    """Configure database settings"""
    global db_manager

    try:
        config = request.get_json()

        if not config:
            return jsonify({'success': False, 'error': 'No configuration provided'})

        db_type = config.get('type', 'sqlite')

        if db_type == 'sqlite':
            # For SQLite, just confirm current configuration
            return jsonify({
                'success': True,
                'message': 'SQLite configuration confirmed'
            })
        elif db_type == 'mysql':
            # Implement MySQL configuration
            host = config.get('host', 'localhost')
            port = config.get('port', 3306)
            database = config.get('database', 'task_planner')
            username = config.get('username', 'root')
            password = config.get('password', '')

            # Validate required fields
            if not all([host, database, username]):
                return jsonify({
                    'success': False,
                    'error': 'Host, database name, and username are required for MySQL'
                })

            try:
                # Try to create MySQL connection
                import mysql.connector
                from mysql.connector import Error

                # Test connection first with proper error handling
                try:
                    connection = mysql.connector.connect(
                        host=host,
                        port=port,
                        database=database,
                        user=username,
                        password=password,
                        connect_timeout=10,  # 10 second timeout
                        autocommit=True
                    )

                    if connection.is_connected():
                        # Create new MySQL database manager
                        mysql_db_manager = MySQLDatabaseManager(host, port, database, username, password)

                        # Test the manager connection
                        if mysql_db_manager.connect():
                            # Initialize tables if they don't exist
                            mysql_db_manager.initialize_tables()

                            # Replace global db_manager
                            if db_manager:
                                db_manager.close()
                            db_manager = mysql_db_manager

                            connection.close()

                            return jsonify({
                                'success': True,
                                'message': f'Successfully connected to MySQL database: {database}@{host}:{port}'
                            })
                        else:
                            connection.close()
                            return jsonify({
                                'success': False,
                                'error': 'Failed to initialize MySQL database manager'
                            })
                    else:
                        return jsonify({
                            'success': False,
                            'error': 'Failed to connect to MySQL database'
                        })

                except mysql.connector.Error as mysql_err:
                    error_msg = str(mysql_err)
                    if "Unknown database" in error_msg:
                        return jsonify({
                            'success': False,
                            'error': f'Database "{database}" does not exist. Please create it first.'
                        })
                    elif "Access denied" in error_msg:
                        return jsonify({
                            'success': False,
                            'error': 'Access denied. Please check username and password.'
                        })
                    elif "Can't connect" in error_msg or "Connection refused" in error_msg:
                        return jsonify({
                            'success': False,
                            'error': f'Cannot connect to MySQL server at {host}:{port}. Please check if the server is running.'
                        })
                    else:
                        return jsonify({
                            'success': False,
                            'error': f'MySQL connection error: {error_msg}'
                        })

            except ImportError:
                return jsonify({
                    'success': False,
                    'error': 'MySQL connector not installed. Please install: pip install mysql-connector-python'
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f'Database configuration error: {str(e)}'
                })
        else:
            return jsonify({
                'success': False,
                'error': f'Unsupported database type: {db_type}'
            })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/export/<data_type>')
def export_data(data_type):
    """Export data (tasks, categories, etc.)"""
    if not db_manager:
        return jsonify({'error': 'Database not available'}), 500

    try:
        format_type = request.args.get('format', 'json')

        if data_type == 'tasks':
            data = db_manager.fetch_all("""
                SELECT t.*, c.name as category_name, p.name as priority_name
                FROM tasks t
                LEFT JOIN categories c ON t.category_id = c.id
                LEFT JOIN priority_levels p ON t.priority_id = p.id
                ORDER BY t.created_at DESC
            """)
        elif data_type == 'categories':
            data = db_manager.fetch_all("SELECT * FROM categories ORDER BY name")
        else:
            return jsonify({'error': 'Invalid data type'}), 400

        if format_type == 'csv':
            # Convert to CSV
            if data:
                import io
                import csv
                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
                csv_content = output.getvalue()
                output.close()

                return jsonify({
                    'success': True,
                    'csv': csv_content
                })
            else:
                return jsonify({
                    'success': True,
                    'csv': ''
                })
        else:
            return jsonify({
                'success': True,
                'data': data
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/notifications/check', methods=['GET'])
def check_notifications():
    """Check for pending notifications (due tasks, overdue tasks, etc.)"""
    if not db_manager:
        return jsonify({'error': 'Database not available'}), 500

    try:
        notifications = []
        now = datetime.now()

        # Get user's reminder setting (default 15 minutes)
        reminder_minutes = 15
        try:
            setting = db_manager.fetch_one(
                "SELECT setting_value FROM user_settings WHERE user_id = 1 AND setting_key = 'reminder_minutes'"
            )
            if setting:
                reminder_minutes = int(setting['setting_value'])
        except:
            pass

        # Check for tasks due soon
        due_tasks = db_manager.fetch_all("""
            SELECT t.*, c.name as category_name
            FROM tasks t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE t.status != 'completed'
            AND t.due_date IS NOT NULL
            AND datetime(t.due_date) BETWEEN datetime('now') AND datetime('now', '+{} minutes')
        """.format(reminder_minutes))

        for task in due_tasks:
            notifications.append({
                'type': 'task_due',
                'title': '⏰ Task Due Soon',
                'message': f'"{task["title"]}" is due in {reminder_minutes} minutes',
                'task': task
            })

        # Check for overdue tasks
        overdue_tasks = db_manager.fetch_all("""
            SELECT t.*, c.name as category_name
            FROM tasks t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE t.status != 'completed'
            AND t.due_date IS NOT NULL
            AND datetime(t.due_date) < datetime('now')
        """)

        for task in overdue_tasks:
            notifications.append({
                'type': 'task_overdue',
                'title': '⚠️ Task Overdue',
                'message': f'"{task["title"]}" is overdue!',
                'task': task
            })

        return jsonify({
            'success': True,
            'notifications': notifications,
            'count': len(notifications)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Production-ready configuration
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))

    print("🌐 Starting Task Planner Web Application...")
    print(f"📍 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"🐛 Debug: {debug_mode}")
    print(f"🗄️  Database: {db_manager.get_db_info()['type'] if db_manager else 'None'}")

    if not debug_mode:
        print("🚀 Running in PRODUCTION mode")
        print("⚠️  Make sure to set proper environment variables for production")

    app.run(debug=debug_mode, host=host, port=port)
