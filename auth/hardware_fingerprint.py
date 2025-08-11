"""
Hardware Fingerprinting for License Binding
Generates unique hardware ID for license validation
"""

import hashlib
import platform
import subprocess
import uuid
import os
import sys
import json
from typing import Optional


class HardwareFingerprint:
    """Generate unique hardware fingerprint for license binding"""

    def __init__(self):
        self.components = {}
        self.cache_file = os.path.join(os.path.expanduser("~"), ".taskplanner_hwid_cache.json")
        self._collect_hardware_info()

    def _collect_hardware_info(self):
        """Collect various hardware identifiers"""
        try:
            # Get CPU info
            self.components['cpu'] = self._get_cpu_id()

            # Get motherboard info
            self.components['motherboard'] = self._get_motherboard_id()

            # Get MAC address
            self.components['mac'] = self._get_mac_address()

            # Get hard drive serial
            self.components['hdd'] = self._get_hdd_serial()

            # Get Windows machine GUID (Windows only)
            if platform.system() == "Windows":
                self.components['machine_guid'] = self._get_windows_machine_guid()

            # Get system UUID
            self.components['system_uuid'] = self._get_system_uuid()

        except Exception as e:
            print(f"Error collecting hardware info: {e}")

    def _get_cpu_id(self) -> str:
        """Get CPU identifier"""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(
                    ['wmic', 'cpu', 'get', 'ProcessorId', '/value'],
                    capture_output=True, text=True, timeout=10, creationflags=subprocess.CREATE_NO_WINDOW
                )
                for line in result.stdout.split('\n'):
                    if 'ProcessorId=' in line:
                        return line.split('=')[1].strip()
            elif platform.system() == "Linux":
                with open('/proc/cpuinfo', 'r') as f:
                    for line in f:
                        if 'processor' in line:
                            return line.split(':')[1].strip()
            elif platform.system() == "Darwin":  # macOS
                result = subprocess.run(
                    ['system_profiler', 'SPHardwareDataType'],
                    capture_output=True, text=True, timeout=10, creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
                )
                return hashlib.md5(result.stdout.encode()).hexdigest()[:16]
        except:
            pass
        return platform.processor()[:16] or "unknown_cpu"

    def _get_motherboard_id(self) -> str:
        """Get motherboard identifier"""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(
                    ['wmic', 'baseboard', 'get', 'SerialNumber', '/value'],
                    capture_output=True, text=True, timeout=10, creationflags=subprocess.CREATE_NO_WINDOW
                )
                for line in result.stdout.split('\n'):
                    if 'SerialNumber=' in line:
                        serial = line.split('=')[1].strip()
                        if serial and serial != "To be filled by O.E.M.":
                            return serial
            elif platform.system() == "Linux":
                try:
                    with open('/sys/class/dmi/id/board_serial', 'r') as f:
                        return f.read().strip()
                except:
                    pass
        except:
            pass
        return "unknown_mb"

    def _get_mac_address(self) -> str:
        """Get primary MAC address"""
        try:
            mac = uuid.getnode()
            return ':'.join(('%012X' % mac)[i:i+2] for i in range(0, 12, 2))
        except:
            return "unknown_mac"

    def _get_hdd_serial(self) -> str:
        """Get hard drive serial number"""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(
                    ['wmic', 'diskdrive', 'get', 'SerialNumber', '/value'],
                    capture_output=True, text=True, timeout=10, creationflags=subprocess.CREATE_NO_WINDOW
                )
                for line in result.stdout.split('\n'):
                    if 'SerialNumber=' in line:
                        serial = line.split('=')[1].strip()
                        if serial:
                            return serial
            elif platform.system() == "Linux":
                result = subprocess.run(
                    ['lsblk', '-d', '-o', 'SERIAL'],
                    capture_output=True, text=True, timeout=10, creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
                )
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    return lines[1].strip()
        except:
            pass
        return "unknown_hdd"

    def _get_windows_machine_guid(self) -> str:
        """Get Windows machine GUID"""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(
                    ['reg', 'query', 'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Cryptography', '/v', 'MachineGuid'],
                    capture_output=True, text=True, timeout=10, creationflags=subprocess.CREATE_NO_WINDOW
                )
                for line in result.stdout.split('\n'):
                    if 'MachineGuid' in line:
                        return line.split()[-1]
        except:
            pass
        return "unknown_guid"

    def _get_system_uuid(self) -> str:
        """Get system UUID with consistent fallback"""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(
                    ['wmic', 'csproduct', 'get', 'UUID', '/value'],
                    capture_output=True, text=True, timeout=10, creationflags=subprocess.CREATE_NO_WINDOW
                )
                for line in result.stdout.split('\n'):
                    if 'UUID=' in line:
                        uuid_value = line.split('=')[1].strip()
                        if uuid_value and uuid_value != "FFFFFFFF-FFFF-FFFF-FFFF-FFFFFFFFFFFF":
                            return uuid_value
            elif platform.system() == "Linux":
                try:
                    with open('/sys/class/dmi/id/product_uuid', 'r') as f:
                        return f.read().strip()
                except:
                    pass
        except:
            pass

        # Use consistent fallback based on machine characteristics
        return self._get_consistent_fallback_uuid()

    def _get_consistent_fallback_uuid(self) -> str:
        """Generate consistent fallback UUID based on machine characteristics"""
        # Check cache first
        cached_uuid = self._load_cached_uuid()
        if cached_uuid:
            return cached_uuid

        # Generate consistent UUID based on machine characteristics
        machine_data = f"{platform.system()}{platform.node()}{platform.machine()}{uuid.getnode()}"

        # Create a deterministic UUID from machine data
        hash_obj = hashlib.md5(machine_data.encode())
        hash_hex = hash_obj.hexdigest()

        # Format as UUID
        fallback_uuid = f"{hash_hex[:8]}-{hash_hex[8:12]}-{hash_hex[12:16]}-{hash_hex[16:20]}-{hash_hex[20:32]}"

        # Cache this UUID for future use
        self._save_cached_uuid(fallback_uuid)

        return fallback_uuid

    def _load_cached_uuid(self) -> str:
        """Load cached UUID if it exists"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    cache_data = json.load(f)
                    return cache_data.get('fallback_uuid', '')
        except:
            pass
        return ''

    def _save_cached_uuid(self, uuid_value: str):
        """Save UUID to cache"""
        try:
            cache_data = {'fallback_uuid': uuid_value}
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f)
        except:
            pass

    def generate_fingerprint(self) -> str:
        """Generate unique hardware fingerprint"""
        # Combine all hardware components
        fingerprint_data = ""

        # Use the most reliable components
        priority_components = ['cpu', 'motherboard', 'mac', 'machine_guid', 'system_uuid']

        for component in priority_components:
            if component in self.components and self.components[component]:
                fingerprint_data += self.components[component]

        # Add fallback components if needed
        if len(fingerprint_data) < 20:
            for component, value in self.components.items():
                if component not in priority_components and value:
                    fingerprint_data += value

        # Generate SHA-256 hash
        if fingerprint_data:
            return hashlib.sha256(fingerprint_data.encode()).hexdigest()[:32].upper()
        else:
            # Fallback to a consistent combination of available system info
            fallback_data = f"{platform.system()}{platform.node()}{platform.machine()}{uuid.getnode()}"
            return hashlib.sha256(fallback_data.encode()).hexdigest()[:32].upper()

    def get_hardware_info(self) -> dict:
        """Get detailed hardware information for display"""
        return {
            'fingerprint': self.generate_fingerprint(),
            'system': platform.system(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'components': self.components
        }


def get_hardware_id() -> str:
    """Convenience function to get hardware ID"""
    fingerprint = HardwareFingerprint()
    return fingerprint.generate_fingerprint()


def get_hardware_info() -> dict:
    """Convenience function to get hardware info"""
    fingerprint = HardwareFingerprint()
    return fingerprint.get_hardware_info()


if __name__ == "__main__":
    # Test the hardware fingerprinting
    print("Hardware Fingerprinting Test")
    print("=" * 40)

    fingerprint = HardwareFingerprint()
    info = fingerprint.get_hardware_info()

    print(f"Hardware ID: {info['fingerprint']}")
    print(f"System: {info['system']}")
    print(f"Machine: {info['machine']}")
    print(f"Processor: {info['processor']}")
    print("\nComponents:")
    for key, value in info['components'].items():
        print(f"  {key}: {value}")
