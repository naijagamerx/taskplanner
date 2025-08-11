# 🚀 Task Planner Web - Deployment Checklist

## ✅ Pre-Deployment Verification

### Code Quality & Security
- [x] **No hardcoded localhost URLs** - All URLs are relative or use environment variables
- [x] **No hardcoded database credentials** - Uses environment variables
- [x] **Secret key configuration** - Uses environment variable for Flask secret key
- [x] **Debug mode disabled** - Set to False for production
- [x] **CORS properly configured** - Allows specific origins only
- [x] **SQL injection protection** - Uses parameterized queries
- [x] **JSON serialization fixed** - Handles datetime/timedelta objects

### Database Compatibility
- [x] **MySQL integration working** - Query conversion from SQLite to MySQL syntax
- [x] **SQLite fallback available** - Works with both database types
- [x] **Database connection error handling** - Graceful failure handling
- [x] **Environment variable support** - DB configuration via environment

### Frontend Compatibility
- [x] **Responsive design** - Works on mobile, tablet, desktop
- [x] **Relative API calls** - All AJAX calls use relative URLs (/api/*)
- [x] **CDN resources** - Bootstrap and icons loaded from CDN
- [x] **Cross-browser compatibility** - Modern browser support

## 🌐 Deployment Steps

### 1. File Preparation
- [ ] Upload all `web_version` files to hosting provider
- [ ] Ensure file permissions are correct (755 for directories, 644 for files)
- [ ] Verify Python version compatibility (3.8+)

### 2. Environment Setup
- [ ] Copy `.env.example` to `.env`
- [ ] Configure production environment variables:
  - [ ] `FLASK_ENV=production`
  - [ ] `FLASK_DEBUG=False`
  - [ ] `SECRET_KEY=your_unique_secret_key`
  - [ ] `ALLOWED_ORIGINS=https://yourdomain.com`
  - [ ] Database credentials (MySQL recommended)

### 3. Dependencies Installation
- [ ] Install Python packages: `pip install -r requirements.txt`
- [ ] Verify Flask installation: `python -c "import flask; print(flask.__version__)"`
- [ ] Verify MySQL connector: `python -c "import mysql.connector; print('MySQL OK')"`

### 4. Database Setup
- [ ] Create MySQL database on hosting provider
- [ ] Configure database credentials in environment variables
- [ ] Test database connection
- [ ] Initialize database tables (automatic on first run)

### 5. Web Server Configuration
- [ ] Configure WSGI server (gunicorn recommended)
- [ ] Set up reverse proxy (nginx recommended)
- [ ] Configure SSL/HTTPS
- [ ] Set up domain DNS records

### 6. Testing
- [ ] Test home page loads: `https://yourdomain.com/`
- [ ] Test API endpoints: `https://yourdomain.com/api/tasks`
- [ ] Test database operations (create, read, update, delete tasks)
- [ ] Test settings page and database configuration
- [ ] Test mobile responsiveness

## 🔧 Production Configuration

### Environment Variables
```bash
# Required
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your_super_secret_key_here
DB_TYPE=mysql
DB_HOST=your_mysql_host
DB_NAME=task_planner
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password

# Optional
ALLOWED_ORIGINS=https://yourdomain.com
PORT=5000
HOST=0.0.0.0
```

### Recommended WSGI Configuration (gunicorn)
```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 app:app
```

### Nginx Configuration Example
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🌐 Domain Access Examples

### For domain: `example.com`

**Main Pages:**
- Home: `https://example.com/`
- Dashboard: `https://example.com/dashboard`
- Calendar: `https://example.com/calendar`
- Settings: `https://example.com/settings`

**API Endpoints:**
- Tasks: `https://example.com/api/tasks`
- Categories: `https://example.com/api/categories`
- Database Info: `https://example.com/api/database/info`

## ⚠️ Common Issues & Solutions

### Database Connection Issues
- **Error**: "Cannot connect to MySQL server"
- **Solution**: Check host, port, and firewall settings

### CORS Issues
- **Error**: "Access blocked by CORS policy"
- **Solution**: Update `ALLOWED_ORIGINS` environment variable

### Static Files Not Loading
- **Error**: CSS/JS files not found
- **Solution**: Ensure static files are uploaded and accessible

### 500 Internal Server Error
- **Error**: Application crashes on startup
- **Solution**: Check logs, verify environment variables, test database connection

## 🎯 Post-Deployment Verification

### Functional Testing
- [ ] Create a new task
- [ ] Edit an existing task
- [ ] Delete a task
- [ ] Filter tasks by category/priority
- [ ] Test recurring tasks
- [ ] Test calendar view
- [ ] Test settings configuration

### Performance Testing
- [ ] Page load times < 3 seconds
- [ ] API response times < 1 second
- [ ] Database queries optimized
- [ ] No memory leaks

### Security Testing
- [ ] HTTPS enabled
- [ ] No sensitive data in URLs
- [ ] Database credentials secure
- [ ] CORS properly configured

## 🎉 Deployment Complete!

Once all items are checked, your Task Planner web application is ready for production use!

**Access your application at: `https://yourdomain.com/`**
