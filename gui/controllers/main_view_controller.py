#!/usr/bin/env python3
"""
Main View Controller
Handles the main view operations and coordination.
"""

from typing import Optional
from PyQt5.QtWidgets import QMessageBox

from backup_config import BackupProfile
from managers.schedule_status_manager import ScheduleStatusManager
from gui.dialogs.backup_progress_dialog import BackupProgressDialog


class MainViewController:
    """Handles main view operations and coordination."""

    def __init__(self, parent_widget, schedule_status_manager: ScheduleStatusManager):
        self.parent_widget = parent_widget
        self.schedule_status_manager = schedule_status_manager

    def validate_profile_for_backup(self, profile: Optional[BackupProfile]) -> bool:
        """Validate if the profile is ready for backup."""
        if not profile:
            QMessageBox.warning(self.parent_widget, "No Profile", "No backup profile loaded!")
            return False

        if not profile.sources:
            QMessageBox.warning(
                self.parent_widget, "No Sources",
                "No backup sources defined. Please add at least one source directory."
            )
            return False

        if not profile.destinations:
            QMessageBox.warning(
                self.parent_widget, "No Destinations",
                "No backup destinations defined. Please add at least one destination."
            )
            return False

        return True

    def update_schedule_display(self, profile: Optional[BackupProfile],
                                schedule_mode_label, profile_info_group, truncate_text_func):
        """Update the schedule status display."""
        display_text, color = self.schedule_status_manager.get_schedule_display_info(profile)

        # Truncate text if needed
        truncated_text = truncate_text_func(display_text)
        schedule_mode_label.setText(truncated_text)

        # Set styling based on whether schedule is active
        is_active = self.schedule_status_manager.is_schedule_active(profile)
        if is_active:
            schedule_mode_label.setStyleSheet(f"font-size: 11px; color: {color}; font-weight: bold;")
            profile_info_group.setStyleSheet("QGroupBox { border: 2px solid #007ACC; }")
        else:
            schedule_mode_label.setStyleSheet(f"font-size: 11px; color: {color};")
            profile_info_group.setStyleSheet("QGroupBox { border: 2px solid #CCCCCC; }")

    def run_backup_now(self, profile: Optional[BackupProfile]):
        """Run backup immediately with progress dialog."""
        if not self.validate_profile_for_backup(profile):
            return

        # Show progress dialog
        progress_dialog = BackupProgressDialog(profile, self.parent_widget)
        progress_dialog.exec_()

    def toggle_schedule(self, profile: Optional[BackupProfile], state):
        """Handle schedule toggle."""
        if not self.validate_profile_for_backup(profile):
            # Reset the checkbox if validation fails
            if hasattr(self.parent_widget, 'schedule_enabled_cb'):
                self.parent_widget.schedule_enabled_cb.setChecked(False)
            return

        # Update profile and mark as dirty
        if hasattr(self.parent_widget, 'mark_profile_dirty'):
            self.parent_widget.mark_profile_dirty()
