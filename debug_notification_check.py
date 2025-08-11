"""
Debug notification check to see exactly what's happening
"""

import sys
sys.path.append('.')
from models.task import Task
from models.category import Category
from datetime import datetime, timedelta, time as datetime_time

print('🔍 DEBUG: Notification Check Analysis')
print('='*60)

# Get current time
now = datetime.now()
print(f'Current time: {now.strftime("%Y-%m-%d %H:%M:%S")}')

# Check notification settings
from database.settings_manager import SettingsManager
settings = SettingsManager()
reminder_minutes = settings.get('reminder_minutes_before', 15)
print(f'Reminder setting: {reminder_minutes} minutes before due time')

# Calculate reminder window
reminder_time = now + timedelta(minutes=reminder_minutes)
print(f'Reminder window: {now.strftime("%H:%M:%S")} to {reminder_time.strftime("%H:%M:%S")}')
print()

# Get all tasks
tasks = Task.get_all()
print(f'Total tasks: {len(tasks)}')

# Analyze each task
for i, task in enumerate(tasks, 1):
    print(f'\n📋 Task {i}: {task.title}')
    print(f'   Status: {task.status}')
    print(f'   Due Date: {task.due_date}')
    print(f'   Due Time: {task.due_time} (type: {type(task.due_time)})')
    
    if task.due_date and task.due_time and task.status in ['pending', 'in_progress']:
        # Handle time conversion
        due_time = task.due_time
        print(f'   Original due_time: {due_time}')
        
        if hasattr(due_time, 'total_seconds'):
            print('   Converting timedelta to time...')
            total_seconds = int(due_time.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            due_time = datetime_time(hours, minutes, seconds)
            print(f'   Converted due_time: {due_time}')
        
        # Combine date and time
        task_datetime = datetime.combine(task.due_date, due_time)
        print(f'   Task datetime: {task_datetime.strftime("%Y-%m-%d %H:%M:%S")}')
        
        # Check timing
        time_diff = task_datetime - now
        print(f'   Time until due: {time_diff}')
        
        # Check notification conditions
        print(f'   Checking conditions:')
        print(f'     now <= task_datetime: {now <= task_datetime}')
        print(f'     task_datetime <= reminder_time: {task_datetime <= reminder_time}')
        print(f'     Both conditions: {now <= task_datetime <= reminder_time}')
        
        if now <= task_datetime <= reminder_time:
            print('   🔔 SHOULD SEND REMINDER NOTIFICATION!')
        elif task_datetime < now:
            print('   🔴 SHOULD SEND OVERDUE NOTIFICATION!')
        else:
            print('   ⏰ No notification needed yet')
    else:
        print('   ⏸️ Skipped (no due date/time or not pending/in_progress)')

print('\n' + '='*60)
print('🧪 TESTING NOTIFICATION MANAGER')
print('='*60)

# Test the actual notification manager
try:
    from services.notification_manager import notification_manager
    
    print('✅ Notification manager imported')
    
    # Check current settings
    print(f'Manager reminder_minutes: {notification_manager.reminder_minutes}')
    print(f'Manager desktop_notifications_enabled: {notification_manager.desktop_notifications_enabled}')
    print(f'Manager monitoring_enabled: {notification_manager.monitoring_enabled}')
    
    # Force a check with debug
    print('\n🔍 Forcing notification check with debug...')
    
    # Manually run the check logic with debug
    now = datetime.now()
    reminder_time = now + timedelta(minutes=notification_manager.reminder_minutes)
    
    print(f'Manager check - Now: {now.strftime("%H:%M:%S")}')
    print(f'Manager check - Reminder window: {reminder_time.strftime("%H:%M:%S")}')
    
    tasks = Task.get_all()
    notifications_sent = 0
    
    for task in tasks:
        if (task.due_date and task.due_time and
            task.status in ['pending', 'in_progress']):
            
            # Same logic as in notification manager
            due_time = task.due_time
            if hasattr(due_time, 'total_seconds'):
                total_seconds = int(due_time.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60
                due_time = datetime_time(hours, minutes, seconds)
            
            task_datetime = datetime.combine(task.due_date, due_time)
            
            print(f'\nChecking task: {task.title}')
            print(f'  Task datetime: {task_datetime}')
            print(f'  Now <= task_datetime <= reminder_time: {now <= task_datetime <= reminder_time}')
            print(f'  task_datetime < now (overdue): {task_datetime < now}')
            
            # Check if task is due within reminder window
            if now <= task_datetime <= reminder_time:
                print(f'  🔔 SENDING REMINDER for {task.title}')
                notification_manager.send_task_reminder(task, task_datetime)
                notifications_sent += 1
            
            # Check for overdue tasks
            elif task_datetime < now:
                print(f'  🔴 SENDING OVERDUE for {task.title}')
                notification_manager.send_overdue_notification(task, task_datetime)
                notifications_sent += 1
    
    print(f'\n📊 Notifications sent: {notifications_sent}')
    
    if notifications_sent == 0:
        print('💡 No notifications sent. To test:')
        print('   1. Create a task due in 10-15 minutes')
        print('   2. Or modify an existing task to be due soon')
        print('   3. Run this script again')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()

print('\n' + '='*60)
print('🎯 SUMMARY')
print('='*60)
print('This debug script shows exactly what the notification system sees.')
print('If no notifications were sent, check the timing conditions above.')
