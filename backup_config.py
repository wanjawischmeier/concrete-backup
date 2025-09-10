#!/usr/bin/env python3
"""
Backup Configuration Management
Handles loading, saving, and validation of backup configurations.
"""

import yaml
import os
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class BackupSource:
    """Represents a source directory for backup."""
    path: str
    enabled: bool = True

    def is_valid(self) -> bool:
        """Check if the source path exists."""
        return os.path.exists(self.path)


@dataclass
class BackupDestination:
    """Represents a backup destination."""
    drive_device: str  # e.g., /dev/sda1
    mount_point: str   # e.g., /media/user/backup_drive
    target_path: str   # e.g., /media/user/backup_drive/backups
    enabled: bool = True
    auto_mount: bool = True

    def __post_init__(self):
        """Validate destination settings."""
        if self.auto_mount and not self.drive_device:
            raise ValueError("Drive device required when auto_mount is enabled")


@dataclass
class CustomCommand:
    """Represents a custom command to run before/after backup."""
    command: str
    description: str = ""
    enabled: bool = True
    timeout: int = 300  # 5 minutes default timeout


@dataclass
class ScheduleConfig:
    """Backup schedule configuration."""
    enabled: bool = False
    hour: int = 2  # 2 AM default
    minute: int = 0
    days_of_week: List[int] = None  # 0=Monday, 6=Sunday, None=daily

    def __post_init__(self):
        if self.days_of_week is None:
            self.days_of_week = list(range(7))  # Daily by default


@dataclass
class BackupProfile:
    """Complete backup configuration profile."""
    name: str
    sources: List[BackupSource]
    destinations: List[BackupDestination]
    pre_commands: List[CustomCommand]
    post_commands: List[CustomCommand]
    schedule: ScheduleConfig
    log_enabled: bool = True
    dry_run: bool = False
    created_at: str = ""
    modified_at: str = ""

    def __post_init__(self):
        """Initialize empty lists if None."""
        if not self.sources:
            self.sources = []
        if not self.destinations:
            self.destinations = []
        if not self.pre_commands:
            self.pre_commands = []
        if not self.post_commands:
            self.post_commands = []
        if not self.schedule:
            self.schedule = ScheduleConfig()


class BackupConfigManager:
    """Manages backup configurations and profiles."""

    def __init__(self):
        """Initialize the config manager."""
        self.current_profile: Optional[BackupProfile] = None

    def create_profile(self, name: str) -> BackupProfile:
        """Create a new backup profile."""
        from datetime import datetime

        profile = BackupProfile(
            name=name,
            sources=[],
            destinations=[],
            pre_commands=[],
            post_commands=[],
            schedule=ScheduleConfig(),
            created_at=datetime.now().isoformat(),
            modified_at=datetime.now().isoformat()
        )

        self.current_profile = profile
        return profile

    def save_profile(self, profile: BackupProfile, filepath: str) -> bool:
        """Save a backup profile to a YAML file."""
        try:
            from datetime import datetime
            profile.modified_at = datetime.now().isoformat()

            filepath_obj = Path(filepath)

            # Create directory if it doesn't exist
            filepath_obj.parent.mkdir(parents=True, exist_ok=True)

            # Convert dataclass to dict
            profile_dict = self._profile_to_dict(profile)

            # Always save as YAML
            with open(filepath_obj, 'w') as f:
                yaml.dump(profile_dict, f, default_flow_style=False, indent=2)

            return True

        except (OSError, PermissionError, yaml.YAMLError) as e:
            print(f"Error saving profile: {e}")
            return False

    def load_profile_from_file(self, filepath: str) -> Optional[BackupProfile]:
        """Load a backup profile from a YAML file."""
        try:
            filepath_obj = Path(filepath)
            if not filepath_obj.exists():
                return None

            with open(filepath_obj, 'r') as f:
                profile_dict = yaml.safe_load(f)

            profile = self._dict_to_profile(profile_dict)
            self.current_profile = profile
            return profile

        except (OSError, PermissionError, FileNotFoundError, yaml.YAMLError) as e:
            print(f"Error loading profile: {e}")
            return None

    def validate_profile(self, profile: BackupProfile) -> List[str]:
        """Validate a backup profile and return list of errors."""
        errors = []

        # Basic validation
        errors.extend(self._validate_basic_fields(profile))

        # Validate sources and destinations
        errors.extend(self._validate_sources(profile.sources))
        errors.extend(self._validate_destinations(profile.destinations))

        # Validate schedule
        errors.extend(self._validate_schedule(profile.schedule))

        return errors

    def validate_profile_with_ui(self, profile: Optional['BackupProfile'], parent_widget=None) -> bool:
        """
        Validate a backup profile and show UI message if validation fails.
        
        Args:
            profile: The profile to validate (can be None)
            parent_widget: Parent widget for message boxes (optional)
            
        Returns:
            bool: True if validation passes, False otherwise
        """
        # Check if profile exists
        if not profile:
            if parent_widget:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(parent_widget, "No Profile", "No backup profile loaded!")
            return False

        # Validate profile content
        errors = self.validate_profile(profile)
        if errors:
            if parent_widget:
                from PyQt5.QtWidgets import QMessageBox
                # Show user-friendly error message
                if len(errors) == 1:
                    error_message = errors[0]
                else:
                    error_message = "Multiple validation errors:\n• " + "\n• ".join(errors)
                
                QMessageBox.warning(
                    parent_widget, "Profile Validation Error", error_message
                )
            return False

        return True

    def _validate_basic_fields(self, profile: BackupProfile) -> List[str]:
        """Validate basic profile fields."""
        errors = []

        if not profile.name:
            errors.append("Profile name is required")
        # Removed requirements for sources and destinations
        # if not profile.sources:
        #     errors.append("No backup sources defined. Please add at least one source directory.")
        # if not profile.destinations:
        #     errors.append("No backup destinations defined. Please add at least one destination.")

        return errors

    def _validate_sources(self, sources: List[BackupSource]) -> List[str]:
        """Validate source directories."""
        errors = []

        for i, source in enumerate(sources):
            if not source.path:
                errors.append(f"Source {i + 1}: Path is required")
            elif not source.is_valid():
                errors.append(f"Source {i + 1}: Path does not exist: {source.path}")

        return errors

    def _validate_destinations(self, destinations: List[BackupDestination]) -> List[str]:
        """Validate backup destinations."""
        errors = []

        for i, dest in enumerate(destinations):
            if not dest.target_path:
                errors.append(f"Destination {i + 1}: Target path is required")
            if dest.auto_mount and not dest.drive_device:
                errors.append(f"Destination {i + 1}: Drive device required for auto-mount")

        return errors

    def _validate_schedule(self, schedule) -> List[str]:
        """Validate backup schedule."""
        errors = []

        if schedule.enabled:
            if not (0 <= schedule.hour <= 23):
                errors.append("Schedule hour must be between 0 and 23")
            if not (0 <= schedule.minute <= 59):
                errors.append("Schedule minute must be between 0 and 59")

        return errors

    def _profile_to_dict(self, profile: BackupProfile) -> Dict[str, Any]:
        """Convert profile dataclass to dictionary."""
        try:
            # Convert sources to dict
            sources_list = [asdict(source) for source in profile.sources or []]

            # Convert destinations to dict
            destinations_list = [asdict(dest) for dest in profile.destinations or []]

            # Convert pre_commands to dict
            pre_commands_list = [asdict(cmd) for cmd in profile.pre_commands or []]

            # Convert post_commands to dict
            post_commands_list = [asdict(cmd) for cmd in profile.post_commands or []]

            # Convert schedule to dict
            schedule_dict = asdict(profile.schedule) if profile.schedule else asdict(ScheduleConfig())

            return {
                "name": profile.name,
                "sources": sources_list,
                "destinations": destinations_list,
                "pre_commands": pre_commands_list,
                "post_commands": post_commands_list,
                "schedule": schedule_dict,
                "log_enabled": profile.log_enabled,
                "dry_run": profile.dry_run,
                "created_at": profile.created_at,
                "modified_at": profile.modified_at
            }
        except Exception as e:
            print(f"Error in _profile_to_dict: {e}")
            print(f"Profile name: {profile.name}")
            print(f"Sources: {profile.sources}")
            print(f"Destinations: {profile.destinations}")
            print(f"Pre-commands: {profile.pre_commands}")
            print(f"Post-commands: {profile.post_commands}")
            print(f"Schedule: {profile.schedule}")
            raise

    def _dict_to_profile(self, data: Dict[str, Any]) -> BackupProfile:
        """Convert dictionary to profile dataclass."""
        return BackupProfile(
            name=data.get("name", ""),
            sources=[BackupSource(**src) for src in data.get("sources", [])],
            destinations=[BackupDestination(**dest) for dest in data.get("destinations", [])],
            pre_commands=[CustomCommand(**cmd) for cmd in data.get("pre_commands", [])],
            post_commands=[CustomCommand(**cmd) for cmd in data.get("post_commands", [])],
            schedule=ScheduleConfig(**data.get("schedule", {})),
            log_enabled=data.get("log_enabled", True),
            dry_run=data.get("dry_run", False),
            created_at=data.get("created_at", ""),
            modified_at=data.get("modified_at", "")
        )
