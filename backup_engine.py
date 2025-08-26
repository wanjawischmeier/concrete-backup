#!/usr/bin/env python3
"""
Backup Engine
Handles the actual backup execution, drive mounting, and logging.
"""

import os
import sys
import shutil
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import json

from backup_config import BackupConfigManager, BackupProfile, BackupDestination


class BackupEngine:
    """Handles backup execution and drive management."""
    
    def __init__(self, profile_name: str, config_manager: BackupConfigManager = None):
        """Initialize the backup engine."""
        if config_manager is None:
            config_manager = BackupConfigManager()
        
        self.config_manager = config_manager
        self.profile = config_manager.load_profile(profile_name)
        
        if not self.profile:
            raise ValueError(f"Profile '{profile_name}' not found")
        
        self.logger = None
        self.mounted_drives = []  # Track what we mounted
        
    def setup_logging(self, destination_path: str) -> logging.Logger:
        """Setup logging for a specific destination."""
        log_dir = Path(destination_path) / "backup_logs"
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logger = logging.getLogger(f"backup_{destination_path}")
        logger.setLevel(logging.INFO)
        
        # Clear any existing handlers
        logger.handlers.clear()
        
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def mount_drive(self, destination: BackupDestination) -> Tuple[bool, str]:
        """Mount a drive if needed."""
        if not destination.auto_mount:
            return True, "Auto-mount disabled"
        
        try:
            # Check if already mounted
            result = subprocess.run(['findmnt', destination.mount_point], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return True, f"Already mounted at {destination.mount_point}"
            
            # Create mount point
            os.makedirs(destination.mount_point, exist_ok=True)
            
            # Try udisksctl first
            result = subprocess.run([
                'udisksctl', 'mount', '-b', destination.drive_device
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.mounted_drives.append(destination.drive_device)
                return True, f"Mounted {destination.drive_device}"
            else:
                # Fallback to sudo mount
                result = subprocess.run([
                    'sudo', 'mount', destination.drive_device, destination.mount_point
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.mounted_drives.append(destination.drive_device)
                    return True, f"Mounted {destination.drive_device} at {destination.mount_point}"
                else:
                    return False, f"Failed to mount: {result.stderr}"
        
        except Exception as e:
            return False, f"Error mounting drive: {str(e)}"
    
    def unmount_drive(self, drive_device: str) -> bool:
        """Unmount a drive."""
        try:
            # Try udisksctl first
            result = subprocess.run([
                'udisksctl', 'unmount', '-b', drive_device
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                return True
            else:
                # Fallback to sudo umount
                result = subprocess.run([
                    'sudo', 'umount', drive_device
                ], capture_output=True, text=True)
                return result.returncode == 0
        
        except Exception:
            return False
    
    def run_custom_commands(self, commands: List, phase: str, logger: logging.Logger) -> bool:
        """Run custom commands (pre or post backup)."""
        logger.info(f"Running {phase} commands...")
        
        for i, cmd in enumerate(commands):
            if not cmd.enabled:
                logger.info(f"Skipping disabled {phase} command {i+1}: {cmd.description}")
                continue
            
            logger.info(f"Running {phase} command {i+1}: {cmd.description}")
            logger.info(f"Command: {cmd.command}")
            
            try:
                result = subprocess.run(
                    cmd.command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=cmd.timeout
                )
                
                if result.returncode == 0:
                    logger.info(f"Command completed successfully")
                    if result.stdout:
                        logger.info(f"Output: {result.stdout}")
                else:
                    logger.error(f"Command failed with exit code {result.returncode}")
                    logger.error(f"Error: {result.stderr}")
                    return False
                
            except subprocess.TimeoutExpired:
                logger.error(f"Command timed out after {cmd.timeout} seconds")
                return False
            except Exception as e:
                logger.error(f"Error running command: {str(e)}")
                return False
        
        return True
    
    def sync_directory(self, source: str, destination: str, logger: logging.Logger) -> bool:
        """Sync a source directory to destination using rsync."""
        try:
            source_path = Path(source)
            dest_path = Path(destination) / source_path.name
            
            logger.info(f"Syncing {source} -> {dest_path}")
            
            # Ensure destination directory exists
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Use rsync for efficient synchronization
            cmd = [
                'rsync',
                '-av',  # archive mode, verbose
                '--delete',  # delete files that don't exist in source
                '--progress',
                f"{source}/",  # trailing slash important for rsync
                str(dest_path)
            ]
            
            if self.profile.dry_run:
                cmd.append('--dry-run')
                logger.info("DRY RUN MODE - No files will actually be copied")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Successfully synced {source}")
                if result.stdout:
                    # Log rsync output (but limit it to avoid huge logs)
                    lines = result.stdout.split('\n')
                    if len(lines) > 50:
                        logger.info(f"Rsync output (first 25 and last 25 lines):")
                        for line in lines[:25]:
                            if line.strip():
                                logger.info(f"  {line}")
                        logger.info("  ... (output truncated) ...")
                        for line in lines[-25:]:
                            if line.strip():
                                logger.info(f"  {line}")
                    else:
                        logger.info("Rsync output:")
                        for line in lines:
                            if line.strip():
                                logger.info(f"  {line}")
                return True
            else:
                logger.error(f"Rsync failed for {source}")
                logger.error(f"Error: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error syncing {source}: {str(e)}")
            return False
    
    def run_backup(self) -> bool:
        """Execute the complete backup process."""
        success = True
        
        # Validate profile
        errors = self.config_manager.validate_profile(self.profile)
        if errors:
            print("Profile validation failed:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        print(f"Starting backup for profile: {self.profile.name}")
        
        # Process each destination
        for dest_idx, destination in enumerate(self.profile.destinations):
            if not destination.enabled:
                print(f"Skipping disabled destination {dest_idx + 1}")
                continue
            
            print(f"\nProcessing destination {dest_idx + 1}: {destination.target_path}")
            
            # Mount drive if needed
            mount_success, mount_msg = self.mount_drive(destination)
            if not mount_success:
                print(f"Failed to mount drive: {mount_msg}")
                success = False
                continue
            
            print(f"Mount status: {mount_msg}")
            
            # Ensure target directory exists
            try:
                os.makedirs(destination.target_path, exist_ok=True)
            except Exception as e:
                print(f"Failed to create target directory: {e}")
                success = False
                continue
            
            # Setup logging for this destination
            logger = self.setup_logging(destination.target_path)
            logger.info(f"Starting backup to {destination.target_path}")
            logger.info(f"Profile: {self.profile.name}")
            logger.info(f"Sources: {len(self.profile.sources)} directories")
            
            try:
                # Run pre-backup commands
                if not self.run_custom_commands(self.profile.pre_commands, "pre-backup", logger):
                    logger.error("Pre-backup commands failed, skipping this destination")
                    success = False
                    continue
                
                # Backup each source
                sources_success = True
                for source_idx, source in enumerate(self.profile.sources):
                    if not source.enabled:
                        logger.info(f"Skipping disabled source: {source.path}")
                        continue
                    
                    if not self.sync_directory(source.path, destination.target_path, logger):
                        sources_success = False
                        success = False
                
                # Run post-backup commands only if sources succeeded
                if sources_success:
                    if not self.run_custom_commands(self.profile.post_commands, "post-backup", logger):
                        logger.error("Post-backup commands failed")
                        success = False
                else:
                    logger.error("Skipping post-backup commands due to source sync failures")
                
                if sources_success:
                    logger.info("Backup completed successfully for this destination")
                else:
                    logger.error("Backup completed with errors for this destination")
            
            except Exception as e:
                logger.error(f"Unexpected error during backup: {str(e)}")
                success = False
        
        # Cleanup: unmount drives we mounted
        for drive in self.mounted_drives:
            print(f"Unmounting {drive}...")
            if self.unmount_drive(drive):
                print(f"Successfully unmounted {drive}")
            else:
                print(f"Failed to unmount {drive}")
                success = False
        
        return success
    
    def run_backup_to_destination(self, destination: BackupDestination) -> Tuple[bool, str]:
        """
        Run backup to a specific destination.
        
        Args:
            destination: The backup destination to run backup to
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Check if destination is enabled
            if not destination.enabled:
                return False, "Destination is disabled"
            
            # Mount drive if needed
            if destination.auto_mount and destination.drive_device:
                mount_success, mount_msg = self.mount_drive(destination.drive_device, destination.mount_point)
                if not mount_success:
                    return False, f"Failed to mount drive: {mount_msg}"
            
            # Ensure target directory exists
            try:
                os.makedirs(destination.target_path, exist_ok=True)
            except Exception as e:
                return False, f"Failed to create target directory: {str(e)}"
            
            # Setup logging for this destination
            logger = self.setup_logging(destination.target_path)
            logger.info(f"Starting backup to {destination.target_path}")
            logger.info(f"Profile: {self.profile.name}")
            logger.info(f"Sources: {len(self.profile.sources)} directories")
            
            success = True
            
            # Run pre-backup commands
            if not self.run_custom_commands(self.profile.pre_commands, "pre-backup", logger):
                logger.error("Pre-backup commands failed")
                return False, "Pre-backup commands failed"
            
            # Backup each source
            failed_sources = []
            for source in self.profile.sources:
                if not source.enabled:
                    logger.info(f"Skipping disabled source: {source.path}")
                    continue
                
                if not self.sync_directory(source.path, destination.target_path, logger):
                    failed_sources.append(source.path)
                    success = False
            
            # Run post-backup commands only if sources succeeded
            if success:
                if not self.run_custom_commands(self.profile.post_commands, "post-backup", logger):
                    logger.error("Post-backup commands failed")
                    return False, "Post-backup commands failed"
                
                logger.info("Backup completed successfully for this destination")
                return True, "Backup completed successfully"
            else:
                logger.error(f"Backup failed for sources: {', '.join(failed_sources)}")
                return False, f"Failed to backup sources: {', '.join(failed_sources)}"
                
        except Exception as e:
            error_msg = f"Unexpected error during backup: {str(e)}"
            if hasattr(self, 'logger') and self.logger:
                self.logger.error(error_msg)
            return False, error_msg


def main():
    """Command-line entry point for backup engine."""
    if len(sys.argv) != 2:
        print("Usage: backup_engine.py <profile_name>")
        sys.exit(1)
    
    profile_name = sys.argv[1]
    
    try:
        engine = BackupEngine(profile_name)
        success = engine.run_backup()
        
        if success:
            print("\nBackup completed successfully!")
            sys.exit(0)
        else:
            print("\nBackup completed with errors!")
            sys.exit(1)
    
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
