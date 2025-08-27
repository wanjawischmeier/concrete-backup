#!/usr/bin/env python3
"""
Profile Management Module
Handles loading, saving, and managing backup profiles.
"""

from typing import Optional

from PyQt5.QtWidgets import QWidget, QMessageBox, QInputDialog, QFileDialog

from backup_config import BackupConfigManager, BackupProfile


class ProfileManager:
    """Manages backup profile operations."""

    def __init__(self, parent_widget: QWidget = None):
        """Initialize the profile manager."""
        self.parent_widget = parent_widget
        self.config_manager = BackupConfigManager()
        self.current_profile: Optional[BackupProfile] = None
        self.current_profile_path: Optional[str] = None

    def create_new_profile(self) -> bool:
        """Create a new backup profile."""
        name, ok = QInputDialog.getText(
            self.parent_widget,
            "New Profile",
            "Enter profile name:"
        )

        if ok and name.strip():
            self.current_profile = self.config_manager.create_profile(name.strip())
            self.current_profile_path = None
            return True

        return False

    def save_current_profile(self) -> bool:
        """Save the current profile."""
        if not self.current_profile:
            QMessageBox.warning(
                self.parent_widget,
                "No Profile",
                "No profile to save. Create a new profile first."
            )
            return False

        if self.current_profile_path:
            # Save to existing file
            return self._save_to_file(self.current_profile_path)
        else:
            # No file path set, do "Save As"
            return self.save_profile_as()

    def save_profile_as(self) -> bool:
        """Save the current profile to a new file."""
        if not self.current_profile:
            QMessageBox.warning(
                self.parent_widget,
                "No Profile",
                "No profile to save. Create a new profile first."
            )
            return False

        # Get filename from user
        filename, _ = QFileDialog.getSaveFileName(
            self.parent_widget,
            "Save Profile As",
            f"{self.current_profile.name}.yaml",
            "YAML files (*.yaml *.yml);;All files (*)"
        )

        if filename:
            if self._save_to_file(filename):
                self.current_profile_path = filename
                return True

        return False

    def _save_to_file(self, file_path: str) -> bool:
        """Save the current profile to a specific file path."""
        try:
            from datetime import datetime

            # Update modification time
            self.current_profile.modified_at = datetime.now().isoformat()

            # Always save as YAML
            if self.config_manager.save_profile(self.current_profile, file_path):
                return True
            else:
                QMessageBox.critical(
                    self.parent_widget,
                    "Save Error",
                    "Failed to save profile file"
                )
                return False
        except Exception as e:
            QMessageBox.critical(
                self.parent_widget,
                "Save Error",
                f"Failed to save profile: {str(e)}"
            )
            return False

    def open_profile_file(self) -> bool:
        """Open a profile from file."""
        filename, _ = QFileDialog.getOpenFileName(
            self.parent_widget,
            "Open Profile",
            "",
            "YAML files (*.yaml *.yml);;All files (*)"
        )

        if filename:
            try:
                # Use the config manager's new load method
                profile = self.config_manager.load_profile_from_file(filename)
                if profile:
                    self.current_profile = profile
                    self.current_profile_path = filename
                    return True
                else:
                    QMessageBox.critical(self.parent_widget, "Error", "Failed to load profile file")
                    return False
            except Exception as e:
                QMessageBox.critical(
                    self.parent_widget,
                    "Error",
                    f"Failed to load profile: {str(e)}"
                )

        return False

    def is_profile_saved(self) -> bool:
        """Check if the current profile has been saved."""
        return self.current_profile_path is not None

    def has_profile(self) -> bool:
        """Check if there is a current profile."""
        return self.current_profile is not None

    def get_profile_name(self) -> str:
        """Get the current profile name."""
        if self.current_profile:
            return self.current_profile.name
        return "No profile loaded"

    def get_profile_path(self) -> Optional[str]:
        """Get the current profile file path."""
        return self.current_profile_path

    def get_profile(self) -> Optional[BackupProfile]:
        """Get the current profile."""
        return self.current_profile

    def set_profile(self, profile: BackupProfile):
        """Set the current profile."""
        self.current_profile = profile
