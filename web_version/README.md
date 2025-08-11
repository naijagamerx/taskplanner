# 🌐 Task Planner Web Version

A modern, responsive web-based version of the Task Planner application that runs in any browser.

## ✨ **Features**

### 🎨 **Modern Web Interface**
- **Responsive Design** - Works on desktop, tablet, and mobile
- **Dark/Light Mode** - Toggle between themes with persistence
- **Bootstrap 5** - Modern, professional UI components
- **Real-time Updates** - Dynamic content loading without page refresh

### 📋 **Task Management**
- **Full CRUD Operations** - Create, read, update, delete tasks
- **Priority System** - Visual priority indicators and filtering
- **Category Organization** - Organize tasks by categories
- **Status Tracking** - Pending, In Progress, Completed states
- **Due Date Management** - Set and track task deadlines

### 🔍 **Smart Features**
- **Global Search** - Search across all tasks and categories
- **Advanced Filtering** - Filter by status, category, priority
- **Task Templates** - Quick task creation with pre-filled templates
- **List/Grid Views** - Switch between different display modes

### 📊 **Analytics Dashboard**
- **Visual Charts** - Task distribution and progress charts
- **Productivity Metrics** - Completion rates and trends
- **Today's Focus** - Highlight tasks due today
- **Recent Activity** - Track recent task changes

### 🔧 **Technical Features**
- **RESTful API** - Clean API endpoints for all operations
- **Database Integration** - Uses same database as desktop version
- **Real-time Search** - Instant search results as you type
- **Toast Notifications** - User-friendly feedback messages

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.7 or higher
- Existing Task Planner desktop installation (for database access)

### **Installation**

1. **Navigate to web version directory:**
   ```bash
   cd web_version
   ```

2. **Install requirements:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python run_web.py
   ```

4. **Open your browser:**
   - Main App: http://localhost:5000
   - Dashboard: http://localhost:5000/dashboard

### **Alternative Launch Methods**

**Direct Flask run:**
```bash
python app.py
```

**Production deployment:**
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 🌐 **Accessing the Web Version**

### **Local Access**
- **Main Interface:** http://localhost:5000
- **Analytics Dashboard:** http://localhost:5000/dashboard
- **API Documentation:** http://localhost:5000/api/

### **Network Access**
The web version runs on `0.0.0.0:5000` by default, making it accessible from other devices on your network:
- Find your computer's IP address (e.g., 192.168.1.100)
- Access from other devices: http://192.168.1.100:5000

### **Mobile Access**
The responsive design works perfectly on mobile devices:
- Open any modern browser on your phone/tablet
- Navigate to your computer's IP address
- Enjoy full functionality on mobile!

## 📱 **Browser Compatibility**

### **Fully Supported**
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

### **Mobile Browsers**
- ✅ Chrome Mobile
- ✅ Safari Mobile
- ✅ Firefox Mobile
- ✅ Samsung Internet

## 🔌 **API Endpoints**

### **Tasks**
- `GET /api/tasks` - Get all tasks
- `POST /api/tasks` - Create new task
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task

### **Categories**
- `GET /api/categories` - Get all categories

### **Priorities**
- `GET /api/priorities` - Get all priorities

### **Goals**
- `GET /api/goals` - Get all goals

### **Analytics**
- `GET /api/analytics/overview` - Get analytics overview

### **Search**
- `GET /api/search?q={query}` - Global search

## 🎨 **Customization**

### **Themes**
The web version supports light and dark themes:
- Click the moon/sun icon in the navigation bar
- Theme preference is saved in browser localStorage
- Automatic theme detection based on system preference

### **Styling**
Customize the appearance by editing:
- `static/css/style.css` - Main stylesheet
- CSS custom properties for easy color changes
- Bootstrap variables for component styling

## 🔧 **Configuration**

### **Database Connection**
The web version automatically uses the same database as your desktop application:
- SQLite: Uses the existing `task_planner.db` file
- MySQL: Uses the same connection settings

### **Port Configuration**
Change the default port (5000) by modifying `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8080)
```

### **Debug Mode**
For production, disable debug mode:
```python
app.run(debug=False, host='0.0.0.0', port=5000)
```

## 🔒 **Security Considerations**

### **Development Mode**
- Debug mode is enabled by default for development
- Disable debug mode for production deployment
- Use environment variables for sensitive configuration

### **Network Access**
- The app binds to `0.0.0.0` for network access
- Consider firewall rules for production deployment
- Use HTTPS in production environments

## 🐛 **Troubleshooting**

### **Common Issues**

**"Flask not found" error:**
```bash
pip install flask flask-cors
```

**"Models not accessible" warning:**
- Ensure you're running from the correct directory
- Check that the desktop version is properly installed
- Verify database file permissions

**Port already in use:**
- Change the port in `app.py` or `run_web.py`
- Kill existing processes using the port

**Database connection issues:**
- Ensure the desktop application database is accessible
- Check file permissions for SQLite database
- Verify MySQL connection settings if using MySQL

### **Performance Tips**
- Use a production WSGI server (gunicorn, waitress) for better performance
- Enable browser caching for static assets
- Consider using a reverse proxy (nginx) for production

## 🔄 **Data Synchronization**

### **Real-time Sync**
- Web version uses the same database as desktop version
- Changes made in web version appear in desktop version
- Changes made in desktop version appear in web version after refresh

### **Concurrent Usage**
- Both desktop and web versions can be used simultaneously
- Database handles concurrent access safely
- Refresh web version to see desktop changes

## 🚀 **Deployment Options**

### **Local Network**
Perfect for home or office use:
- Run on one computer
- Access from any device on the network
- No internet connection required

### **Cloud Deployment**
For remote access:
- Deploy to cloud platforms (Heroku, DigitalOcean, AWS)
- Configure database connection for cloud environment
- Set up proper security measures

### **Docker Deployment**
For containerized deployment:
```dockerfile
FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python", "app.py"]
```

## 📞 **Support**

### **Getting Help**
- Check the troubleshooting section above
- Review the desktop version documentation
- Ensure all requirements are properly installed

### **Feature Requests**
The web version is designed to complement the desktop version:
- Core functionality matches desktop features
- Web-specific enhancements for browser environment
- Mobile-optimized interface for on-the-go access

---

## 🎉 **Enjoy Your Web-Based Task Management!**

The Task Planner Web Version brings all the power of the desktop application to your browser, with the added convenience of mobile access and network sharing. Perfect for teams, families, or anyone who wants to access their tasks from anywhere!
