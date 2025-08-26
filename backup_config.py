#!/usr/bin/env python3
"""
Backup Configuration Management
Handles loading, saving, and validation of backup configurations.
"""

import json
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
    
    def __post_init__(self):
        """Validate the source path exists."""
        if not os.path.exists(self.path):
            raise ValueError(f"Source path does not exist: {self.path}")


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
    
    def __init__(self, config_dir: str = None):
        """Initialize the config manager."""
        if config_dir is None:
            config_dir = os.path.expanduser("~/.config/concrete-backup")
        
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.profiles_dir = self.config_dir / "profiles"
        self.profiles_dir.mkdir(exist_ok=True)
        
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
    
    def save_profile(self, profile: BackupProfile, format: str = "yaml") -> bool:
        """Save a backup profile to disk."""
        try:
            from datetime import datetime
            profile.modified_at = datetime.now().isoformat()
            
            filename = f"{profile.name}.{format}"
            filepath = self.profiles_dir / filename
            
            # Convert dataclass to dict
            profile_dict = self._profile_to_dict(profile)
            
            if format.lower() == "json":
                with open(filepath, 'w') as f:
                    json.dump(profile_dict, f, indent=2)
            elif format.lower() in ["yaml", "yml"]:
                with open(filepath, 'w') as f:
                    yaml.dump(profile_dict, f, default_flow_style=False, indent=2)
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            return True
            
        except Exception as e:
            print(f"Error saving profile: {e}")
            return False
    
    def load_profile(self, name: str) -> Optional[BackupProfile]:
        """Load a backup profile from disk."""
        try:
            # Try both yaml and json extensions
            for ext in ["yaml", "yml", "json"]:
                filepath = self.profiles_dir / f"{name}.{ext}"
                if filepath.exists():
                    with open(filepath, 'r') as f:
                        if ext == "json":
                            profile_dict = json.load(f)
                        else:
                            profile_dict = yaml.safe_load(f)
                    
                    profile = self._dict_to_profile(profile_dict)
                    self.current_profile = profile
                    return profile
            
            return None
            
        except Exception as e:
            print(f"Error loading profile: {e}")
            return None
    
    def list_profiles(self) -> List[str]:
        """List all available profile names."""
        profiles = []
        for file in self.profiles_dir.glob("*.yaml"):
            profiles.append(file.stem)
        for file in self.profiles_dir.glob("*.yml"):
            if file.stem not in profiles:
                profiles.append(file.stem)
        for file in self.profiles_dir.glob("*.json"):
            if file.stem not in profiles:
                profiles.append(file.stem)
        
        return sorted(profiles)
    
    def delete_profile(self, name: str) -> bool:
        """Delete a profile from disk."""
        try:
            for ext in ["yaml", "yml", "json"]:
                filepath = self.profiles_dir / f"{name}.{ext}"
                if filepath.exists():
                    filepath.unlink()
                    return True
            return False
            
        except Exception as e:
            print(f"Error deleting profile: {e}")
            return False
    
    def validate_profile(self, profile: BackupProfile) -> List[str]:
        """Validate a backup profile and return list of errors."""
        errors = []
        
        if not profile.name:
            errors.append("Profile name is required")
        
        if not profile.sources:
            errors.append("At least one source directory is required")
        
        if not profile.destinations:
            errors.append("At least one destination is required")
        
        # Validate sources
        for i, source in enumerate(profile.sources):
            if not source.path:
                errors.append(f"Source {i+1}: Path is required")
            elif not os.path.exists(source.path):
                errors.append(f"Source {i+1}: Path does not exist: {source.path}")
        
        # Validate destinations
        for i, dest in enumerate(profile.destinations):
            if not dest.target_path:
                errors.append(f"Destination {i+1}: Target path is required")
            
            if dest.auto_mount and not dest.drive_device:
                errors.append(f"Destination {i+1}: Drive device required for auto-mount")
        
        # Validate schedule
        if profile.schedule.enabled:
            if not (0 <= profile.schedule.hour <= 23):
                errors.append("Schedule hour must be between 0 and 23")
            if not (0 <= profile.schedule.minute <= 59):
                errors.append("Schedule minute must be between 0 and 59")
        
        return errors
    
    def _profile_to_dict(self, profile: BackupProfile) -> Dict[str, Any]:
        """Convert profile dataclass to dictionary."""
        return {
            "name": profile.name,
            "sources": [asdict(source) for source in profile.sources],
            "destinations": [asdict(dest) for dest in profile.destinations],
            "pre_commands": [asdict(cmd) for cmd in profile.pre_commands],
            "post_commands": [asdict(cmd) for cmd in profile.post_commands],
            "schedule": asdict(profile.schedule),
            "log_enabled": profile.log_enabled,
            "dry_run": profile.dry_run,
            "created_at": profile.created_at,
            "modified_at": profile.modified_at
        }
    
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
