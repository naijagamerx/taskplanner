"""
Cryptographic utilities for license encryption and validation
"""

import json
import base64
import hashlib
import os
from typing import Dict, Any, Optional

# Simple encryption using base64 and XOR (for demo purposes)
# In production, use proper cryptography libraries


class LicenseCrypto:
    """Handle encryption and decryption of license data"""

    def __init__(self, master_key: Optional[str] = None):
        """Initialize with master key or generate one"""
        if master_key:
            self.master_key = master_key.encode()
        else:
            # Use a combination of application-specific data as master key
            app_data = "TaskPlanner_License_System_v1.0"
            self.master_key = app_data.encode()

    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """Derive encryption key from password and salt (simplified)"""
        # Simple key derivation for demo purposes
        combined = password.encode() + salt
        key_hash = hashlib.sha256(combined).digest()
        return base64.urlsafe_b64encode(key_hash)

    def encrypt_license_data(self, license_data: Dict[str, Any], hardware_id: str) -> str:
        """Encrypt license data with hardware binding (simplified XOR)"""
        try:
            # Add hardware binding to license data
            license_data['hardware_id'] = hardware_id

            # Convert to JSON
            json_data = json.dumps(license_data, indent=2)

            # Simple XOR encryption with hardware ID as key
            key = hashlib.sha256(hardware_id.encode()).digest()
            encrypted_bytes = bytearray()

            for i, byte in enumerate(json_data.encode()):
                encrypted_bytes.append(byte ^ key[i % len(key)])

            # Return base64 encoded encrypted data
            return base64.b64encode(encrypted_bytes).decode()

        except Exception as e:
            raise Exception(f"Failed to encrypt license data: {e}")

    def decrypt_license_data(self, encrypted_data: str, hardware_id: str) -> Dict[str, Any]:
        """Decrypt license data and verify hardware binding (simplified XOR)"""
        try:
            # Decode base64
            encrypted_bytes = base64.b64decode(encrypted_data.encode())

            # Simple XOR decryption with hardware ID as key
            key = hashlib.sha256(hardware_id.encode()).digest()
            decrypted_bytes = bytearray()

            for i, byte in enumerate(encrypted_bytes):
                decrypted_bytes.append(byte ^ key[i % len(key)])

            # Parse JSON
            license_data = json.loads(decrypted_bytes.decode())

            # Verify hardware binding
            if license_data.get('hardware_id') != hardware_id:
                raise Exception("Hardware ID mismatch - license not valid for this machine")

            return license_data

        except Exception as e:
            raise Exception(f"Failed to decrypt license data: {e}")

    def generate_license_key(self, license_data: Dict[str, Any]) -> str:
        """Generate a license key from license data"""
        try:
            # Create a hash of the license data
            license_string = json.dumps(license_data, sort_keys=True)
            license_hash = hashlib.sha256(license_string.encode()).hexdigest()

            # Format as license key (XXXX-XXXX-XXXX-XXXX)
            key_parts = [license_hash[i:i+4].upper() for i in range(0, 16, 4)]
            return '-'.join(key_parts)

        except Exception as e:
            raise Exception(f"Failed to generate license key: {e}")

    def validate_license_key(self, license_key: str, license_data: Dict[str, Any]) -> bool:
        """Validate that license key matches license data"""
        try:
            expected_key = self.generate_license_key(license_data)
            return license_key.upper() == expected_key.upper()
        except:
            return False


class SecureStorage:
    """Secure storage for license files in AppData"""

    def __init__(self, app_name: str = "TaskPlanner"):
        self.app_name = app_name
        self.app_data_dir = self._get_app_data_dir()
        self.license_file = os.path.join(self.app_data_dir, "license.dat")
        self.crypto = LicenseCrypto()

    def _get_app_data_dir(self) -> str:
        """Get application data directory"""
        if os.name == 'nt':  # Windows
            app_data = os.environ.get('APPDATA')
            if not app_data:
                app_data = os.path.expanduser('~\\AppData\\Roaming')
        else:  # Linux/Mac
            app_data = os.path.expanduser('~/.config')

        app_dir = os.path.join(app_data, self.app_name)
        os.makedirs(app_dir, exist_ok=True)
        return app_dir

    def save_license(self, license_data: Dict[str, Any], hardware_id: str) -> bool:
        """Save encrypted license to AppData"""
        try:
            encrypted_data = self.crypto.encrypt_license_data(license_data, hardware_id)

            with open(self.license_file, 'w') as f:
                f.write(encrypted_data)

            # Set file permissions (read-only for user)
            if os.name != 'nt':  # Unix-like systems
                os.chmod(self.license_file, 0o600)

            return True

        except Exception as e:
            print(f"Error saving license: {e}")
            return False

    def load_license(self, hardware_id: str) -> Optional[Dict[str, Any]]:
        """Load and decrypt license from AppData"""
        try:
            if not os.path.exists(self.license_file):
                return None

            with open(self.license_file, 'r') as f:
                encrypted_data = f.read().strip()

            if not encrypted_data:
                return None

            license_data = self.crypto.decrypt_license_data(encrypted_data, hardware_id)
            return license_data

        except Exception as e:
            print(f"Error loading license: {e}")
            return None

    def delete_license(self) -> bool:
        """Delete license file"""
        try:
            if os.path.exists(self.license_file):
                os.remove(self.license_file)
            return True
        except Exception as e:
            print(f"Error deleting license: {e}")
            return False

    def license_exists(self) -> bool:
        """Check if license file exists"""
        return os.path.exists(self.license_file)

    def get_license_file_path(self) -> str:
        """Get the full path to license file"""
        return self.license_file


if __name__ == "__main__":
    # Test the crypto utilities
    print("License Crypto Test")
    print("=" * 40)

    # Test data
    hardware_id = "TEST123456789ABCDEF"
    license_data = {
        "license_key": "ABCD-EFGH-IJKL-MNOP",
        "user_name": "Test User",
        "license_type": "professional",
        "expires_at": "2025-12-31",
        "issued_at": "2024-01-01"
    }

    # Test encryption/decryption
    crypto = LicenseCrypto()

    print("Original data:", license_data)

    encrypted = crypto.encrypt_license_data(license_data, hardware_id)
    print(f"Encrypted: {encrypted[:50]}...")

    decrypted = crypto.decrypt_license_data(encrypted, hardware_id)
    print("Decrypted:", decrypted)

    # Test license key generation
    license_key = crypto.generate_license_key(license_data)
    print(f"Generated license key: {license_key}")

    # Test secure storage
    storage = SecureStorage("TaskPlannerTest")
    print(f"License file path: {storage.get_license_file_path()}")

    if storage.save_license(license_data, hardware_id):
        print("License saved successfully")

        loaded_data = storage.load_license(hardware_id)
        if loaded_data:
            print("License loaded successfully:", loaded_data.get('license_key'))
        else:
            print("Failed to load license")
    else:
        print("Failed to save license")
