BEGIN TRANSACTION;
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER DEFAULT 1,
    name VARCHAR(100) NOT NULL,
    color VARCHAR(7) DEFAULT '#3498db',
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, name)
);
INSERT INTO "categories" VALUES(1,1,'Work','#3498db','Work-related tasks and projects','2025-05-26 19:03:14','2025-05-26 19:03:14');
INSERT INTO "categories" VALUES(2,1,'Personal','#e74c3c','Personal tasks and activities','2025-05-26 19:03:14','2025-05-26 19:03:14');
INSERT INTO "categories" VALUES(3,1,'Health','#2ecc71','Health and fitness related','2025-05-26 19:03:14','2025-05-26 19:03:14');
INSERT INTO "categories" VALUES(4,1,'Learning','#f39c12','Education and skill development','2025-05-26 19:03:14','2025-05-26 19:03:14');
INSERT INTO "categories" VALUES(5,1,'Finance','#9b59b6','Financial planning and management','2025-05-26 19:03:14','2025-05-26 19:03:14');
INSERT INTO "categories" VALUES(36,1,'Help','#3498db','','2025-05-26 20:21:18','2025-05-26 20:21:18');
INSERT INTO "categories" VALUES(47,1,'Test Category','#FF5733','Test category for verification','2025-05-26 20:39:59','2025-05-26 20:39:59');
INSERT INTO "categories" VALUES(48,1,'Test Dialog Category','#FF5733','Test category from dialog simulation','2025-05-26 20:42:05','2025-05-26 20:42:05');
INSERT INTO "categories" VALUES(49,1,'Test Category 1748292241','#FF5733','Test category for verification','2025-05-26 20:44:01','2025-05-26 20:44:01');
INSERT INTO "categories" VALUES(50,1,'Final Test Category 1748292299','#00FF00','Final test category','2025-05-26 20:44:59','2025-05-26 20:44:59');
CREATE TABLE goal_milestones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    goal_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    target_date DATE,
    completed BOOLEAN DEFAULT 0,
    completed_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (goal_id) REFERENCES goals(id) ON DELETE CASCADE
);
CREATE TABLE goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER DEFAULT 1,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category_id INTEGER,
    target_date DATE,
    status VARCHAR(20) DEFAULT 'active',
    progress INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
);
CREATE TABLE habit_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id INTEGER NOT NULL,
    date DATE NOT NULL,
    completed_count INTEGER DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE,
    UNIQUE(habit_id, date)
);
CREATE TABLE habits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER DEFAULT 1,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category_id INTEGER,
    frequency VARCHAR(20) DEFAULT 'daily',
    target_count INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
);
CREATE TABLE notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER DEFAULT 1,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    category_id INTEGER,
    tags TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
);
CREATE TABLE priority_levels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(20) NOT NULL UNIQUE,
    level INTEGER NOT NULL UNIQUE,
    color VARCHAR(7) NOT NULL,
    description VARCHAR(100)
);
INSERT INTO "priority_levels" VALUES(1,'Low',1,'#95a5a6','Low priority tasks');
INSERT INTO "priority_levels" VALUES(2,'Medium',2,'#f39c12','Medium priority tasks');
INSERT INTO "priority_levels" VALUES(3,'High',3,'#e74c3c','High priority tasks');
INSERT INTO "priority_levels" VALUES(4,'Critical',4,'#8e44ad','Critical priority tasks');
CREATE TABLE project_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    task_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    UNIQUE(project_id, task_id)
);
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER DEFAULT 1,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category_id INTEGER,
    status VARCHAR(20) DEFAULT 'active',
    start_date DATE,
    end_date DATE,
    progress INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
);
CREATE TABLE task_attachments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER,
    mime_type VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
);
CREATE TABLE task_comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    comment TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
);
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER DEFAULT 1,
    category_id INTEGER,
    priority_id INTEGER,
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
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
    FOREIGN KEY (priority_id) REFERENCES priority_levels(id) ON DELETE SET NULL,
    FOREIGN KEY (parent_task_id) REFERENCES tasks(id) ON DELETE CASCADE
);
INSERT INTO "tasks" VALUES(1,1,5,2,'Test Calendar Task','This is a test task to verify calendar functionality','2025-05-26','14:30:00',NULL,NULL,'completed',0,NULL,1,NULL,NULL,15,'2025-05-26 14:19:05.436925','2025-05-26 19:05:28','2025-05-26 19:19:05');
INSERT INTO "tasks" VALUES(2,1,5,2,'Test Calendar Task','This is a test task to verify calendar functionality','2025-05-26','14:30:00',NULL,NULL,'pending',0,NULL,1,NULL,NULL,15,NULL,'2025-05-26 19:05:52','2025-05-26 19:05:52');
INSERT INTO "tasks" VALUES(3,1,2,2,'Do lundary','Lundary day tomorrow','2025-05-26',NULL,30,NULL,'pending',0,NULL,1,NULL,NULL,15,NULL,'2025-05-26 19:08:01','2025-05-26 19:08:01');
INSERT INTO "tasks" VALUES(4,1,4,3,'School with the children','School with the children and talk to their teacher','2025-05-26','23:45:00',25,NULL,'pending',0,NULL,1,NULL,NULL,15,NULL,'2025-05-26 19:28:27','2025-05-26 19:30:14');
INSERT INTO "tasks" VALUES(5,1,5,2,'Do invoice','Do invoice','2025-05-27','02:45:00',30,NULL,'pending',0,NULL,1,NULL,NULL,15,NULL,'2025-05-26 20:17:54','2025-05-26 20:17:54');
INSERT INTO "tasks" VALUES(6,1,NULL,2,'ghh','fdd','2025-05-26',NULL,NULL,NULL,'pending',0,NULL,1,NULL,NULL,15,NULL,'2025-05-26 20:18:42','2025-05-26 20:31:54');
INSERT INTO "tasks" VALUES(7,1,36,2,'Work','Work','2025-05-26',NULL,NULL,NULL,'completed',0,NULL,1,NULL,NULL,15,'2025-05-26 15:31:46.306011','2025-05-26 20:21:56','2025-05-26 20:31:46');
INSERT INTO "tasks" VALUES(8,1,5,1,'Updated Test Task','This task has been updated','2025-05-26','14:30:00',60,NULL,'in_progress',0,NULL,1,NULL,NULL,15,NULL,'2025-05-26 20:27:47','2025-05-26 20:27:47');
INSERT INTO "tasks" VALUES(9,1,NULL,2,'UI Test Task 1748291333','This task was created to test UI refresh',NULL,NULL,NULL,NULL,'pending',0,NULL,1,NULL,NULL,15,NULL,'2025-05-26 20:28:53','2025-05-26 20:28:53');
INSERT INTO "tasks" VALUES(10,1,NULL,2,'hjhjh','','2025-05-26',NULL,NULL,NULL,'pending',0,NULL,1,NULL,NULL,15,NULL,'2025-05-26 20:29:21','2025-05-26 20:31:52');
INSERT INTO "tasks" VALUES(11,1,5,1,'Updated Test Task','This task is created during comprehensive testing','2025-05-26','15:30:00',45,NULL,'pending',0,NULL,1,NULL,NULL,15,NULL,'2025-05-26 20:39:59','2025-05-26 20:39:59');
INSERT INTO "tasks" VALUES(12,1,5,2,'Test Dialog Task','This task simulates dialog creation','2025-05-26','14:30:00',60,NULL,'pending',0,NULL,1,NULL,NULL,15,NULL,'2025-05-26 20:42:05','2025-05-26 20:42:05');
INSERT INTO "tasks" VALUES(13,1,5,1,'Updated Test Task','This task is created during comprehensive testing','2025-05-26','15:30:00',45,NULL,'pending',0,NULL,1,NULL,NULL,15,NULL,'2025-05-26 20:43:34','2025-05-26 20:43:34');
INSERT INTO "tasks" VALUES(14,1,5,1,'Updated Test Task','This task is created during comprehensive testing','2025-05-26','15:30:00',45,NULL,'pending',0,NULL,1,NULL,NULL,15,NULL,'2025-05-26 20:44:01','2025-05-26 20:44:01');
INSERT INTO "tasks" VALUES(15,1,5,1,'Final Test Task','Testing before compilation','2025-05-26',NULL,NULL,NULL,'pending',0,NULL,1,NULL,NULL,15,NULL,'2025-05-26 20:44:59','2025-05-26 20:44:59');
CREATE TABLE user_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER DEFAULT 1,
    setting_key VARCHAR(100) NOT NULL,
    setting_value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, setting_key)
);
INSERT INTO "user_settings" VALUES(1,1,'theme','light','2025-05-26 19:03:14','2025-05-26 19:03:14');
INSERT INTO "user_settings" VALUES(2,1,'default_reminder_time','15','2025-05-26 19:03:14','2025-05-26 19:03:14');
INSERT INTO "user_settings" VALUES(3,1,'work_hours_start','09:00','2025-05-26 19:03:14','2025-05-26 19:03:14');
INSERT INTO "user_settings" VALUES(4,1,'work_hours_end','17:00','2025-05-26 19:03:14','2025-05-26 19:03:14');
INSERT INTO "user_settings" VALUES(5,1,'date_format','%Y-%m-%d','2025-05-26 19:03:14','2025-05-26 19:03:14');
INSERT INTO "user_settings" VALUES(6,1,'time_format','%H:%M','2025-05-26 19:03:14','2025-05-26 19:03:14');
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255),
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);
INSERT INTO "users" VALUES(1,'default_user',NULL,NULL,'Default','User','2025-05-26 19:03:14','2025-05-26 19:03:14',1);
CREATE INDEX idx_tasks_category_id ON tasks(category_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_priority ON tasks(priority_id);
CREATE INDEX idx_goals_category_id ON goals(category_id);
CREATE INDEX idx_goals_status ON goals(status);
CREATE INDEX idx_projects_category_id ON projects(category_id);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_notes_category_id ON notes(category_id);
CREATE INDEX idx_habits_category_id ON habits(category_id);
CREATE INDEX idx_habit_tracking_habit_id ON habit_tracking(habit_id);
CREATE INDEX idx_habit_tracking_date ON habit_tracking(date);
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('users',1);
INSERT INTO "sqlite_sequence" VALUES('priority_levels',40);
INSERT INTO "sqlite_sequence" VALUES('categories',55);
INSERT INTO "sqlite_sequence" VALUES('user_settings',60);
INSERT INTO "sqlite_sequence" VALUES('tasks',15);
COMMIT;
