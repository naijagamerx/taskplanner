"""
Database creation script for Task Planner
Creates the database and all tables step by step
"""

import mysql.connector
from mysql.connector import Error

def create_database_and_tables():
    """Create database and all tables"""

    config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': '',
        'charset': 'utf8mb4',
        'autocommit': True
    }

    try:
        print("🔗 Connecting to MySQL...")
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()

        # Create database
        print("🏗️  Creating database 'task_planner'...")
        cursor.execute("CREATE DATABASE IF NOT EXISTS task_planner CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.execute("USE task_planner")
        print("✅ Database created/selected")

        # Create users table
        print("📋 Creating users table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE,
                password_hash VARCHAR(255),
                first_name VARCHAR(50),
                last_name VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        """)
        print("✅ Users table created")

        # Create priority_levels table
        print("📋 Creating priority_levels table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS priority_levels (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(20) NOT NULL UNIQUE,
                level INT NOT NULL UNIQUE,
                color VARCHAR(7) NOT NULL,
                description VARCHAR(100)
            )
        """)
        print("✅ Priority levels table created")

        # Create categories table
        print("📋 Creating categories table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT DEFAULT 1,
                name VARCHAR(100) NOT NULL,
                color VARCHAR(7) DEFAULT '#3498db',
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE KEY unique_user_category (user_id, name)
            )
        """)
        print("✅ Categories table created")

        # Create tasks table
        print("📋 Creating tasks table...")
        cursor.execute("""
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
                status ENUM('pending', 'in_progress', 'completed', 'cancelled') DEFAULT 'pending',
                is_recurring BOOLEAN DEFAULT FALSE,
                recurrence_pattern VARCHAR(50),
                recurrence_interval INT DEFAULT 1,
                recurrence_end_date DATE,
                parent_task_id INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                completed_at TIMESTAMP NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
                FOREIGN KEY (priority_id) REFERENCES priority_levels(id) ON DELETE SET NULL,
                FOREIGN KEY (parent_task_id) REFERENCES tasks(id) ON DELETE CASCADE,
                INDEX idx_user_status (user_id, status),
                INDEX idx_due_date (due_date),
                INDEX idx_category (category_id),
                INDEX idx_priority (priority_id)
            )
        """)
        print("✅ Tasks table created")

        # Create goals table
        print("📋 Creating goals table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS goals (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT DEFAULT 1,
                category_id INT,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                target_date DATE,
                status ENUM('active', 'completed', 'paused', 'cancelled') DEFAULT 'active',
                progress_percentage DECIMAL(5,2) DEFAULT 0.00,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                completed_at TIMESTAMP NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
                INDEX idx_user_status (user_id, status),
                INDEX idx_target_date (target_date)
            )
        """)
        print("✅ Goals table created")

        # Create task_goals table
        print("📋 Creating task_goals table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_goals (
                id INT AUTO_INCREMENT PRIMARY KEY,
                task_id INT NOT NULL,
                goal_id INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
                FOREIGN KEY (goal_id) REFERENCES goals(id) ON DELETE CASCADE,
                UNIQUE KEY unique_task_goal (task_id, goal_id)
            )
        """)
        print("✅ Task-goals table created")

        # Create time_entries table
        print("📋 Creating time_entries table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS time_entries (
                id INT AUTO_INCREMENT PRIMARY KEY,
                task_id INT NOT NULL,
                user_id INT DEFAULT 1,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP NULL,
                duration INT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_task_date (task_id, start_time),
                INDEX idx_user_date (user_id, start_time)
            )
        """)
        print("✅ Time entries table created")

        # Create reminders table
        print("📋 Creating reminders table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INT AUTO_INCREMENT PRIMARY KEY,
                task_id INT NOT NULL,
                reminder_time TIMESTAMP NOT NULL,
                message TEXT,
                is_sent BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
                INDEX idx_reminder_time (reminder_time, is_sent)
            )
        """)
        print("✅ Reminders table created")

        # Create notes table
        print("📋 Creating notes table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT DEFAULT 1,
                task_id INT,
                goal_id INT,
                title VARCHAR(255),
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
                FOREIGN KEY (goal_id) REFERENCES goals(id) ON DELETE CASCADE,
                INDEX idx_user_created (user_id, created_at),
                INDEX idx_task (task_id),
                INDEX idx_goal (goal_id)
            )
        """)
        print("✅ Notes table created")

        # Create tags table
        print("📋 Creating tags table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT DEFAULT 1,
                name VARCHAR(50) NOT NULL,
                color VARCHAR(7) DEFAULT '#95a5a6',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE KEY unique_user_tag (user_id, name)
            )
        """)
        print("✅ Tags table created")

        # Create task_tags table
        print("📋 Creating task_tags table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_tags (
                id INT AUTO_INCREMENT PRIMARY KEY,
                task_id INT NOT NULL,
                tag_id INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE,
                UNIQUE KEY unique_task_tag (task_id, tag_id)
            )
        """)
        print("✅ Task-tags table created")

        # Create user_settings table
        print("📋 Creating user_settings table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT DEFAULT 1,
                setting_key VARCHAR(100) NOT NULL,
                setting_value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE KEY unique_user_setting (user_id, setting_key)
            )
        """)
        print("✅ User settings table created")

        # Insert default data
        print("\n📊 Inserting default data...")

        # Default user
        cursor.execute("""
            INSERT IGNORE INTO users (id, username, first_name, last_name)
            VALUES (1, 'default_user', 'Default', 'User')
        """)
        print("✅ Default user created")

        # Priority levels
        priorities = [
            ('Low', 1, '#95a5a6', 'Low priority tasks'),
            ('Medium', 2, '#f39c12', 'Medium priority tasks'),
            ('High', 3, '#e74c3c', 'High priority tasks'),
            ('Critical', 4, '#8e44ad', 'Critical priority tasks')
        ]

        for name, level, color, desc in priorities:
            cursor.execute("""
                INSERT IGNORE INTO priority_levels (name, level, color, description)
                VALUES (%s, %s, %s, %s)
            """, (name, level, color, desc))
        print("✅ Priority levels created")

        # Default categories
        categories = [
            ('Work', '#3498db', 'Work-related tasks'),
            ('Personal', '#2ecc71', 'Personal tasks and activities'),
            ('Health', '#e74c3c', 'Health and fitness related'),
            ('Learning', '#9b59b6', 'Education and skill development'),
            ('Finance', '#f39c12', 'Financial planning and management'),
            ('Home', '#1abc9c', 'Home and family related tasks')
        ]

        for name, color, desc in categories:
            cursor.execute("""
                INSERT IGNORE INTO categories (name, color, description)
                VALUES (%s, %s, %s)
            """, (name, color, desc))
        print("✅ Default categories created")

        # Default settings
        settings = [
            ('theme', 'light'),
            ('default_reminder_time', '15'),
            ('work_hours_start', '09:00'),
            ('work_hours_end', '17:00'),
            ('date_format', '%Y-%m-%d'),
            ('time_format', '%H:%M')
        ]

        for key, value in settings:
            cursor.execute("""
                INSERT IGNORE INTO user_settings (setting_key, setting_value)
                VALUES (%s, %s)
            """, (key, value))
        print("✅ Default settings created")

        # Verify everything was created
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]

        print(f"\n📊 Database Summary:")
        print(f"   • Database: task_planner")
        print(f"   • Tables created: {len(table_names)}")
        for table in sorted(table_names):
            print(f"     - {table}")

        # Check data counts
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM priority_levels")
        priority_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM categories")
        category_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM user_settings")
        settings_count = cursor.fetchone()[0]

        print(f"\n📊 Default Data:")
        print(f"   • Users: {user_count}")
        print(f"   • Priority levels: {priority_count}")
        print(f"   • Categories: {category_count}")
        print(f"   • Settings: {settings_count}")

        cursor.close()
        connection.close()

        print("\n🎉 Database setup completed successfully!")
        print("✅ Ready to run the Task Planner application!")

        return True

    except Error as e:
        print(f"❌ MySQL Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🏗️  Task Planner Database Setup")
    print("=" * 60)

    success = create_database_and_tables()

    if success:
        print("\n🚀 You can now run: py main.py")
    else:
        print("\n❌ Database setup failed. Please check the errors above.")
