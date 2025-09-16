#!/usr/bin/env python3
"""
Drive Manager Module for Concrete Backup
Handles drive detection for backup configuration (simplified version).
"""

import os
import subprocess
import json
from typing import List, Dict
from utils.logging_helper import get_backend_logger


class DriveInfo:
    """Data class for drive information."""

    def __init__(self, device: str, uuid: str = "", label: str = "",
                 fstype: str = "", size: str = "", mountpoint: str = "",
                 is_mounted: bool = False, is_removable: bool = False):
        self.device = device
        self.uuid = uuid
        self.label = label
        self.fstype = fstype
        self.size = size
        self.mountpoint = mountpoint
        self.is_mounted = is_mounted
        self.is_removable = is_removable

    def __repr__(self):
        return f"DriveInfo(device={self.device}, label={self.label}, mounted={self.is_mounted})"


class DriveManager:
    """Simplified drive manager for configuration purposes."""

    def __init__(self):
        self.drives: List[DriveInfo] = []
        self.logger = get_backend_logger(__name__)

    def refresh_drives(self) -> List[DriveInfo]:
        """Discover and refresh the list of available drives."""
        self.logger.info("Refreshing drive list")
        self.drives = []

        try:
            # Use lsblk to get block device information
            result = subprocess.run([
                'lsblk', '-J', '-o',
                'NAME,UUID,LABEL,FSTYPE,SIZE,MOUNTPOINT,TYPE,HOTPLUG'
            ], capture_output=True, text=True, check=True)

            data = json.loads(result.stdout)
            self._parse_lsblk_output(data['blockdevices'])
            
            self.logger.info(f"Found {len(self.drives)} drives")

        except subprocess.CalledProcessError as e:
            self.logger.error(f"lsblk command failed: {e}")
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse lsblk output: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error refreshing drives: {e}")

        return self.drives

    def _parse_lsblk_output(self, devices: List[Dict], parent_device: str = ""):
        """Parse lsblk JSON output recursively."""
        for device in devices:
            device_name = device.get('name', '')
            device_path = f"/dev/{device_name}"

            # Skip loop devices and other virtual devices we don't want
            if (device_name.startswith('loop')
                    or device_name.startswith('ram')
                    or device.get('type') == 'rom'):
                continue

            # For partitions, include parent device info
            if device.get('type') == 'part' and parent_device:
                device_path = f"/dev/{device_name}"

            drive_info = DriveInfo(
                device=device_path,
                uuid=device.get('uuid', ''),
                label=device.get('label', ''),
                fstype=device.get('fstype', ''),
                size=device.get('size', ''),
                mountpoint=device.get('mountpoint', ''),
                is_mounted=bool(device.get('mountpoint')),
                is_removable=bool(device.get('hotplug'))
            )

            # Only add drives that have a filesystem or are removable
            if drive_info.fstype or drive_info.is_removable:
                self.drives.append(drive_info)

            # Process children (partitions)
            if 'children' in device:
                self._parse_lsblk_output(device['children'], device_name)

    def mount_drive(self, drive_device: str, mount_point: str) -> tuple[bool, str]:
        """Mount a drive to the specified mount point."""
        self.logger.info(f"Attempting to mount {drive_device} at {mount_point}")
        
        try:
            # Check if already mounted
            result = subprocess.run(['findmnt', mount_point],
                                    capture_output=True, text=True)
            if result.returncode == 0:
                self.logger.info(f"Drive already mounted at {mount_point}")
                return True, f"Already mounted at {mount_point}"

            # Create mount point
            os.makedirs(mount_point, exist_ok=True)
            self.logger.info(f"Created mount point directory: {mount_point}")

            # Use sudo mount directly to mount to our specific location
            self.logger.info(f"Trying sudo mount for {drive_device}")
            result = subprocess.run([
                'sudo', 'mount', drive_device, mount_point
            ], capture_output=True, text=True)

            if result.returncode == 0:
                self.logger.info(f"Successfully mounted {drive_device} at {mount_point} using sudo")
                return True, f"Mounted {drive_device} at {mount_point}"
            else:
                self.logger.error(f"Failed to mount {drive_device}: {result.stderr}")
                return False, f"Failed to mount: {result.stderr}"

        except (OSError, subprocess.SubprocessError, PermissionError) as e:
            self.logger.error(f"Error mounting drive {drive_device}: {str(e)}")
            return False, f"Error mounting drive: {str(e)}"

    def unmount_drive(self, drive_device: str) -> bool:
        """Unmount a drive."""
        self.logger.info(f"Attempting to unmount {drive_device}")
        
        try:
            result = subprocess.run([
                'sudo', 'umount', drive_device
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info(f"Successfully unmounted {drive_device}")
                return True
            else:
                # Check if it's already unmounted
                if "not mounted" in result.stderr:
                    self.logger.info(f"{drive_device} was already unmounted")
                    return True
                else:
                    self.logger.error(f"Failed to unmount {drive_device}: {result.stderr}")
                    return False

        except (OSError, subprocess.SubprocessError, PermissionError) as e:
            self.logger.error(f"Error unmounting drive {drive_device}: {str(e)}")
            return False
