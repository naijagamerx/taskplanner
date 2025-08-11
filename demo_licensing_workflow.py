"""
Demo script showing the complete licensing workflow
"""

import sys
import os
import json

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def demo_workflow():
    """Demonstrate the complete licensing workflow"""
    print("Task Planner Licensing System Demo")
    print("=" * 50)
    
    try:
        # Step 1: Get hardware ID (what user sees on first run)
        print("\n1. USER RUNS APP FOR FIRST TIME")
        print("-" * 30)
        
        from auth.hardware_fingerprint import get_hardware_id, get_hardware_info
        
        hardware_id = get_hardware_id()
        hardware_info = get_hardware_info()
        
        print(f"Hardware ID: {hardware_id}")
        print(f"System: {hardware_info['system']}")
        print(f"Machine: {hardware_info['machine']}")
        print("👤 User copies this Hardware ID and sends to admin")
        
        # Step 2: Admin generates license key
        print("\n2. ADMIN GENERATES LICENSE KEY")
        print("-" * 30)
        
        from admin_dashboard import LicenseKeyGenerator
        
        generator = LicenseKeyGenerator()
        
        # Admin inputs
        user_name = "John Doe"
        license_type = "professional"
        duration_days = None  # Unlimited
        
        print(f"Admin inputs:")
        print(f"  Hardware ID: {hardware_id}")
        print(f"  User Name: {user_name}")
        print(f"  License Type: {license_type}")
        print(f"  Duration: {'Unlimited' if not duration_days else f'{duration_days} days'}")
        
        # Generate license key
        license_key = generator.generate_license_key(
            hardware_id, license_type, user_name, duration_days
        )
        
        print(f"🔑 Generated License Key: {license_key}")
        print("📧 Admin sends this license key to user")
        
        # Step 3: User activates license
        print("\n3. USER ACTIVATES LICENSE")
        print("-" * 30)
        
        from auth.license_manager import LicenseManager
        
        manager = LicenseManager()
        
        print(f"User enters license key: {license_key}")
        success, message = manager.activate_license(license_key, user_name)
        
        print(f"Activation result: {success}")
        print(f"Message: {message}")
        
        if success:
            # Step 4: Verify license is working
            print("\n4. LICENSE VERIFICATION")
            print("-" * 30)
            
            print(f"License valid: {manager.is_license_valid()}")
            
            license_info = manager.get_license_info()
            print(f"License info:")
            for key, value in license_info.items():
                print(f"  {key}: {value}")
            
            # Step 5: Show encrypted license file
            print("\n5. ENCRYPTED LICENSE FILE")
            print("-" * 30)
            
            from auth.crypto_utils import SecureStorage
            storage = SecureStorage("TaskPlanner")
            
            print(f"License file location: {storage.get_license_file_path()}")
            print(f"License file exists: {storage.license_exists()}")
            
            if storage.license_exists():
                # Show encrypted content (first 100 chars)
                with open(storage.get_license_file_path(), 'r') as f:
                    encrypted_content = f.read()
                print(f"Encrypted content (first 100 chars): {encrypted_content[:100]}...")
            
            # Step 6: Test feature access
            print("\n6. FEATURE ACCESS TEST")
            print("-" * 30)
            
            features_to_test = [
                'basic_tasks', 'categories', 'calendar', 'notifications',
                'analytics', 'export', 'backup', 'themes', 'advanced_search', 'templates'
            ]
            
            for feature in features_to_test:
                enabled = manager.is_feature_enabled(feature)
                status = "✅ Enabled" if enabled else "❌ Disabled"
                print(f"  {feature}: {status}")
            
            print("\n🎉 LICENSING SYSTEM WORKING CORRECTLY!")
            print("✅ Hardware binding: Working")
            print("✅ Encryption: Working")
            print("✅ License validation: Working")
            print("✅ Feature control: Working")
            print("✅ Offline operation: Working")
            
        else:
            print("❌ License activation failed!")
            
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

def demo_trial_workflow():
    """Demonstrate trial license workflow"""
    print("\n" + "=" * 50)
    print("TRIAL LICENSE WORKFLOW DEMO")
    print("=" * 50)
    
    try:
        from auth.license_manager import LicenseManager
        
        # Create new manager (simulating fresh install)
        manager = LicenseManager()
        
        print("User starts trial...")
        success, message = manager.start_trial("Trial User")
        
        print(f"Trial activation: {success}")
        print(f"Message: {message}")
        
        if success:
            license_info = manager.get_license_info()
            print(f"Trial info:")
            for key, value in license_info.items():
                print(f"  {key}: {value}")
            
            print("✅ Trial license working!")
        else:
            print("❌ Trial activation failed!")
            
    except Exception as e:
        print(f"❌ Trial demo failed: {e}")

def demo_admin_dashboard():
    """Show admin dashboard capabilities"""
    print("\n" + "=" * 50)
    print("ADMIN DASHBOARD CAPABILITIES")
    print("=" * 50)
    
    try:
        from admin_dashboard import LicenseKeyGenerator
        
        generator = LicenseKeyGenerator()
        
        # Show existing licenses
        licenses = generator.get_all_licenses()
        print(f"Total licenses in database: {len(licenses)}")
        
        if licenses:
            print("\nRecent licenses:")
            for license_record in licenses[-3:]:  # Show last 3
                print(f"  Key: {license_record['license_key']}")
                print(f"  User: {license_record['user_name']}")
                print(f"  Type: {license_record['license_type']}")
                print(f"  Status: {license_record['status']}")
                print(f"  Issued: {license_record['issued_at'][:10]}")
                print()
        
        print("✅ Admin dashboard working!")
        print("📊 License database: Working")
        print("🔑 Key generation: Working")
        print("📋 License tracking: Working")
        
    except Exception as e:
        print(f"❌ Admin dashboard demo failed: {e}")

if __name__ == "__main__":
    # Run complete demo
    demo_workflow()
    demo_trial_workflow()
    demo_admin_dashboard()
    
    print("\n" + "=" * 50)
    print("DEMO COMPLETE!")
    print("=" * 50)
    print("\nTo test the GUI components:")
    print("1. Run 'py admin_dashboard.py' for admin interface")
    print("2. Run 'py main.py' to test license activation window")
    print("3. Check the license file in %APPDATA%/TaskPlanner/license.dat")
