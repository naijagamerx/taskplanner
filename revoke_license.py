#!/usr/bin/env python3
"""
License Revocation Script for Task Planner
Revokes the license on the current computer
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    try:
        from auth.license_manager import LicenseManager

        # Check for quick mode
        quick_mode = '--quick' in sys.argv

        if not quick_mode:
            print("Task Planner - License Revocation")
            print("=" * 40)
            print()

        # Initialize license manager
        license_manager = LicenseManager()

        # Check if there's a current license
        if not license_manager.current_license:
            print('❌ No license found on this computer.')
            if not quick_mode:
                print('   Nothing to revoke.')
            return 0

        # Get license info
        license_info = license_manager.get_license_info()
        license_key = license_info.get('license_key', 'Unknown')
        user_name = license_info.get('user_name', 'Unknown')
        license_type = license_info.get('license_type', 'Unknown')

        if not quick_mode:
            print(f'📋 Current License Information:')
            print(f'   License Key: {license_key}')
            print(f'   User: {user_name}')
            print(f'   Type: {license_type.title()}')
            print()

            # Confirm revocation
            response = input('⚠️  Are you sure you want to revoke this license? (y/N): ')
            if response.lower() not in ['y', 'yes']:
                print('❌ License revocation cancelled.')
                return 0

        # Revoke the license
        if license_manager.deactivate_license():
            if quick_mode:
                print(f'✅ License {license_key} successfully revoked!')
            else:
                print('✅ License successfully revoked!')
                print('   The license has been removed from this computer.')
                print('   You will need to activate a new license to use Task Planner.')
            return 0
        else:
            print('❌ Failed to revoke license.')
            if not quick_mode:
                print('   Please try again or contact support.')
            return 1

    except ImportError as e:
        print(f'❌ Error importing license manager: {e}')
        print('   Make sure you are running this from the Task Planner directory.')
        return 1
    except Exception as e:
        print(f'❌ Error revoking license: {e}')
        return 1

if __name__ == "__main__":
    exit_code = main()
    print()
    input("Press Enter to continue...")
    sys.exit(exit_code)
