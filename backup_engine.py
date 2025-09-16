#!/usr/bin/env python3
"""
Backup Engine
Handles the actual backup execution, drive mounting, and logging.
"""

import os
import sys
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

from backup_config import BackupConfigManager, BackupDestination, BackupProfile
from managers.drive_manager import DriveManager
from utils.logging_helper import get_backend_logger


class BackupEngine:
    """Handles backup execution and drive management."""

    def __init__(self, profile: BackupProfile = None):
        """Initialize the backup engine with a profile object."""
        self.profile = profile
        self.logger = get_backend_logger(__name__)  # For file logging
        self.ui_logger = logging.getLogger(__name__)  # For UI logging (propagates to root)
        self.destination_logger = None  # For destination-specific logging
        self.mounted_drives = []  # Track what we mounted
        self.drive_manager = DriveManager()  # For drive operations

    def _log(self, level: str, message: str):
        """Log message to UI (for display) and to file logger if available."""
        # Always log to UI logger (gets captured by UI)
        ui_log_func = getattr(self.ui_logger, level.lower())
        ui_log_func(message)
        
        # Log to destination file logger if available
        if self.destination_logger:
            file_log_func = getattr(self.destination_logger, level.lower())
            file_log_func(message)

    def _log_info(self, message: str):
        """Log info message to both UI and file."""
        self._log("info", message)

    def _log_error(self, message: str):
        """Log error message to both UI and file."""
        self._log("error", message)

    def setup_logging(self, destination_path: str) -> logging.Logger:
        """Setup destination-specific logging (in addition to console logging)."""
        log_dir = Path(destination_path) / "backup_logs"
        log_dir.mkdir(exist_ok=True)

        log_file = log_dir / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

        # Create a destination-specific logger
        destination_logger = logging.getLogger(f"backup_dest_{destination_path}")
        destination_logger.setLevel(logging.INFO)

        # Clear any existing handlers
        destination_logger.handlers.clear()

        # File handler for destination-specific logs
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)

        destination_logger.addHandler(file_handler)
        
        # Disable propagation to avoid duplicates (only file logging)
        destination_logger.propagate = False

        return destination_logger

    def _flush_and_close_destination_logger(self):
        """Flush and close the destination logger to ensure all logs are written."""
        if self.destination_logger:
            for handler in self.destination_logger.handlers:
                handler.flush()
                handler.close()
            self.destination_logger.handlers.clear()

    def run_custom_commands(self, commands: List, phase: str, logger: logging.Logger) -> bool:
        """Run custom commands (pre or post backup)."""
        self._log_info(f"Running {phase} commands...")

        for i, cmd in enumerate(commands):
            if not cmd.enabled:
                self._log_info(f"Skipping disabled {phase} command {i + 1}: {cmd.description}")
                continue

            self._log_info(f"Running {phase} command {i + 1}: {cmd.description}")
            self._log_info(f"Command: {cmd.command}")

            try:
                result = subprocess.run(
                    cmd.command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=cmd.timeout
                )

                if result.returncode == 0:
                    self._log_info("Command completed successfully")
                    
                    if result.stdout:
                        self._log_info(f"Output: {result.stdout}")
                else:
                    self._log_error(f"Command failed with exit code {result.returncode}")
                    self._log_error(f"Error: {result.stderr}")
                    return False

            except subprocess.TimeoutExpired:
                self._log_error(f"Command timed out after {cmd.timeout} seconds")
                return False
            except (OSError, subprocess.SubprocessError, PermissionError) as e:
                self._log_error(f"Error running command: {str(e)}")
                return False

        return True

    def sync_directory(self, source: str, destination: str, logger: logging.Logger, profile: BackupProfile) -> bool:
        """Sync a source directory to destination using rsync."""
        try:
            source_path = Path(source)
            dest_path = Path(destination) / source_path.name

            logger.info(f"Syncing {source} -> {dest_path}")

            # Ensure destination directory exists
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            # Build and run rsync command
            cmd = self._build_rsync_command(source, dest_path, logger, profile)
            result = subprocess.run(cmd, capture_output=True, text=True)

            return self._process_rsync_result(result, source, logger)

        except (OSError, subprocess.SubprocessError, PermissionError, FileNotFoundError) as e:
            logger.error(f"Error syncing {source}: {str(e)}")
            return False

    def _build_rsync_command(self, source: str, dest_path: Path, logger: logging.Logger, profile: BackupProfile) -> list:
        """Build rsync command with appropriate options."""
        cmd = [
            'rsync',
            '-av',
            '--progress',
            '--delete',
            str(source),
            str(dest_path)
        ]

        if profile.dry_run:
            cmd.append('--dry-run')
            logger.info("DRY RUN MODE - No files will actually be copied")

        return cmd

    def _process_rsync_result(self, result: subprocess.CompletedProcess, source: str, logger: logging.Logger) -> bool:
        """Process the result of rsync command."""
        if result.returncode == 0:
            logger.info(f"Successfully synced {source}")
            if result.stdout:
                self._log_rsync_output(result.stdout, logger)
            return True
        else:
            logger.error(f"Rsync failed for {source}")
            logger.error(f"Error: {result.stderr}")
            return False

    def _log_rsync_output(self, stdout: str, logger: logging.Logger) -> None:
        """Log rsync output with appropriate truncation."""
        lines = stdout.split('\n')
        if len(lines) > 50:
            logger.info("Rsync output (first 25 and last 25 lines):")
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

    def run_backup(self, profile: BackupProfile = None) -> bool:
        """Execute the complete backup process: pre-commands → destinations → post-commands."""
        if profile is None:
            profile = self.profile

        if not profile:
            self._log_error("No profile provided")
            return False

        # Validate profile
        config_manager = BackupConfigManager()
        errors = config_manager.validate_profile(profile)
        if errors:
            self._log_error("Profile validation failed:")
            for error in errors:
                self._log_error(f"  - {error}")
            return False

        self._log_info(f"Starting backup for profile: {profile.name}")

        # Setup destination-specific logging (use first enabled destination or temp directory)
        log_dir = self._get_log_directory(profile)
        try:
            self.destination_logger = self.setup_logging(log_dir)
        except Exception as e:
            # If we can't set up destination logging, continue with UI-only logging
            self._log_error(f"Failed to setup destination logging: {e}")
            self.destination_logger = None
        
        try:
            # 1. Run pre-backup commands
            if not self.run_custom_commands(profile.pre_commands, "pre-backup", self.ui_logger):
                self._log_error("Pre-backup commands failed")
                return False

            # 2. Process all destinations
            destinations_success = self._process_all_destinations(profile)

            # 3. Run post-backup commands (always run if pre-commands succeeded)
            if not self.run_custom_commands(profile.post_commands, "post-backup", self.ui_logger):
                self._log_error("Post-backup commands failed")
                destinations_success = False

            # 4. Cleanup mounted drives
            self._cleanup_mounted_drives()

            return destinations_success
            
        except Exception as e:
            self._log_error(f"Backup process failed: {e}")
            return False
        finally:
            # 5. Always flush and close destination logger to ensure all logs are written
            self._flush_and_close_destination_logger()

    def run_backup_to_destination(self, destination: BackupDestination, profile: BackupProfile = None) -> Tuple[bool, str]:
        """Run backup to a specific destination (files only, no custom commands)."""
        if profile is None:
            profile = self.profile

        if not profile:
            return False, "No profile provided"

        if not destination.enabled:
            return False, "Destination is disabled"

        try:
            # Setup destination (mounting, directory creation)
            setup_success, setup_msg = self._setup_destination(destination)
            if not setup_success:
                return False, setup_msg

            # Use existing destination logger or create one if not available
            logger = self.destination_logger
                
            # Log destination-specific messages
            self._log_info(f"Starting backup to {destination.target_path}")
            self._log_info(f"Profile: {profile.name}")
            self._log_info(f"Sources: {len(profile.sources)} directories")

            # Backup all sources to this destination
            success, failed_sources = self._backup_all_sources(destination, logger, profile)

            if success:
                self._log_info("Backup completed successfully for this destination")
                return True, "Backup completed successfully"
            else:
                self._log_error(f"Backup failed for sources: {', '.join(failed_sources)}")
                return False, f"Failed to backup sources: {', '.join(failed_sources)}"

        except (OSError, subprocess.SubprocessError, PermissionError, KeyboardInterrupt) as e:
            error_msg = f"Backup error: {str(e)}"
            self._log_error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error during backup: {str(e)}"
            self._log_error(error_msg)
            return False, error_msg

    def _get_log_directory(self, profile: BackupProfile) -> str:
        """Get directory for profile-level logging."""
        # Use first enabled destination for logging, otherwise temp directory
        for dest in profile.destinations:
            if dest.enabled:
                return dest.target_path
        
        import tempfile
        return tempfile.gettempdir()

    def _process_all_destinations(self, profile: BackupProfile) -> bool:
        """Process all enabled destinations."""
        success = True
        destinations_processed = 0

        for dest_idx, destination in enumerate(profile.destinations):
            if not destination.enabled:
                self._log_info(f"Skipping disabled destination {dest_idx + 1}")
                continue

            destinations_processed += 1
            self._log_info(f"Processing destination {dest_idx + 1}: {destination.target_path}")

            dest_success, message = self.run_backup_to_destination(destination, profile)
            
            if dest_success:
                self._log_info(f"✓ {message}")
            else:
                self._log_error(f"✗ {message}")
                success = False

        if destinations_processed == 0:
            self._log_info("No destinations to process - only running custom commands")

        return success

    def _cleanup_mounted_drives(self):
        """Unmount all drives we mounted during backup."""
        for drive in self.mounted_drives:
            self._log_info(f"Unmounting {drive}...")
            if self.drive_manager.unmount_drive(drive):
                self._log_info(f"Successfully unmounted {drive}")
            else:
                self._log_error(f"Failed to unmount {drive}")

    def _setup_destination(self, destination: BackupDestination) -> Tuple[bool, str]:
        """Setup destination for backup (mounting, directory creation)."""
        # Mount drive if needed
        if destination.auto_mount and destination.drive_device:
            success, message = self.drive_manager.mount_drive(
                destination.drive_device, 
                destination.mount_point
            )
            if not success:
                return False, f"Failed to mount drive: {message}"
            self.mounted_drives.append(destination.drive_device)

        # Ensure target directory exists
        try:
            os.makedirs(destination.target_path, exist_ok=True)
            return True, "Destination setup successful"
        except (OSError, PermissionError) as e:
            return False, f"Failed to create target directory: {str(e)}"

    def _backup_all_sources(self, destination: BackupDestination,
                            logger: logging.Logger,
                            profile: BackupProfile) -> Tuple[bool, list]:
        """Backup all enabled sources to destination."""
        failed_sources = []

        for source in profile.sources:
            if not source.enabled:
                logger.info(f"Skipping disabled source: {source.path}")
                continue

            if not self.sync_directory(source.path, destination.target_path, logger, profile):
                failed_sources.append(source.path)

        success = len(failed_sources) == 0
        return success, failed_sources


def main():
    """Command-line entry point for backup engine."""
    # Setup main logger for CLI usage
    main_logger = get_backend_logger(__name__ + ".main")
    
    if len(sys.argv) != 2:
        main_logger.error("Usage: backup_engine.py <profile_file_path>")
        sys.exit(1)

    profile_file_path = sys.argv[1]

    try:
        # Load the profile from file path
        from backup_config import BackupConfigManager
        config_manager = BackupConfigManager()
        
        profile = config_manager.load_profile_from_file(profile_file_path)
        if not profile:
            main_logger.error(f"Could not load profile from file '{profile_file_path}'")
            sys.exit(1)

        engine = BackupEngine(profile)
        success = engine.run_backup()

        if success:
            main_logger.info("Backup completed successfully!")
            sys.exit(0)
        else:
            main_logger.error("Backup completed with errors!")
            sys.exit(1)

    except (ValueError, OSError, PermissionError) as e:
        main_logger.error(f"Fatal error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        main_logger.info("Backup interrupted by user")
        sys.exit(130)
    except Exception as e:
        main_logger.error(f"Unexpected fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
