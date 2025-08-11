"""
Desktop Notification Manager for Task Planner
Handles desktop notifications, reminders, and sound alerts
"""

import os
import sys
import threading
import time
from datetime import datetime, timedelta
from typing import List, Optional
import json

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Try to import plyer for cross-platform notifications
    from plyer import notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False
    print("Plyer not available. Installing...")
    import subprocess
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "plyer"])
        from plyer import notification
        PLYER_AVAILABLE = True
    except:
        print("Failed to install plyer. Desktop notifications will be limited.")

try:
    # Try to import pygame for sound alerts
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("Pygame not available. Installing...")
    import subprocess
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
        import pygame
        PYGAME_AVAILABLE = True
    except:
        print("Failed to install pygame. Sound alerts will be disabled.")

from models.task import Task
from database.settings_manager import SettingsManager

class NotificationManager:
    """Manages desktop notifications and reminders"""
    
    def __init__(self):
        self.settings = SettingsManager()
        self.running = False
        self.notification_thread = None
        self.sound_initialized = False
        
        # Initialize sound system
        self.init_sound_system()
        
        # Load notification settings
        self.load_settings()
        
    def init_sound_system(self):
        """Initialize pygame sound system"""
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.init()
                self.sound_initialized = True
                print("Sound system initialized successfully")
            except Exception as e:
                print(f"Failed to initialize sound system: {e}")
                self.sound_initialized = False
        
    def load_settings(self):
        """Load notification settings"""
        try:
            self.desktop_notifications_enabled = self.settings.get('desktop_notifications_enabled', True)
            self.sound_alerts_enabled = self.settings.get('sound_alerts_enabled', True)
            self.reminder_minutes = self.settings.get('reminder_minutes_before', 15)
            self.notification_sound = self.settings.get('notification_sound', 'default')
            self.check_interval = self.settings.get('notification_check_interval', 60)  # seconds
        except Exception as e:
            print(f"Error loading notification settings: {e}")
            # Set defaults
            self.desktop_notifications_enabled = True
            self.sound_alerts_enabled = True
            self.reminder_minutes = 15
            self.notification_sound = 'default'
            self.check_interval = 60
    
    def save_settings(self):
        """Save notification settings"""
        try:
            self.settings.set('desktop_notifications_enabled', self.desktop_notifications_enabled)
            self.settings.set('sound_alerts_enabled', self.sound_alerts_enabled)
            self.settings.set('reminder_minutes_before', self.reminder_minutes)
            self.settings.set('notification_sound', self.notification_sound)
            self.settings.set('notification_check_interval', self.check_interval)
            self.settings.save()
        except Exception as e:
            print(f"Error saving notification settings: {e}")
    
    def show_desktop_notification(self, title: str, message: str, timeout: int = 10):
        """Show desktop notification"""
        if not self.desktop_notifications_enabled:
            return
            
        try:
            if PLYER_AVAILABLE:
                notification.notify(
                    title=title,
                    message=message,
                    app_name="Task Planner",
                    timeout=timeout,
                    app_icon=self.get_app_icon_path()
                )
            else:
                # Fallback for Windows
                if sys.platform == "win32":
                    import subprocess
                    subprocess.run([
                        'powershell', '-Command',
                        f'Add-Type -AssemblyName System.Windows.Forms; '
                        f'[System.Windows.Forms.MessageBox]::Show("{message}", "{title}")'
                    ], shell=True)
                else:
                    print(f"Notification: {title} - {message}")
        except Exception as e:
            print(f"Error showing desktop notification: {e}")
    
    def play_notification_sound(self, sound_type: str = 'default'):
        """Play notification sound"""
        if not self.sound_alerts_enabled or not self.sound_initialized:
            return
            
        try:
            sound_file = self.get_sound_file_path(sound_type)
            if sound_file and os.path.exists(sound_file):
                pygame.mixer.music.load(sound_file)
                pygame.mixer.music.play()
            else:
                # Play system beep as fallback
                if sys.platform == "win32":
                    import winsound
                    winsound.Beep(800, 500)  # 800 Hz for 500ms
                else:
                    print('\a')  # Terminal bell
        except Exception as e:
            print(f"Error playing notification sound: {e}")
    
    def get_app_icon_path(self) -> Optional[str]:
        """Get application icon path"""
        try:
            # Look for icon in assets folder
            icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'icon.ico')
            if os.path.exists(icon_path):
                return icon_path
            return None
        except:
            return None
    
    def get_sound_file_path(self, sound_type: str) -> Optional[str]:
        """Get sound file path"""
        try:
            # Look for sound files in assets/sounds folder
            sounds_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'sounds')
            sound_files = {
                'default': 'notification.wav',
                'reminder': 'reminder.wav',
                'urgent': 'urgent.wav',
                'complete': 'complete.wav'
            }
            
            sound_file = sound_files.get(sound_type, 'notification.wav')
            sound_path = os.path.join(sounds_dir, sound_file)
            
            if os.path.exists(sound_path):
                return sound_path
            return None
        except:
            return None
    
    def check_task_reminders(self):
        """Check for tasks that need reminders"""
        try:
            now = datetime.now()
            reminder_time = now + timedelta(minutes=self.reminder_minutes)
            
            # Get tasks due within reminder window
            tasks = Task.get_all()
            for task in tasks:
                if (task.due_date and task.due_time and 
                    task.status in ['pending', 'in_progress']):
                    
                    # Combine date and time
                    task_datetime = datetime.combine(task.due_date, task.due_time)
                    
                    # Check if task is due within reminder window
                    if now <= task_datetime <= reminder_time:
                        self.send_task_reminder(task, task_datetime)
                    
                    # Check for overdue tasks
                    elif task_datetime < now:
                        self.send_overdue_notification(task, task_datetime)
                        
        except Exception as e:
            print(f"Error checking task reminders: {e}")
    
    def send_task_reminder(self, task, task_datetime):
        """Send reminder for upcoming task"""
        time_until = task_datetime - datetime.now()
        minutes_until = int(time_until.total_seconds() / 60)
        
        title = "📅 Task Reminder"
        message = f"'{task.title}' is due in {minutes_until} minutes"
        
        self.show_desktop_notification(title, message)
        self.play_notification_sound('reminder')
    
    def send_overdue_notification(self, task, task_datetime):
        """Send notification for overdue task"""
        time_overdue = datetime.now() - task_datetime
        hours_overdue = int(time_overdue.total_seconds() / 3600)
        
        title = "⚠️ Overdue Task"
        if hours_overdue < 1:
            message = f"'{task.title}' is overdue"
        else:
            message = f"'{task.title}' is {hours_overdue} hours overdue"
        
        self.show_desktop_notification(title, message, timeout=15)
        self.play_notification_sound('urgent')
    
    def send_task_completion_notification(self, task):
        """Send notification when task is completed"""
        title = "✅ Task Completed"
        message = f"Great job! You completed '{task.title}'"
        
        self.show_desktop_notification(title, message)
        self.play_notification_sound('complete')
    
    def start_monitoring(self):
        """Start monitoring for task reminders"""
        if self.running:
            return
            
        self.running = True
        self.notification_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.notification_thread.start()
        print("Notification monitoring started")
    
    def stop_monitoring(self):
        """Stop monitoring for task reminders"""
        self.running = False
        if self.notification_thread:
            self.notification_thread.join(timeout=1)
        print("Notification monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                self.check_task_reminders()
                time.sleep(self.check_interval)
            except Exception as e:
                print(f"Error in notification monitoring loop: {e}")
                time.sleep(self.check_interval)
    
    def test_notification(self):
        """Test desktop notification system"""
        self.show_desktop_notification(
            "🔔 Test Notification",
            "Desktop notifications are working correctly!"
        )
        self.play_notification_sound('default')

# Global notification manager instance
notification_manager = NotificationManager()
