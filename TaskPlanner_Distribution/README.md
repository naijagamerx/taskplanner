# Task Planner - Comprehensive Life Planning Application

A powerful desktop task planning application built with Python that helps users organize their daily, weekly, monthly, and yearly tasks and goals.

## Features

### 📋 Task Management
- Create, edit, and delete tasks
- Set priorities (Low, Medium, High, Critical)
- Organize tasks by categories
- Set due dates and times
- Add detailed descriptions
- Mark tasks as completed
- Support for recurring tasks
- Subtask functionality

### 📅 Calendar Integration
- Month, week, and day views
- Visual task scheduling
- Drag-and-drop task management
- Calendar overview with task indicators
- Quick task creation for specific dates

### 📊 Analytics & Reporting
- Task completion statistics
- Productivity charts and graphs
- Category-based analytics
- Priority distribution analysis
- Progress tracking over time
- Goal achievement metrics

### 🎯 Goal Management
- Set long-term and short-term goals
- Track goal progress with percentage completion
- Link tasks to specific goals
- Goal categorization
- Target date tracking

### ⚙️ Customization
- Light and dark themes
- Customizable categories with colors
- Flexible date and time formats
- Configurable work hours
- Personal preferences settings

### 💾 Data Management
- MySQL database for reliable data storage
- Data export/import functionality
- Automatic data backup
- Settings persistence

## Technology Stack

- **Frontend**: Python with CustomTkinter for modern GUI
- **Database**: MySQL for robust data storage
- **Charts**: Matplotlib for analytics visualization
- **Calendar**: TkCalendar for date selection
- **Packaging**: PyInstaller for executable creation

## Installation

### Prerequisites

1. **Python 3.8 or higher**
2. **MySQL Server** (5.7 or higher)
3. **Git** (for cloning the repository)

### Database Setup

1. Install and start MySQL server
2. Create a database user (or use root)
3. The application will automatically create the required database and tables

### Application Installation

#### Option 1: Run from Source

1. Clone the repository:
```bash
git clone <repository-url>
cd tasksplanner
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure database connection (optional):
   - Set environment variables:
     - `DB_HOST` (default: localhost)
     - `DB_PORT` (default: 3306)
     - `DB_USER` (default: root)
     - `DB_PASSWORD` (default: empty)
     - `DB_NAME` (default: task_planner)

4. Run the application:
```bash
python main.py
```

#### Option 2: Build Executable

1. Follow steps 1-2 from Option 1
2. Build the executable:
```bash
python setup.py
```
3. Find the executable in the `dist` folder

## Configuration

### Database Configuration

The application uses the following default database settings:
- Host: localhost
- Port: 3306
- User: root
- Password: (empty)
- Database: task_planner

You can modify these settings by:
1. Setting environment variables
2. Editing `config/database_config.py`
3. Using the Settings interface in the application

### Application Settings

Access settings through the application's Settings panel:
- **General**: Default reminder times, work hours, date formats
- **Appearance**: Themes, colors, font sizes
- **Database**: Connection information and testing
- **Categories**: Manage task categories
- **Backup**: Export and import data

## Usage Guide

### Getting Started

1. **First Launch**: The application will automatically create the database schema
2. **Create Categories**: Set up your task categories (Work, Personal, etc.)
3. **Add Tasks**: Start creating tasks with due dates and priorities
4. **Set Goals**: Define your long-term objectives
5. **Use Calendar**: Schedule and visualize your tasks
6. **Track Progress**: Monitor your productivity with analytics

### Task Management

- **Quick Add**: Use the "+" button in the sidebar for quick task creation
- **Detailed Tasks**: Access full task dialog for comprehensive task setup
- **Recurring Tasks**: Set up daily, weekly, monthly, or yearly recurring tasks
- **Task Filtering**: Filter tasks by status, priority, category, or search terms

### Calendar Views

- **Month View**: Overview of tasks across the month
- **Week View**: Detailed weekly schedule with time slots
- **Day View**: Hour-by-hour task breakdown for a specific day

### Analytics

- **Overview Dashboard**: Quick statistics and charts
- **Productivity Analysis**: Track your completion rates and trends
- **Category Breakdown**: See how tasks are distributed across categories
- **Goal Progress**: Monitor advancement toward your objectives

## Database Schema

The application uses a comprehensive MySQL schema with the following main tables:

- `users` - User accounts (future multi-user support)
- `categories` - Task categories with colors
- `priority_levels` - Task priority definitions
- `tasks` - Main task storage with full details
- `goals` - Goal tracking and progress
- `task_goals` - Links between tasks and goals
- `time_entries` - Time tracking for tasks
- `reminders` - Task reminder system
- `notes` - Additional notes for tasks/goals
- `tags` - Flexible tagging system
- `user_settings` - Application preferences

## Development

### Project Structure

```
tasksplanner/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── setup.py               # Build script
├── config/
│   └── database_config.py # Database configuration
├── database/
│   ├── db_manager.py      # Database connection manager
│   └── schema.sql         # Database schema
├── models/
│   ├── task.py           # Task model
│   ├── category.py       # Category and Priority models
│   └── goal.py           # Goal model
├── gui/
│   ├── main_window.py    # Main application window
│   ├── task_manager.py   # Task management interface
│   ├── calendar_view.py  # Calendar interface
│   ├── analytics.py      # Analytics and reporting
│   ├── settings.py       # Settings interface
│   └── dialogs/
│       └── task_dialog.py # Task creation/editing dialog
└── utils/                # Utility functions (future)
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Building for Distribution

1. Ensure all dependencies are installed
2. Run the build script: `python setup.py`
3. Test the executable in the `dist` folder
4. Create installer using platform-specific tools (NSIS for Windows, etc.)

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Ensure MySQL server is running
   - Check database credentials
   - Verify network connectivity

2. **Application Won't Start**
   - Check Python version (3.8+ required)
   - Verify all dependencies are installed
   - Check for error messages in console

3. **Tasks Not Saving**
   - Check database connection
   - Verify database permissions
   - Check disk space

4. **Calendar Not Loading**
   - Ensure tkcalendar is properly installed
   - Check for date format conflicts

### Getting Help

- Check the application logs for error messages
- Verify database connectivity using the Settings panel
- Ensure all required Python packages are installed
- Check MySQL server status and permissions

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- CustomTkinter for the modern GUI framework
- MySQL for reliable database storage
- Matplotlib for analytics visualization
- TkCalendar for calendar functionality
- The Python community for excellent libraries and tools

## Version History

- **v1.0.0** - Initial release with core task management features
- **v1.1.0** - Added calendar views and analytics (planned)
- **v1.2.0** - Enhanced goal tracking and reporting (planned)
- **v2.0.0** - Multi-user support and cloud sync (planned)

---

**Task Planner** - Organize your life, achieve your goals! 🎯
