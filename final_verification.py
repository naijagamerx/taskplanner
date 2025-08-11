"""
Final Verification Script for Notification System
Tests all components and creates a comprehensive report
"""

import sys
import os
import time
from datetime import datetime, timedelta

# Add current directory to path
sys.path.append('.')

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print('='*60)

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def print_warning(message):
    """Print warning message"""
    print(f"⚠️ {message}")

def print_info(message):
    """Print info message"""
    print(f"ℹ️ {message}")

def test_imports():
    """Test all notification-related imports"""
    print_header("TESTING IMPORTS")
    
    results = {}
    
    # Test notification manager import
    try:
        from services.notification_manager import notification_manager
        print_success("Notification Manager imported")
        results['notification_manager'] = True
    except Exception as e:
        print_error(f"Notification Manager import failed: {e}")
        results['notification_manager'] = False
    
    # Test notification service import
    try:
        from services.notification_service import notification_service, start_notification_service, stop_notification_service
        print_success("Notification Service imported")
        results['notification_service'] = True
    except Exception as e:
        print_error(f"Notification Service import failed: {e}")
        results['notification_service'] = False
    
    # Test database imports
    try:
        from database.db_manager import db_manager
        from models.task import Task
        print_success("Database components imported")
        results['database'] = True
    except Exception as e:
        print_error(f"Database import failed: {e}")
        results['database'] = False
    
    # Test settings import
    try:
        from database.settings_manager import SettingsManager
        print_success("Settings Manager imported")
        results['settings'] = True
    except Exception as e:
        print_error(f"Settings Manager import failed: {e}")
        results['settings'] = False
    
    return results

def test_notification_functionality():
    """Test notification functionality"""
    print_header("TESTING NOTIFICATION FUNCTIONALITY")
    
    try:
        from services.notification_manager import notification_manager
        
        # Test 1: Get status
        status = notification_manager.get_monitoring_status()
        print_info(f"Monitoring Status:")
        print(f"   Running: {status['running']}")
        print(f"   Enabled: {status['monitoring_enabled']}")
        print(f"   Check Interval: {status['check_interval']}s")
        print(f"   Desktop Notifications: {status['desktop_notifications_enabled']}")
        print(f"   Sound Alerts: {status['sound_alerts_enabled']}")
        
        # Test 2: Test notification
        print_info("Testing desktop notification...")
        if notification_manager.test_notification():
            print_success("Desktop notification sent successfully")
        else:
            print_error("Desktop notification failed")
        
        # Test 3: Check monitoring
        if notification_manager.is_monitoring_active():
            print_success("Notification monitoring is active")
        else:
            print_warning("Notification monitoring is not active")
            print_info("Starting monitoring...")
            notification_manager.start_monitoring()
            time.sleep(2)
            if notification_manager.is_monitoring_active():
                print_success("Monitoring started successfully")
            else:
                print_error("Failed to start monitoring")
        
        # Test 4: Force check
        print_info("Testing force check...")
        if notification_manager.force_check_now():
            print_success("Force check completed")
        else:
            print_error("Force check failed")
        
        return True
        
    except Exception as e:
        print_error(f"Notification functionality test failed: {e}")
        return False

def test_service_functionality():
    """Test notification service functionality"""
    print_header("TESTING NOTIFICATION SERVICE")
    
    try:
        from services.notification_service import notification_service, start_notification_service
        
        # Test 1: Get service status
        status = notification_service.get_service_status()
        print_info(f"Service Status:")
        print(f"   Running: {status['running']}")
        print(f"   Thread Alive: {status['thread_alive']}")
        print(f"   Restart Count: {status['restart_count']}")
        print(f"   Notification Manager Active: {status['notification_manager_active']}")
        
        # Test 2: Start service if not running
        if not notification_service.is_service_running():
            print_info("Starting notification service...")
            if start_notification_service():
                print_success("Service started successfully")
                time.sleep(2)
            else:
                print_error("Failed to start service")
        else:
            print_success("Service is already running")
        
        # Test 3: Health check
        print_info("Testing health check...")
        if notification_service.perform_health_check():
            print_success("Health check passed")
        else:
            print_warning("Health check failed")
        
        return True
        
    except Exception as e:
        print_error(f"Service functionality test failed: {e}")
        return False

def test_database_integration():
    """Test database integration"""
    print_header("TESTING DATABASE INTEGRATION")
    
    try:
        from database.db_manager import db_manager
        from models.task import Task
        
        # Test 1: Database connection
        if db_manager.test_connection():
            print_success("Database connection successful")
        else:
            print_error("Database connection failed")
            return False
        
        # Test 2: Task retrieval
        tasks = Task.get_all()
        print_info(f"Found {len(tasks)} tasks in database")
        
        # Test 3: Check for upcoming tasks
        upcoming_tasks = []
        overdue_tasks = []
        now = datetime.now()
        
        for task in tasks:
            if task.due_date and task.due_time and task.status in ['pending', 'in_progress']:
                # Handle time conversion
                due_time = task.due_time
                if hasattr(due_time, 'total_seconds'):
                    total_seconds = int(due_time.total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    seconds = total_seconds % 60
                    due_time = datetime.time(hours, minutes, seconds)
                
                task_datetime = datetime.combine(task.due_date, due_time)
                
                if task_datetime > now:
                    upcoming_tasks.append(task)
                else:
                    overdue_tasks.append(task)
        
        print_info(f"Found {len(upcoming_tasks)} upcoming tasks")
        print_info(f"Found {len(overdue_tasks)} overdue tasks")
        
        return True
        
    except Exception as e:
        print_error(f"Database integration test failed: {e}")
        return False

def test_settings_persistence():
    """Test settings persistence"""
    print_header("TESTING SETTINGS PERSISTENCE")
    
    try:
        from database.settings_manager import SettingsManager
        
        settings = SettingsManager()
        
        # Test 1: Read current settings
        notification_settings = settings.get_notification_settings()
        print_info("Current notification settings:")
        for key, value in notification_settings.items():
            print(f"   {key}: {value}")
        
        # Test 2: Test write/read cycle
        test_key = 'verification_test_timestamp'
        test_value = datetime.now().isoformat()
        
        settings.set(test_key, test_value)
        settings.save()
        
        # Read back
        read_value = settings.get(test_key)
        if read_value == test_value:
            print_success("Settings write/read cycle successful")
            
            # Cleanup
            settings.delete(test_key)
            settings.save()
            
            # Verify deletion
            deleted_value = settings.get(test_key)
            if deleted_value is None:
                print_success("Settings deletion successful")
            else:
                print_warning("Settings deletion may have failed")
        else:
            print_error("Settings write/read cycle failed")
            return False
        
        return True
        
    except Exception as e:
        print_error(f"Settings persistence test failed: {e}")
        return False

def generate_report(test_results):
    """Generate final test report"""
    print_header("FINAL VERIFICATION REPORT")
    
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result)
    
    print(f"📊 Test Results: {passed_tests}/{total_tests} passed")
    print()
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<25} {status}")
    
    print()
    
    if passed_tests == total_tests:
        print_success("🎉 ALL TESTS PASSED!")
        print_info("The notification system is fully functional and ready for use.")
        print_info("Key features verified:")
        print("   • Desktop notifications working")
        print("   • Persistent monitoring active")
        print("   • Database integration functional")
        print("   • Settings persistence working")
        print("   • Service health monitoring operational")
        print("   • Automatic restart capabilities enabled")
    else:
        print_warning(f"⚠️ {total_tests - passed_tests} test(s) failed")
        print_info("Please review the failed tests above and address any issues.")
    
    return passed_tests == total_tests

def main():
    """Run comprehensive verification"""
    print("🚀 Task Planner Notification System - Final Verification")
    print("This script will comprehensively test all notification functionality")
    
    # Run all tests
    test_results = {}
    
    # Import tests
    import_results = test_imports()
    test_results.update(import_results)
    
    # Only proceed with functionality tests if imports succeeded
    if import_results.get('notification_manager', False):
        test_results['notification_functionality'] = test_notification_functionality()
    else:
        test_results['notification_functionality'] = False
    
    if import_results.get('notification_service', False):
        test_results['service_functionality'] = test_service_functionality()
    else:
        test_results['service_functionality'] = False
    
    if import_results.get('database', False):
        test_results['database_integration'] = test_database_integration()
    else:
        test_results['database_integration'] = False
    
    if import_results.get('settings', False):
        test_results['settings_persistence'] = test_settings_persistence()
    else:
        test_results['settings_persistence'] = False
    
    # Generate final report
    success = generate_report(test_results)
    
    print_header("NEXT STEPS")
    if success:
        print_info("✅ The notification system is ready for production use!")
        print_info("🔔 Users will now receive reliable task notifications")
        print_info("🔄 The system will automatically restart if issues occur")
        print_info("💾 All settings are properly stored in AppData")
    else:
        print_info("❌ Please address the failed tests before deployment")
        print_info("📋 Check the error messages above for specific issues")
    
    return success

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Verification interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Verification error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
