"""
Desktop Notification Manager for Task Planner
Handles desktop notifications, reminders, and sound alerts
"""

import os
import sys
import threading
import time
from datetime import datetime, timedelta
from datetime import time as datetime_time
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
        subprocess.check_call([sys.executable, "-m", "pip", "install", "plyer"], creationflags=subprocess.CREATE_NO_WINDOW)
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
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"], creationflags=subprocess.CREATE_NO_WINDOW)
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
        self.monitoring_enabled = True
        self.last_check_time = datetime.now()
        self.check_failures = 0
        self.max_check_failures = 5

        # Set Application User Model ID for proper Windows notifications
        self.set_app_user_model_id()

        # Initialize sound system
        self.init_sound_system()

        # Track sent notifications to prevent spam
        self.sent_notifications = set()
        self.last_notification_reset = datetime.now()

        # Load notification settings
        self.load_settings()

        # Auto-start monitoring if enabled
        if self.monitoring_enabled:
            self.start_monitoring()

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

    def set_app_user_model_id(self):
        """Set Application User Model ID for proper Windows notifications"""
        try:
            if sys.platform == "win32":
                import ctypes
                from ctypes import wintypes

                # Set the Application User Model ID
                app_id = "TaskPlanner.DesktopApp.1.0"
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
                print(f"Application User Model ID set to: {app_id}")
        except Exception as e:
            print(f"Failed to set Application User Model ID: {e}")

    def load_settings(self):
        """Load notification settings"""
        try:
            self.desktop_notifications_enabled = self.settings.get('desktop_notifications_enabled', True)
            self.sound_alerts_enabled = self.settings.get('sound_alerts_enabled', True)
            self.reminder_minutes = self.settings.get('reminder_minutes_before', 15)
            self.notification_sound = self.settings.get('notification_sound', 'default')
            self.check_interval = self.settings.get('notification_check_interval', 30)  # seconds - check every 30s for countdown notifications
            self.monitoring_enabled = self.settings.get('notification_monitoring_enabled', True)
        except Exception as e:
            print(f"Error loading notification settings: {e}")
            # Set defaults
            self.desktop_notifications_enabled = True
            self.sound_alerts_enabled = True
            self.reminder_minutes = 15
            self.notification_sound = 'default'
            self.check_interval = 30
            self.monitoring_enabled = True

    def save_settings(self):
        """Save notification settings"""
        try:
            self.settings.set('desktop_notifications_enabled', self.desktop_notifications_enabled)
            self.settings.set('sound_alerts_enabled', self.sound_alerts_enabled)
            self.settings.set('reminder_minutes_before', self.reminder_minutes)
            self.settings.set('notification_sound', self.notification_sound)
            self.settings.set('notification_check_interval', self.check_interval)
            self.settings.set('notification_monitoring_enabled', self.monitoring_enabled)
            self.settings.save()
        except Exception as e:
            print(f"Error saving notification settings: {e}")

    def show_desktop_notification(self, title: str, message: str, timeout: int = 10):
        """Show desktop notification with compiled-environment support"""
        if not self.desktop_notifications_enabled:
            return

        try:
            # Check if running in compiled environment
            is_compiled = getattr(sys, 'frozen', False)
            success = False

            # For compiled environments, use more reliable methods first
            if is_compiled and sys.platform == "win32":
                print(f"Running in compiled mode, using native Windows notifications")

                # Method 1: PowerShell Toast (most reliable in compiled)
                try:
                    success = self._show_powershell_toast_reliable(title, message)
                    if success:
                        print(f"Notification sent via PowerShell Toast: {title}")
                except Exception as e:
                    print(f"PowerShell Toast notification failed: {e}")

                # Method 2: Windows MessageBox (always works)
                if not success:
                    try:
                        success = self._show_windows_messagebox(title, message)
                        if success:
                            print(f"Notification sent via Windows MessageBox: {title}")
                    except Exception as e:
                        print(f"Windows MessageBox failed: {e}")

            # For development environment or if compiled methods failed
            if not success:
                # Method 3: Try plyer (development environment)
                if PLYER_AVAILABLE:
                    try:
                        notification.notify(
                            title=title,
                            message=message,
                            app_name="Task Planner",
                            timeout=timeout,
                            app_icon=self.get_app_icon_path()
                        )
                        success = True
                        print(f"Notification sent via plyer: {title}")
                    except Exception as e:
                        print(f"Plyer notification failed: {e}")

                # Method 4: Windows Toast (development)
                if sys.platform == "win32" and not success:
                    try:
                        success = self._show_windows_toast(title, message, timeout)
                        if success:
                            print(f"Notification sent via Windows Toast: {title}")
                    except Exception as e:
                        print(f"Windows Toast notification failed: {e}")

            # Final fallback - always show something
            if not success:
                print(f"NOTIFICATION: {title} - {message}")
                # Show a simple message box as last resort
                try:
                    self._show_windows_messagebox(title, message)
                except:
                    pass

        except Exception as e:
            print(f"Error showing desktop notification: {e}")
            print(f"NOTIFICATION: {title} - {message}")

    def _show_windows_toast(self, title: str, message: str, timeout: int = 10) -> bool:
        """Show Windows 10+ toast notification using win10toast"""
        try:
            # Try to import and use win10toast
            from win10toast import ToastNotifier
            toaster = ToastNotifier()
            toaster.show_toast(
                title=title,
                msg=message,
                app_name="Task Planner",
                duration=timeout,
                threaded=True
            )
            return True
        except ImportError:
            # Try to install win10toast
            try:
                import subprocess
                subprocess.check_call([sys.executable, "-m", "pip", "install", "win10toast"], creationflags=subprocess.CREATE_NO_WINDOW)
                from win10toast import ToastNotifier
                toaster = ToastNotifier()
                toaster.show_toast(
                    title=title,
                    msg=message,
                    app_name="Task Planner",
                    duration=timeout,
                    threaded=True
                )
                return True
            except:
                return False
        except Exception:
            return False

    def _show_windows_balloon(self, title: str, message: str, timeout: int = 10) -> bool:
        """Show Windows balloon tip notification"""
        try:
            import win32gui
            import win32con
            import win32api

            # Create a simple balloon tip
            hwnd = win32gui.GetForegroundWindow()
            if hwnd:
                win32api.MessageBox(0, message, title, win32con.MB_ICONINFORMATION | win32con.MB_TOPMOST)
                return True
            return False
        except ImportError:
            return False
        except Exception:
            return False

    def _show_powershell_toast(self, title: str, message: str) -> bool:
        """Show toast notification using PowerShell"""
        try:
            import subprocess

            # Escape quotes in title and message
            title_escaped = title.replace('"', '""')
            message_escaped = message.replace('"', '""')

            # PowerShell command to show toast notification
            ps_command = f'''
            [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            [Windows.UI.Notifications.ToastNotification, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

            $template = @"
            <toast>
                <visual>
                    <binding template="ToastText02">
                        <text id="1">{title_escaped}</text>
                        <text id="2">{message_escaped}</text>
                    </binding>
                </visual>
            </toast>
"@

            $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
            $xml.LoadXml($template)
            $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
            $notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("TaskPlanner.DesktopApp.1.0")
            $notifier.Show($toast)
            '''

            result = subprocess.run([
                'powershell', '-WindowStyle', 'Hidden', '-Command', ps_command
            ], capture_output=True, text=True, timeout=10, creationflags=subprocess.CREATE_NO_WINDOW)

            return result.returncode == 0
        except Exception:
            return False

    def _show_powershell_toast_reliable(self, title: str, message: str) -> bool:
        """Show toast notification using PowerShell - optimized for compiled environments"""
        try:
            import subprocess

            # Escape quotes and special characters
            title_clean = title.replace('"', '""').replace("'", "''")
            message_clean = message.replace('"', '""').replace("'", "''")

            # Simplified PowerShell command that works better in compiled environments
            ps_command = f'''
            try {{
                [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
                [Windows.UI.Notifications.ToastNotification, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
                [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

                $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
                $toastXml = @"
<toast>
    <visual>
        <binding template="ToastText02">
            <text id="1">{title_clean}</text>
            <text id="2">{message_clean}</text>
        </binding>
    </visual>
</toast>
"@
                $xml.LoadXml($toastXml)
                $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
                $notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("TaskPlanner.DesktopApp.1.0")
                $notifier.Show($toast)
                Write-Host "SUCCESS"
            }} catch {{
                Write-Host "FAILED: $($_.Exception.Message)"
            }}
            '''

            result = subprocess.run([
                'powershell', '-WindowStyle', 'Hidden', '-ExecutionPolicy', 'Bypass', '-Command', ps_command
            ], capture_output=True, text=True, timeout=15, creationflags=subprocess.CREATE_NO_WINDOW)

            return "SUCCESS" in result.stdout

        except Exception as e:
            print(f"PowerShell toast error: {e}")
            return False

    def _show_windows_messagebox(self, title: str, message: str) -> bool:
        """Show Windows MessageBox - always works in compiled environments"""
        try:
            import ctypes
            from ctypes import wintypes

            # Use ctypes to call Windows API directly
            user32 = ctypes.windll.user32

            # MessageBox with information icon and topmost flag
            # MB_ICONINFORMATION (0x40) | MB_TOPMOST (0x40000) | MB_OK (0x0)
            result = user32.MessageBoxW(
                0,  # hWnd (no parent window)
                message,  # lpText
                title,  # lpCaption
                0x40 | 0x40000  # dwType: MB_ICONINFORMATION | MB_TOPMOST
            )

            return result != 0  # Returns non-zero on success

        except Exception as e:
            print(f"Windows MessageBox error: {e}")
            return False

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
            # Get the directory where the application is located
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                app_dir = os.path.dirname(sys.executable)
            else:
                # Running as script
                app_dir = os.path.dirname(os.path.dirname(__file__))

            # Look for icon in assets folder
            icon_path = os.path.join(app_dir, 'assets', 'icons', 'app_icon.ico')
            if os.path.exists(icon_path):
                return icon_path
            return None
        except:
            return None

    def get_sound_file_path(self, sound_type: str) -> Optional[str]:
        """Get sound file path"""
        try:
            # Get the directory where the application is located
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                app_dir = os.path.dirname(sys.executable)
            else:
                # Running as script
                app_dir = os.path.dirname(os.path.dirname(__file__))

            # Look for sound files in assets/sounds folder
            sounds_dir = os.path.join(app_dir, 'assets', 'sounds')
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
        """Check for tasks that need reminders with improved error handling"""
        try:
            now = datetime.now()
            self.last_check_time = now

            # Reset notification tracking daily
            if (now - self.last_notification_reset).days >= 1:
                self.sent_notifications.clear()
                self.last_notification_reset = now
                print("Notification tracking reset for new day")

            reminder_time = now + timedelta(minutes=self.reminder_minutes)

            # Test database connection before proceeding
            from database.db_manager import db_manager
            if not db_manager.test_connection():
                print("Database connection failed during notification check")
                self.check_failures += 1
                if self.check_failures >= self.max_check_failures:
                    print("Too many database failures, stopping notification monitoring")
                    self.stop_monitoring()
                return

            # Reset failure count on successful connection
            self.check_failures = 0

            # Get tasks due within reminder window
            tasks = Task.get_all()
            if not tasks:
                return  # No tasks to check

            for task in tasks:
                if (task.due_date and task.due_time and
                    task.status in ['pending', 'in_progress']):

                    # Ensure due_time is a time object (handle SQLite timedelta)
                    due_time = task.due_time
                    if hasattr(due_time, 'total_seconds'):
                        # Convert timedelta to time
                        total_seconds = int(due_time.total_seconds())
                        hours = total_seconds // 3600
                        minutes = (total_seconds % 3600) // 60
                        seconds = total_seconds % 60
                        due_time = datetime_time(hours, minutes, seconds)

                    # Combine date and time
                    task_datetime = datetime.combine(task.due_date, due_time)

                    # Calculate time until due
                    time_until = task_datetime - now
                    minutes_until = int(time_until.total_seconds() / 60)

                    # Send countdown notifications for tasks due within reminder window
                    # Send notifications at 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1 minutes
                    if 1 <= minutes_until <= self.reminder_minutes:
                        self.send_task_reminder(task, task_datetime)

                    # Check for overdue tasks
                    elif task_datetime < now:
                        self.send_overdue_notification(task, task_datetime)

        except Exception as e:
            print(f"Error checking task reminders: {e}")
            self.check_failures += 1
            if self.check_failures >= self.max_check_failures:
                print("Too many check failures, stopping notification monitoring")
                self.stop_monitoring()

    def send_task_reminder(self, task, task_datetime):
        """Send reminder for upcoming task"""
        time_until = task_datetime - datetime.now()
        minutes_until = int(time_until.total_seconds() / 60)

        # Create unique notification key that includes the minutes until due
        # This allows multiple notifications for the same task (15, 14, 13, 12, 11 minutes)
        notification_key = f"reminder_{task.id}_{task_datetime.strftime('%Y%m%d_%H%M')}_{minutes_until}min"

        # Check if we already sent this specific minute notification
        if notification_key in self.sent_notifications:
            return

        title = "📅 Task Reminder"
        message = f"'{task.title}' is due in {minutes_until} minutes"

        self.show_desktop_notification(title, message)
        self.play_notification_sound('reminder')

        # Mark this specific minute notification as sent
        self.sent_notifications.add(notification_key)

        print(f"📅 Sent reminder: {task.title} - {minutes_until} minutes until due")

    def send_overdue_notification(self, task, task_datetime):
        """Send notification for overdue task"""
        # Create unique notification key (send overdue notification once per day)
        notification_key = f"overdue_{task.id}_{datetime.now().strftime('%Y%m%d')}"

        # Check if we already sent this notification today
        if notification_key in self.sent_notifications:
            return

        time_overdue = datetime.now() - task_datetime
        hours_overdue = int(time_overdue.total_seconds() / 3600)

        title = "⚠️ Overdue Task"
        if hours_overdue < 1:
            message = f"'{task.title}' is overdue"
        else:
            message = f"'{task.title}' is {hours_overdue} hours overdue"

        self.show_desktop_notification(title, message, timeout=15)
        self.play_notification_sound('urgent')

        # Mark notification as sent
        self.sent_notifications.add(notification_key)

    def send_task_completion_notification(self, task):
        """Send notification when task is completed"""
        title = "✅ Task Completed"
        message = f"Great job! You completed '{task.title}'"

        # Add smart context
        try:
            # Check if this completes a goal or milestone
            from models.goal import Goal
            goals = Goal.get_all()
            related_goals = [g for g in goals if g.category_id == task.category_id and g.status == 'active']

            if related_goals:
                message += f"\n🎯 This contributes to your '{related_goals[0].title}' goal!"

            # Check productivity streak
            completed_today = len([t for t in Task.get_all()
                                 if t.status == 'completed' and
                                 t.completed_at and
                                 t.completed_at.date() == datetime.now().date()])

            if completed_today >= 5:
                message += f"\n🔥 You're on fire! {completed_today} tasks completed today!"

        except Exception as e:
            print(f"Error adding smart context to completion notification: {e}")

        self.show_desktop_notification(title, message)
        self.play_notification_sound('complete')

    def send_smart_reminder(self, task):
        """Send context-aware smart reminder"""
        try:
            # Analyze task context
            context = self.analyze_task_context(task)

            # Generate smart message
            title = "🔔 Smart Reminder"
            message = f"'{task.title}' is due soon"

            # Add context-based suggestions
            if context['estimated_time'] <= 30:
                message += "\n💡 Quick task - perfect for a short break!"
            elif context['similar_tasks_completed']:
                avg_time = context['avg_completion_time']
                message += f"\n⏱️ Similar tasks took ~{avg_time} minutes on average"

            if context['optimal_time']:
                message += f"\n🕐 Best time to do this: {context['optimal_time']}"

            if context['energy_level']:
                message += f"\n⚡ Recommended energy level: {context['energy_level']}"

            self.show_desktop_notification(title, message, timeout=20)
            self.play_notification_sound('reminder')

        except Exception as e:
            print(f"Error sending smart reminder: {e}")
            # Fallback to basic reminder
            self.send_task_reminder(task)

    def analyze_task_context(self, task) -> dict:
        """Analyze task context for smart notifications"""
        context = {
            'estimated_time': task.estimated_duration or 60,
            'similar_tasks_completed': 0,
            'avg_completion_time': 0,
            'optimal_time': None,
            'energy_level': 'medium'
        }

        try:
            # Find similar completed tasks
            all_tasks = Task.get_all()
            similar_tasks = [
                t for t in all_tasks
                if (t.status == 'completed' and
                    t.category_id == task.category_id and
                    t.priority_id == task.priority_id and
                    t.actual_duration)
            ]

            if similar_tasks:
                context['similar_tasks_completed'] = len(similar_tasks)
                context['avg_completion_time'] = sum(t.actual_duration for t in similar_tasks) // len(similar_tasks)

            # Determine optimal time based on historical data
            current_hour = datetime.now().hour
            if 9 <= current_hour <= 11:
                context['optimal_time'] = "morning (high focus)"
            elif 14 <= current_hour <= 16:
                context['optimal_time'] = "afternoon (good energy)"
            elif current_hour >= 19:
                context['optimal_time'] = "evening (wind down tasks)"

            # Suggest energy level based on task complexity
            if task.estimated_duration and task.estimated_duration > 120:
                context['energy_level'] = 'high'
            elif task.estimated_duration and task.estimated_duration < 30:
                context['energy_level'] = 'low'

        except Exception as e:
            print(f"Error analyzing task context: {e}")

        return context

    def start_monitoring(self):
        """Start monitoring for task reminders with persistence"""
        if self.running:
            print("Notification monitoring already running")
            return

        if not self.monitoring_enabled:
            print("Notification monitoring is disabled")
            return

        try:
            self.running = True
            self.check_failures = 0
            self.notification_thread = threading.Thread(target=self._monitoring_loop, daemon=False)
            self.notification_thread.start()
            print("Notification monitoring started successfully")
        except Exception as e:
            print(f"Failed to start notification monitoring: {e}")
            self.running = False

    def stop_monitoring(self):
        """Stop monitoring for task reminders"""
        print("Stopping notification monitoring...")
        self.running = False
        if self.notification_thread and self.notification_thread.is_alive():
            self.notification_thread.join(timeout=2)
        print("Notification monitoring stopped")

    def restart_monitoring(self):
        """Restart monitoring after failure"""
        print("Restarting notification monitoring...")
        self.stop_monitoring()
        time.sleep(1)  # Brief pause before restart
        self.start_monitoring()

    def is_monitoring_active(self):
        """Check if monitoring is currently active"""
        return self.running and self.notification_thread and self.notification_thread.is_alive()

    def _monitoring_loop(self):
        """Main monitoring loop with improved error handling and persistence"""
        print("Notification monitoring loop started")
        consecutive_errors = 0
        max_consecutive_errors = 3

        while self.running:
            try:
                # Check if monitoring is still enabled
                if not self.monitoring_enabled:
                    print("Monitoring disabled, stopping loop")
                    break

                # Perform the actual check
                self.check_task_reminders()
                consecutive_errors = 0  # Reset error count on success

                # Sleep for the specified interval
                for _ in range(self.check_interval):
                    if not self.running:
                        break
                    time.sleep(1)  # Sleep in 1-second intervals to allow quick shutdown

            except Exception as e:
                consecutive_errors += 1
                print(f"Error in notification monitoring loop (#{consecutive_errors}): {e}")

                if consecutive_errors >= max_consecutive_errors:
                    print(f"Too many consecutive errors ({consecutive_errors}), stopping monitoring")
                    break

                # Wait before retrying, but allow quick shutdown
                for _ in range(min(self.check_interval, 30)):  # Max 30 seconds wait on error
                    if not self.running:
                        break
                    time.sleep(1)

        print("Notification monitoring loop ended")
        self.running = False

    def test_notification(self):
        """Test desktop notification system"""
        try:
            self.show_desktop_notification(
                "🔔 Test Notification",
                "Desktop notifications are working correctly!"
            )
            self.play_notification_sound('default')
            return True
        except Exception as e:
            print(f"Test notification failed: {e}")
            return False

    def get_monitoring_status(self):
        """Get detailed monitoring status information"""
        return {
            'running': self.running,
            'monitoring_enabled': self.monitoring_enabled,
            'thread_alive': self.notification_thread.is_alive() if self.notification_thread else False,
            'last_check_time': self.last_check_time.strftime('%Y-%m-%d %H:%M:%S') if self.last_check_time else 'Never',
            'check_failures': self.check_failures,
            'max_check_failures': self.max_check_failures,
            'check_interval': self.check_interval,
            'desktop_notifications_enabled': self.desktop_notifications_enabled,
            'sound_alerts_enabled': self.sound_alerts_enabled,
            'reminder_minutes': self.reminder_minutes,
            'notifications_sent_today': len(self.sent_notifications)
        }

    def enable_monitoring(self):
        """Enable notification monitoring"""
        self.monitoring_enabled = True
        self.save_settings()
        if not self.is_monitoring_active():
            self.start_monitoring()

    def disable_monitoring(self):
        """Disable notification monitoring"""
        self.monitoring_enabled = False
        self.save_settings()
        if self.is_monitoring_active():
            self.stop_monitoring()

    def force_check_now(self):
        """Force an immediate check for task reminders"""
        try:
            print("Forcing immediate notification check...")
            self.check_task_reminders()
            return True
        except Exception as e:
            print(f"Force check failed: {e}")
            return False

# Global notification manager instance
notification_manager = NotificationManager()
