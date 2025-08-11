# Task Planner - MySQL Version

This version uses MySQL database for multi-user environments.

## Requirements
- Python 3.8 or higher
- MySQL Server 5.7 or higher
- Network access to MySQL server

## Setup Instructions

### 1. Install MySQL Server
- Download from: https://dev.mysql.com/downloads/mysql/
- Install and configure with root password

### 2. Create Database
Run in MySQL:
```sql
CREATE DATABASE task_planner CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. Configure Application
1. Run: python main.py
2. Go to Settings → Database
3. Click "Configure Database"
4. Enter your MySQL connection details

### 4. Alternative: Environment Variables
Set these environment variables:
- DB_HOST=localhost
- DB_PORT=3306
- DB_USER=root
- DB_PASSWORD=your_password
- DB_NAME=task_planner

## Multi-User Setup
- Install MySQL on a server
- Configure all clients to connect to the server
- Each user can have their own tasks in the same database

## Backup
Use MySQL backup tools:
```bash
mysqldump -u root -p task_planner > backup.sql
```
