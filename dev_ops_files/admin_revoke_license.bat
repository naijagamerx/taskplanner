@echo off
title Task Planner - Admin License Revocation Tool
color 0C

echo.
echo =============================================
echo    Task Planner Admin License Revocation
echo =============================================
echo.

REM Get the current directory
set "APP_DIR=%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again.
    pause
    exit /b 1
)

echo This tool allows you to revoke licenses from the admin database.
echo.

REM Run Python script for admin license revocation
python -c "
import sys
import os
sys.path.append(r'%APP_DIR%')

try:
    from admin_dashboard import LicenseKeyGenerator
    
    # Initialize license generator
    generator = LicenseKeyGenerator()
    
    # Get all licenses
    licenses = generator.get_all_licenses()
    
    if not licenses:
        print('❌ No licenses found in admin database.')
        sys.exit(0)
    
    print(f'📋 Found {len(licenses)} licenses in database:')
    print()
    
    # Display licenses
    active_licenses = []
    for i, license_record in enumerate(licenses):
        status = license_record.get('status', 'unknown')
        if status == 'active':
            active_licenses.append((i, license_record))
            license_key = license_record.get('license_key', 'Unknown')
            user_name = license_record.get('user_name', 'Unknown')
            license_type = license_record.get('license_type', 'Unknown')
            issued_at = license_record.get('issued_at', '')[:10]
            
            print(f'   {len(active_licenses)}. {license_key}')
            print(f'      User: {user_name}')
            print(f'      Type: {license_type.title()}')
            print(f'      Issued: {issued_at}')
            print()
    
    if not active_licenses:
        print('❌ No active licenses found to revoke.')
        sys.exit(0)
    
    # Get user selection
    while True:
        try:
            choice = input(f'Enter license number to revoke (1-{len(active_licenses)}) or 0 to cancel: ')
            choice_num = int(choice)
            
            if choice_num == 0:
                print('❌ License revocation cancelled.')
                sys.exit(0)
            elif 1 <= choice_num <= len(active_licenses):
                selected_license = active_licenses[choice_num - 1][1]
                break
            else:
                print(f'❌ Please enter a number between 1 and {len(active_licenses)}')
        except ValueError:
            print('❌ Please enter a valid number')
    
    # Confirm revocation
    license_key = selected_license.get('license_key', 'Unknown')
    user_name = selected_license.get('user_name', 'Unknown')
    
    print()
    print(f'⚠️  You are about to revoke:')
    print(f'   License: {license_key}')
    print(f'   User: {user_name}')
    print()
    
    response = input('Are you sure you want to revoke this license? (y/N): ')
    if response.lower() not in ['y', 'yes']:
        print('❌ License revocation cancelled.')
        sys.exit(0)
    
    # Revoke the license
    if generator.revoke_license(license_key):
        print()
        print('✅ License successfully revoked in admin database!')
        print(f'   License {license_key} has been marked as revoked.')
        print('   The user will be prompted for a new license within 5 minutes.')
    else:
        print('❌ Failed to revoke license in admin database.')
        sys.exit(1)
        
except ImportError as e:
    print(f'❌ Error importing admin dashboard: {e}')
    print('   Make sure you are running this from the Task Planner directory.')
    sys.exit(1)
except Exception as e:
    print(f'❌ Error revoking license: {e}')
    sys.exit(1)
"

if errorlevel 1 (
    echo.
    echo ❌ Admin license revocation failed.
    pause
    exit /b 1
)

echo.
echo ✅ Admin license revocation completed successfully!
echo.
echo NOTE: The revoked license will be detected by the main application
echo       within 5 minutes and the user will be prompted to activate
echo       a new license.
echo.
pause
