#!/usr/bin/env python3
"""
Drive Manager Module for Concrete Backup
Handles drive detection for backup configuration (simplified version).
"""

import os
import subprocess
import json
from typing import List, Dict, Optional
import psutil


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
    
    def refresh_drives(self) -> List[DriveInfo]:
        """Discover and refresh the list of available drives."""
        self.drives = []
        
        try:
            # Use lsblk to get block device information
            result = subprocess.run([
                'lsblk', '-J', '-o', 
                'NAME,UUID,LABEL,FSTYPE,SIZE,MOUNTPOINT,TYPE,HOTPLUG'
            ], capture_output=True, text=True, check=True)
            
            data = json.loads(result.stdout)
            self._parse_lsblk_output(data['blockdevices'])
            
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            print(f"Error getting drive information: {e}")
        
        return self.drives
    
    def _parse_lsblk_output(self, devices: List[Dict], parent_device: str = ""):
        """Parse lsblk JSON output recursively."""
        for device in devices:
            device_name = device.get('name', '')
            device_path = f"/dev/{device_name}"
            
            # Skip loop devices and other virtual devices we don't want
            if (device_name.startswith('loop') or 
                device_name.startswith('ram') or
                device.get('type') == 'rom'):
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
