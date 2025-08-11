# Task Planner Web Version - Deployment Guide

## 🚀 Online Deployment Instructions

This guide will help you deploy the Task Planner web version to an online hosting provider with MySQL database support.

### ✅ Pre-Deployment Checklist

**✅ DEPLOYMENT READY STATUS:**
- ✅ No hardcoded localhost URLs
- ✅ Relative API endpoints (/api/*)
- ✅ Environment variable support
- ✅ MySQL compatibility with query conversion
- ✅ JSON serialization fixes for datetime/timedelta
- ✅ Production configuration file
- ✅ Security considerations implemented
- ✅ CORS configuration for cross-origin requests

### Prerequisites

1. **Web Hosting Provider** with Python support (e.g., PythonAnywhere, Heroku, DigitalOcean, AWS)
2. **MySQL Database** (most hosting providers offer this)
3. **Domain name** (optional but recommended)

### Step 1: Prepare Your Files

1. Upload all files from the `web_version` folder to your hosting provider
2. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
   Or manually:
   ```bash
   pip install flask flask-cors mysql-connector-python gunicorn
   ```

### Step 2: Environment Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your production settings:
   ```bash
   # Production settings
   FLASK_ENV=production
   FLASK_DEBUG=False
   SECRET_KEY=your_super_secret_key_here

   # Your domain configuration
   ALLOWED_ORIGINS=https://example.com,https://www.example.com

   # MySQL database settings
   DB_TYPE=mysql
   DB_HOST=your_mysql_host
   DB_NAME=task_planner
   DB_USER=your_mysql_user
   DB_PASSWORD=your_mysql_password
   ```

### Step 3: Database Setup

#### Option A: Using Hosting Provider's MySQL
1. Create a MySQL database through your hosting provider's control panel
2. Note down the database credentials:
   - Host (e.g., `mysql.yourhost.com`)
   - Port (usually `3306`)
   - Database name
   - Username
   - Password

#### Option B: Using Environment Variables (Recommended)
Set these environment variables in your hosting provider:
```bash
FLASK_ENV=production
MYSQL_HOST=your-mysql-host.com
MYSQL_PORT=3306
MYSQL_DATABASE=task_planner
MYSQL_USERNAME=your_username
MYSQL_PASSWORD=your_password
```

### Step 3: Configure Database in Web Interface

1. Access your deployed website
2. Go to Settings → Database
3. Select "MySQL" as database type
4. Enter your database credentials:
   - **Host**: Your MySQL server host (NOT localhost)
   - **Port**: 3306 (or your provider's port)
   - **Database Name**: task_planner (or your chosen name)
   - **Username**: Your database username
   - **Password**: Your database password
5. Click "Save Configuration"
6. Test the connection

### Step 4: Verify Deployment

1. **Test Database Connection**: Use the "Test Connection" button in settings
2. **Create Sample Data**: Add a few tasks to verify everything works
3. **Check All Features**: Test categories, recurring tasks, calendar, etc.

### Common Hosting Providers

#### PythonAnywhere
- Supports Python/Flask applications
- Provides MySQL databases
- Easy deployment through web interface

#### Heroku
- Use ClearDB MySQL add-on
- Set environment variables in Heroku dashboard
- Deploy using Git

#### DigitalOcean App Platform
- Supports Python applications
- Use managed MySQL database
- Deploy from GitHub repository

### Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `FLASK_ENV` | Environment mode | `production` |
| `MYSQL_HOST` | Database host | `mysql.example.com` |
| `MYSQL_PORT` | Database port | `3306` |
| `MYSQL_DATABASE` | Database name | `task_planner` |
| `MYSQL_USERNAME` | Database user | `your_username` |
| `MYSQL_PASSWORD` | Database password | `your_password` |
| `SECRET_KEY` | Flask secret key | `your_secret_key` |

## 🌐 Accessing Your Deployed Application

### Domain Configuration

Once deployed, your Task Planner web application will be accessible through your domain. Here's how to access different sections:

**For domain: `example.com`**

| Page | URL | Description |
|------|-----|-------------|
| **Home Page** | `https://example.com/` | Main task management interface |
| **Dashboard** | `https://example.com/dashboard` | Analytics and overview |
| **Calendar** | `https://example.com/calendar` | Calendar view of tasks |
| **Recurring Tasks** | `https://example.com/recurring` | Manage recurring tasks |
| **Settings** | `https://example.com/settings` | Application settings and database config |

### API Endpoints

The application also provides REST API endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `https://example.com/api/tasks` | GET | Get all tasks |
| `https://example.com/api/tasks` | POST | Create new task |
| `https://example.com/api/categories` | GET | Get all categories |
| `https://example.com/api/priorities` | GET | Get all priorities |
| `https://example.com/api/database/info` | GET | Get database information |

### Default Landing Page

**The application automatically redirects to the main task interface when users visit your domain root (`https://example.com/`).**

### Mobile Access

The web application is fully responsive and works on:
- 📱 Mobile phones
- 📱 Tablets
- 💻 Desktop computers
- 🖥️ Large screens

### Troubleshooting

#### "Cannot connect to MySQL server"
- Check if your hosting provider's MySQL service is running
- Verify the host and port are correct
- Ensure your IP is whitelisted (if required)

#### "Access denied"
- Double-check username and password
- Verify the user has permissions for the database

#### "Unknown database"
- Create the database through your hosting provider's control panel
- Ensure the database name matches exactly

### Security Notes

1. **Never use default passwords** in production
2. **Use environment variables** for sensitive data
3. **Enable SSL** if your hosting provider supports it
4. **Regular backups** of your database

### Performance Tips

1. **Use MySQL** instead of SQLite for better performance
2. **Enable caching** if your hosting provider supports it
3. **Optimize database** regularly
4. **Monitor resource usage**

### Support

If you encounter issues:
1. Check your hosting provider's documentation
2. Verify all environment variables are set correctly
3. Test database connection separately
4. Check application logs for error messages
