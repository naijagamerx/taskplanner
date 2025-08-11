"""
Persistent Notification Service for Task Planner
Runs independently and ensures notifications work continuously
"""

import os
import sys
import threading
import time
import atexit
from datetime import datetime, timedelta
import signal

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.settings_manager import SettingsManager


class NotificationService:
    """Persistent notification service that runs independently"""
    
    def __init__(self):
        self.settings = SettingsManager()
        self.running = False
        self.service_thread = None
        self.notification_manager = None
        self.restart_count = 0
        self.max_restarts = 10
        self.last_restart_time = None
        self.restart_cooldown = 300  # 5 minutes
        
        # Register cleanup handlers
        atexit.register(self.cleanup)
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        
        # Initialize notification manager
        self.init_notification_manager()
    
    def init_notification_manager(self):
        """Initialize the notification manager"""
        try:
            from services.notification_manager import notification_manager
            self.notification_manager = notification_manager
            print("✅ Notification manager initialized")
        except Exception as e:
            print(f"❌ Failed to initialize notification manager: {e}")
            self.notification_manager = None
    
    def start_service(self):
        """Start the persistent notification service"""
        if self.running:
            print("⚠️ Notification service already running")
            return True
        
        try:
            # Check if service is enabled
            service_enabled = self.settings.get('notification_service_enabled', True)
            if not service_enabled:
                print("ℹ️ Notification service is disabled")
                return False
            
            self.running = True
            self.service_thread = threading.Thread(target=self._service_loop, daemon=False)
            self.service_thread.start()
            print("🚀 Notification service started")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start notification service: {e}")
            self.running = False
            return False
    
    def stop_service(self):
        """Stop the notification service"""
        print("🛑 Stopping notification service...")
        self.running = False
        
        if self.notification_manager:
            try:
                self.notification_manager.stop_monitoring()
            except Exception as e:
                print(f"⚠️ Error stopping notification manager: {e}")
        
        if self.service_thread and self.service_thread.is_alive():
            self.service_thread.join(timeout=5)
        
        print("✅ Notification service stopped")
    
    def restart_service(self):
        """Restart the notification service with cooldown protection"""
        now = datetime.now()
        
        # Check restart cooldown
        if (self.last_restart_time and 
            (now - self.last_restart_time).total_seconds() < self.restart_cooldown):
            print(f"⏳ Service restart on cooldown, waiting...")
            return False
        
        # Check restart limit
        if self.restart_count >= self.max_restarts:
            print(f"❌ Maximum restart attempts ({self.max_restarts}) reached")
            return False
        
        print(f"🔄 Restarting notification service (attempt {self.restart_count + 1})")
        
        self.stop_service()
        time.sleep(2)  # Brief pause
        
        success = self.start_service()
        if success:
            self.restart_count += 1
            self.last_restart_time = now
            print("✅ Notification service restarted successfully")
        else:
            print("❌ Failed to restart notification service")
        
        return success
    
    def _service_loop(self):
        """Main service loop with health monitoring"""
        print("🔄 Notification service loop started")
        health_check_interval = 30  # Check health every 30 seconds
        last_health_check = datetime.now()
        consecutive_failures = 0
        max_consecutive_failures = 5
        
        while self.running:
            try:
                current_time = datetime.now()
                
                # Perform health check
                if (current_time - last_health_check).total_seconds() >= health_check_interval:
                    if self.perform_health_check():
                        consecutive_failures = 0
                    else:
                        consecutive_failures += 1
                        print(f"⚠️ Health check failed ({consecutive_failures}/{max_consecutive_failures})")
                        
                        if consecutive_failures >= max_consecutive_failures:
                            print("❌ Too many health check failures, restarting service")
                            self.restart_service()
                            break
                    
                    last_health_check = current_time
                
                # Ensure notification manager is running
                if self.notification_manager and not self.notification_manager.is_monitoring_active():
                    print("🔧 Notification manager not active, restarting...")
                    try:
                        self.notification_manager.restart_monitoring()
                    except Exception as e:
                        print(f"⚠️ Failed to restart notification manager: {e}")
                
                # Sleep in small intervals to allow quick shutdown
                for _ in range(10):  # 10 seconds total
                    if not self.running:
                        break
                    time.sleep(1)
                
            except Exception as e:
                print(f"❌ Error in service loop: {e}")
                consecutive_failures += 1
                
                if consecutive_failures >= max_consecutive_failures:
                    print("❌ Too many service loop errors, stopping service")
                    break
                
                time.sleep(5)  # Wait before retrying
        
        print("🏁 Notification service loop ended")
        self.running = False
    
    def perform_health_check(self):
        """Perform health check on notification system"""
        try:
            # Check if notification manager exists and is responsive
            if not self.notification_manager:
                print("⚠️ Health check: Notification manager not available")
                return False
            
            # Check if monitoring is active
            if not self.notification_manager.is_monitoring_active():
                print("⚠️ Health check: Notification monitoring not active")
                return False
            
            # Check database connectivity
            from database.db_manager import db_manager
            if not db_manager.test_connection():
                print("⚠️ Health check: Database connection failed")
                return False
            
            # Check if settings are accessible
            test_setting = self.settings.get('notification_service_enabled', True)
            if test_setting is None:
                print("⚠️ Health check: Settings not accessible")
                return False
            
            return True
            
        except Exception as e:
            print(f"⚠️ Health check error: {e}")
            return False
    
    def is_service_running(self):
        """Check if service is currently running"""
        return self.running and self.service_thread and self.service_thread.is_alive()
    
    def get_service_status(self):
        """Get detailed service status"""
        return {
            'running': self.running,
            'thread_alive': self.service_thread.is_alive() if self.service_thread else False,
            'restart_count': self.restart_count,
            'max_restarts': self.max_restarts,
            'last_restart_time': self.last_restart_time.strftime('%Y-%m-%d %H:%M:%S') if self.last_restart_time else 'Never',
            'notification_manager_active': self.notification_manager.is_monitoring_active() if self.notification_manager else False
        }
    
    def signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown"""
        print(f"📡 Received signal {signum}, shutting down service...")
        self.stop_service()
        sys.exit(0)
    
    def cleanup(self):
        """Cleanup when service is terminated"""
        if self.running:
            self.stop_service()


# Global service instance
notification_service = NotificationService()


def start_notification_service():
    """Start the notification service"""
    return notification_service.start_service()


def stop_notification_service():
    """Stop the notification service"""
    notification_service.stop_service()


def get_service_status():
    """Get service status"""
    return notification_service.get_service_status()


if __name__ == "__main__":
    # Run as standalone service
    print("🚀 Starting Task Planner Notification Service...")
    
    try:
        if start_notification_service():
            print("✅ Service started successfully")
            
            # Keep service running
            while notification_service.is_service_running():
                time.sleep(1)
        else:
            print("❌ Failed to start service")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Service interrupted by user")
    except Exception as e:
        print(f"❌ Service error: {e}")
    finally:
        stop_notification_service()
        print("👋 Service shutdown complete")
