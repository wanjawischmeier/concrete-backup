#!/usr/bin/env python3
"""
Schedule UI Controller
Handles all schedule-related UI operations.
"""

from PyQt5.QtWidgets import QWidget, QMessageBox, QLabel, QCheckBox

from backup_config import BackupProfile
from cron_manager import CronManager


class ScheduleUIController:
    """Controls schedule-related UI operations."""

    def __init__(self, parent_widget: QWidget, schedule_status_label: QLabel, schedule_enabled_cb: QCheckBox):
        """Initialize the schedule UI controller."""
        self.parent_widget = parent_widget
        self.schedule_status_label = schedule_status_label
        self.schedule_enabled_cb = schedule_enabled_cb

        self.cron_manager = CronManager(parent_widget=parent_widget)

        # Connect signals
        self.schedule_enabled_cb.stateChanged.connect(self.toggle_schedule)

    def on_schedule_changed(self, profile: BackupProfile, old_schedule):
        """Handle schedule changes."""
        # Update the cron job if the schedule changed
        if old_schedule != profile.schedule:
            if self.cron_manager.remove_backup_jobs():
                success, message = self.cron_manager.add_backup_job(profile)
                if not success and "cancelled" not in message.lower():
                    # Only show warning for non-cancellation errors
                    QMessageBox.warning(
                        self.parent_widget,
                        "Schedule Update Error",
                        f"Failed to update schedule: {message}"
                    )

    def toggle_schedule(self, state):
        """Toggle schedule enabled/disabled."""
        # This method will be connected to from the main widget
        # since it needs access to the profile
        pass

    def handle_schedule_toggle(self, enabled: bool, profile: BackupProfile, is_profile_saved_callback):
        """Handle the actual schedule toggle logic."""
        if enabled:
            # Enabling schedule
            if not is_profile_saved_callback():
                reply = QMessageBox.question(
                    self.parent_widget,
                    "Save Profile?",
                    "The profile must be saved before scheduling. Save now?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )

                if reply == QMessageBox.No:
                    # User doesn't want to save, revert checkbox
                    self.schedule_enabled_cb.setChecked(False)
                    return
                # If Yes, the main widget should save the profile first
                return "save_required"

            # Profile is saved, proceed with scheduling
            profile.schedule.enabled = enabled
            success, message = self.cron_manager.add_backup_job(profile)
            if not success:
                QMessageBox.warning(
                    self.parent_widget,
                    "Scheduling Error",
                    f"Failed to schedule backup: {message}"
                )
                self.schedule_enabled_cb.setChecked(False)
                profile.schedule.enabled = False
        else:
            # Disabling schedule
            profile.schedule.enabled = enabled
            success = self.cron_manager.remove_backup_jobs()
            if not success:
                # Don't show error for cancellation when disabling
                pass

    def update_schedule_status(self):
        """Update the schedule status display."""
        if self.cron_manager.is_backup_scheduled():
            job_status = self.cron_manager.get_backup_job_status()
            self.schedule_status_label.setText(f"✓ Scheduled: {job_status}")
        else:
            self.schedule_status_label.setText("✗ Not scheduled")

    def load_schedule_from_profile(self, profile: BackupProfile):
        """Load schedule settings from profile."""
        if profile and profile.schedule:
            self.schedule_enabled_cb.setChecked(profile.schedule.enabled)
        else:
            self.schedule_enabled_cb.setChecked(False)

        self.update_schedule_status()
