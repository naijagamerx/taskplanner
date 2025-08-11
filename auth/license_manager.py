"""
License Manager for Task Planner
Handles license validation, activation, and management
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
from .hardware_fingerprint import get_hardware_id, get_hardware_info
from .crypto_utils import SecureStorage, LicenseCrypto


class LicenseManager:
    """Manage application licensing"""

    def __init__(self):
        self.hardware_id = get_hardware_id()
        self.storage = SecureStorage("TaskPlanner")
        self.crypto = LicenseCrypto()
        self.current_license = None
        self._load_license()

    def _load_license(self):
        """Load current license from storage"""
        try:
            self.current_license = self.storage.load_license(self.hardware_id)
        except Exception as e:
            print(f"Error loading license: {e}")
            self.current_license = None

    def _get_appdata_license_db_path(self) -> str:
        """Get the path for license database in AppData directory"""
        import sys

        if sys.platform == "win32":
            # Windows: %APPDATA%/TaskPlanner/license_database.json
            app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
            app_dir = os.path.join(app_data, 'TaskPlanner')
        elif sys.platform == "darwin":
            # macOS: ~/Library/Application Support/TaskPlanner/license_database.json
            app_dir = os.path.expanduser('~/Library/Application Support/TaskPlanner')
        else:
            # Linux: ~/.config/TaskPlanner/license_database.json
            config_dir = os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
            app_dir = os.path.join(config_dir, 'TaskPlanner')

        return os.path.join(app_dir, 'license_database.json')

    def is_license_valid(self) -> bool:
        """Check if current license is valid"""
        if not self.current_license:
            return False

        try:
            # Check hardware binding
            if self.current_license.get('hardware_id') != self.hardware_id:
                return False

            # Check expiration
            expires_at = self.current_license.get('expires_at')
            if expires_at:
                expiry_date = datetime.fromisoformat(expires_at)
                if datetime.now() > expiry_date:
                    # Mark expired license as inactive
                    self.current_license['status'] = 'expired'
                    return False

            # Check license status
            status = self.current_license.get('status', 'active')
            if status != 'active':
                return False

            # Check server-side license status (for revoked licenses)
            if not self._validate_license_server_side():
                return False

            return True

        except Exception as e:
            print(f"Error validating license: {e}")
            return False

    def get_license_info(self) -> Dict[str, Any]:
        """Get current license information"""
        if not self.current_license:
            return {
                'status': 'no_license',
                'hardware_id': self.hardware_id,
                'message': 'No license found'
            }

        try:
            # For non-trial licenses, try to get updated info from admin database
            license_key = self.current_license.get('license_key', '')
            if self.current_license.get('license_type') != 'trial' and license_key:
                updated_license = self._get_license_from_admin_db(license_key)
                if updated_license:
                    # Update current license with admin database info (especially expires_at)
                    self.current_license['expires_at'] = updated_license.get('expires_at')
                    self.current_license['status'] = updated_license.get('status', 'active')

            info = {
                'status': 'valid' if self.is_license_valid() else 'invalid',
                'license_key': self.current_license.get('license_key', 'Unknown'),
                'user_name': self.current_license.get('user_name', 'Unknown'),
                'license_type': self.current_license.get('license_type', 'Unknown'),
                'issued_at': self.current_license.get('issued_at', 'Unknown'),
                'expires_at': self.current_license.get('expires_at', 'Never'),
                'hardware_id': self.hardware_id
            }

            # Calculate days remaining
            expires_at = self.current_license.get('expires_at')
            if expires_at:
                try:
                    expiry_date = datetime.fromisoformat(expires_at)
                    days_remaining = (expiry_date - datetime.now()).days
                    info['days_remaining'] = max(0, days_remaining)
                except:
                    info['days_remaining'] = 0
            else:
                info['days_remaining'] = -1  # Unlimited

            return info

        except Exception as e:
            return {
                'status': 'error',
                'hardware_id': self.hardware_id,
                'message': f'Error reading license: {e}'
            }

    def activate_license(self, license_key: str, user_name: str = "") -> Tuple[bool, str]:
        """Activate license with provided key"""
        try:
            # Validate license key format
            if not self._validate_license_key_format(license_key):
                return False, "Invalid license key format"

            # For this implementation, we'll decode the license from the key
            # In a real system, this would involve server communication
            license_data = self._decode_license_from_key(license_key, user_name)

            if not license_data:
                return False, "Invalid license key"

            # Verify hardware binding
            if license_data.get('hardware_id') != self.hardware_id:
                return False, "License key is not valid for this machine"

            # Save license
            if self.storage.save_license(license_data, self.hardware_id):
                self.current_license = license_data
                return True, "License activated successfully"
            else:
                return False, "Failed to save license"

        except Exception as e:
            return False, f"Activation failed: {e}"

    def _validate_license_key_format(self, license_key: str) -> bool:
        """Validate license key format (XXXX-XXXX-XXXX-XXXX)"""
        if not license_key:
            return False

        # Remove spaces and convert to uppercase
        key = license_key.replace(' ', '').upper()

        # Check format
        if len(key) != 19:  # 16 chars + 3 dashes
            return False

        parts = key.split('-')
        if len(parts) != 4:
            return False

        for part in parts:
            if len(part) != 4 or not part.isalnum():
                return False

        return True

    def _get_license_from_admin_db(self, license_key: str) -> Optional[Dict[str, Any]]:
        """Get license information from admin database"""
        try:
            # Try multiple possible locations for the admin database
            admin_db_file = None
            possible_paths = [
                self._get_appdata_license_db_path(),  # AppData directory (primary)
                "license_database.json",  # Current directory (fallback)
                os.path.join(os.path.dirname(os.path.dirname(__file__)), "license_database.json"),  # Project root
                os.path.join(os.getcwd(), "license_database.json")  # Working directory
            ]

            for path in possible_paths:
                if os.path.exists(path):
                    admin_db_file = path
                    break

            if not admin_db_file:
                return None

            with open(admin_db_file, 'r') as f:
                admin_data = json.load(f)

            # Find license in admin database
            for record in admin_data.get('licenses', []):
                if record.get('license_key') == license_key.upper():
                    return record

            return None

        except Exception:
            return None

    def _decode_license_from_key(self, license_key: str, user_name: str) -> Optional[Dict[str, Any]]:
        """Decode license data from license key using admin database"""
        try:
            # Load admin database to verify license
            # Try multiple possible locations for the admin database
            admin_db_file = None
            possible_paths = [
                self._get_appdata_license_db_path(),  # AppData directory (primary)
                "license_database.json",  # Current directory (fallback)
                os.path.join(os.path.dirname(os.path.dirname(__file__)), "license_database.json"),  # Project root
                os.path.join(os.getcwd(), "license_database.json")  # Working directory
            ]

            for path in possible_paths:
                if os.path.exists(path):
                    admin_db_file = path
                    break

            if not admin_db_file:
                # Fallback to demo mode if no admin database found
                return self._decode_license_demo_mode(license_key, user_name)

            with open(admin_db_file, 'r') as f:
                admin_data = json.load(f)

            # Find license in admin database
            license_record = None
            for record in admin_data.get('licenses', []):
                if record.get('license_key') == license_key.upper():
                    license_record = record
                    break

            if not license_record:
                # Fallback to demo mode if license not found in admin database
                return self._decode_license_demo_mode(license_key, user_name)

            # Check if license is revoked
            if license_record.get('status') == 'revoked':
                return None

            # Extract license information from the admin record
            license_type = license_record.get('license_type', 'basic')

            # Use the expiration date from admin database
            # This respects the duration set by admin when generating the license
            expires_at = license_record.get('expires_at')

            license_data = {
                'license_key': license_key.upper(),
                'user_name': user_name or license_record.get('user_name', 'Licensed User'),
                'license_type': license_type,
                'hardware_id': self.hardware_id,
                'issued_at': license_record.get('issued_at', datetime.now().isoformat()),
                'expires_at': expires_at,
                'status': 'active',
                'features': self._get_license_features(license_type)
            }

            return license_data

        except Exception as e:
            print(f"Error decoding license: {e}")
            # Fallback to demo mode on error
            return self._decode_license_demo_mode(license_key, user_name)

    def _decode_license_demo_mode(self, license_key: str, user_name: str) -> Optional[Dict[str, Any]]:
        """Fallback demo mode for license decoding"""
        try:
            # Clean license key
            clean_key = license_key.replace('-', '').upper()

            # Determine license type based on key pattern
            license_type = "professional"
            if clean_key.startswith('TRIAL'):
                license_type = "trial"
            elif clean_key.startswith('BASIC'):
                license_type = "basic"
            elif clean_key.startswith('PRO'):
                license_type = "professional"
            elif clean_key.startswith('ENT'):
                license_type = "enterprise"

            # Set expiration based on license type
            issued_at = datetime.now()
            if license_type == "trial":
                expires_at = issued_at + timedelta(days=30)
            elif license_type == "basic":
                expires_at = issued_at + timedelta(days=365)
            else:
                expires_at = None  # Unlimited for pro/enterprise

            license_data = {
                'license_key': license_key.upper(),
                'user_name': user_name or "Licensed User",
                'license_type': license_type,
                'hardware_id': self.hardware_id,
                'issued_at': issued_at.isoformat(),
                'expires_at': expires_at.isoformat() if expires_at else None,
                'status': 'active',
                'features': self._get_license_features(license_type)
            }

            return license_data

        except Exception as e:
            print(f"Error in demo mode license decoding: {e}")
            return None

    def _get_license_features(self, license_type: str) -> Dict[str, bool]:
        """Get features available for license type"""
        features = {
            'basic_tasks': True,
            'categories': True,
            'calendar': True,
            'notifications': True,
            'analytics': False,
            'export': False,
            'backup': False,
            'themes': False,
            'advanced_search': False,
            'templates': False
        }

        if license_type in ['professional', 'enterprise']:
            features.update({
                'analytics': True,
                'export': True,
                'backup': True,
                'themes': True,
                'advanced_search': True,
                'templates': True
            })
        elif license_type == 'basic':
            features.update({
                'export': True,
                'backup': True
            })

        return features

    def deactivate_license(self) -> bool:
        """Deactivate current license"""
        try:
            if self.storage.delete_license():
                self.current_license = None
                return True
            return False
        except Exception as e:
            print(f"Error deactivating license: {e}")
            return False

    def get_hardware_id(self) -> str:
        """Get hardware ID for this machine"""
        return self.hardware_id

    def get_hardware_info(self) -> Dict[str, Any]:
        """Get detailed hardware information"""
        return get_hardware_info()

    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a specific feature is enabled"""
        if not self.is_license_valid():
            # Allow basic features without license
            basic_features = ['basic_tasks', 'categories', 'calendar', 'notifications']
            return feature in basic_features

        features = self.current_license.get('features', {})
        return features.get(feature, False)

    def get_trial_info(self) -> Dict[str, Any]:
        """Get trial license information"""
        return {
            'available': True,
            'duration_days': 30,
            'features': self._get_license_features('trial')
        }

    def start_trial(self, user_name: str = "Trial User") -> Tuple[bool, str]:
        """Start trial license"""
        try:
            # Check if trial already used and still valid
            if self.current_license and self.current_license.get('license_type') == 'trial':
                if self.is_license_valid():
                    return False, "Trial already active on this machine"
                else:
                    return False, "Trial period has expired on this machine"

            # Create trial license directly (no admin database needed)
            from datetime import datetime, timedelta

            issued_at = datetime.now()
            expires_at = issued_at + timedelta(days=30)

            trial_license = {
                'license_key': f"TRIAL-{self.hardware_id[:4]}-{self.hardware_id[4:8]}-{self.hardware_id[8:12]}",
                'user_name': user_name,
                'license_type': 'trial',
                'hardware_id': self.hardware_id,
                'issued_at': issued_at.isoformat(),
                'expires_at': expires_at.isoformat(),
                'status': 'active',
                'features': self._get_license_features('trial')
            }

            # Save trial license
            if self.storage.save_license(trial_license, self.hardware_id):
                self.current_license = trial_license
                return True, "Trial license activated successfully"
            else:
                return False, "Failed to save trial license"

        except Exception as e:
            return False, f"Failed to start trial: {e}"

    def _validate_license_server_side(self) -> bool:
        """Validate license against admin database (check for revoked status)"""
        try:
            # Skip server-side validation for trial licenses
            if self.current_license.get('license_type') == 'trial':
                return True

            import json
            import os

            # Path to admin license database
            admin_db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "license_database.json")

            if not os.path.exists(admin_db_path):
                # If admin database doesn't exist, assume license is valid
                return True

            # Load admin database
            with open(admin_db_path, 'r') as f:
                admin_data = json.load(f)

            # Find our license in admin database
            license_key = self.current_license.get('license_key', '')
            for license_record in admin_data.get('licenses', []):
                if license_record.get('license_key') == license_key:
                    # Check if license is revoked in admin database
                    if license_record.get('status') == 'revoked':
                        print(f"License {license_key} has been revoked")
                        return False
                    break

            return True

        except Exception as e:
            print(f"Error validating license server-side: {e}")
            # If we can't validate, assume license is valid to avoid breaking the app
            return True


if __name__ == "__main__":
    # Test the license manager
    print("License Manager Test")
    print("=" * 40)

    manager = LicenseManager()

    print(f"Hardware ID: {manager.get_hardware_id()}")
    print(f"License valid: {manager.is_license_valid()}")

    license_info = manager.get_license_info()
    print(f"License info: {license_info}")

    # Test trial activation
    print("\nTesting trial activation...")
    success, message = manager.start_trial("Test User")
    print(f"Trial activation: {success} - {message}")

    if success:
        print(f"License valid after trial: {manager.is_license_valid()}")
        print(f"License info: {manager.get_license_info()}")
