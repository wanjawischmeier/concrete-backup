#!/usr/bin/env python3
"""
Profile UI Controller
Handles all profile-related UI operations and updates.
"""

from typing import Optional
from pathlib import Path

from PyQt5.QtWidgets import QWidget, QMessageBox, QLabel

from backup_config import BackupConfigManager, BackupProfile
from gui.profile_manager import ProfileManager


class ProfileUIController:
    """Controls profile-related UI operations."""

    def __init__(self, parent_widget: QWidget, profile_name_label: QLabel, profile_status_label: QLabel):
        """Initialize the profile UI controller."""
        self.parent_widget = parent_widget
        self.profile_name_label = profile_name_label
        self.profile_status_label = profile_status_label

        self.config_manager = BackupConfigManager()
        self.profile_manager = ProfileManager(parent_widget=parent_widget)

        # UI tabs that need to be notified of profile changes
        self.tabs = []

    def register_tabs(self, sources_tab, destinations_tab, schedule_tab, custom_commands_tab):
        """Register the tabs that need profile updates."""
        self.tabs = [sources_tab, destinations_tab, schedule_tab, custom_commands_tab]

    @property
    def current_profile(self) -> Optional[BackupProfile]:
        """Get the current profile."""
        return self.profile_manager.get_profile()

    @property
    def current_profile_path(self) -> Optional[str]:
        """Get the current profile path."""
        return self.profile_manager.get_profile_path()

    def create_new_profile(self) -> bool:
        """Create a new backup profile and update UI."""
        if self.profile_manager.create_new_profile():
            self.load_profile_to_ui()
            self.update_profile_display()
            return True
        return False

    def save_current_profile(self, dry_run_enabled: bool, log_enabled: bool) -> bool:
        """Save the current profile after validation."""
        if not self._validate_and_update_profile(dry_run_enabled, log_enabled):
            return False

        if self.profile_manager.save_current_profile():
            self.update_profile_display()
            return True
        return False

    def save_profile_as(self, dry_run_enabled: bool, log_enabled: bool) -> bool:
        """Save the current profile to a new location."""
        if not self._validate_and_update_profile(dry_run_enabled, log_enabled):
            return False

        if self.profile_manager.save_profile_as():
            self.update_profile_display()
            return True
        return False

    def open_profile_file(self) -> bool:
        """Open a profile from file and update UI."""
        if self.profile_manager.open_profile_file():
            self.load_profile_to_ui()
            self.update_profile_display()
            return True
        return False

    def load_profile_to_ui(self):
        """Load current profile data into all UI tabs."""
        if not self.current_profile:
            return

        # Load data into tabs
        for tab in self.tabs:
            if hasattr(tab, 'load_from_profile'):
                tab.load_from_profile(self.current_profile)

    def update_profile_from_ui(self, dry_run_enabled: bool, log_enabled: bool):
        """Update current profile with values from UI."""
        if not self.current_profile:
            return

        # Update from tabs
        for tab in self.tabs:
            if hasattr(tab, 'save_to_profile'):
                tab.save_to_profile(self.current_profile)

        # Update options
        self.current_profile.dry_run = dry_run_enabled
        self.current_profile.log_enabled = log_enabled

        # Update the profile manager's profile
        self.profile_manager.set_profile(self.current_profile)

    def update_profile_display(self):
        """Update the profile display information."""
        if self.current_profile:
            display_name = self.current_profile.name
            if self.current_profile_path:
                display_name += f" ({Path(self.current_profile_path).name})"

            self.profile_name_label.setText(display_name)
        else:
            self.profile_name_label.setText("No profile loaded")

    def _validate_and_update_profile(self, dry_run_enabled: bool, log_enabled: bool) -> bool:
        """Helper method to validate and update profile from UI."""
        if not self.current_profile:
            QMessageBox.warning(self.parent_widget, "Error", "No profile loaded!")
            return False

        self.update_profile_from_ui(dry_run_enabled, log_enabled)

        # Validate
        errors = self.config_manager.validate_profile(self.current_profile)
        if errors:
            QMessageBox.warning(
                self.parent_widget, 
                "Validation Error", 
                "Profile validation failed: " + ", ".join(errors)
            )
            return False

        return True

    def is_profile_saved(self) -> bool:
        """Check if the current profile has been saved."""
        return self.profile_manager.is_profile_saved()

    def has_profile(self) -> bool:
        """Check if there is a current profile."""
        return self.profile_manager.has_profile()
