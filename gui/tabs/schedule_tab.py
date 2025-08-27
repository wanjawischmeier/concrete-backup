#!/usr/bin/env python3
"""
Schedule Tab for configuring backup schedules
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QGroupBox,
    QGridLayout, QTimeEdit
)
from PyQt5.QtCore import Qt, QTime

from backup_config import BackupProfile
from cron_manager import CronManager


class ScheduleTab(QWidget):
    """Tab for configuring backup schedule."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_widget = parent
        self.cron_manager = CronManager(parent_widget=parent)
        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)

        # Schedule settings
        schedule_group = QGroupBox("Backup Schedule")
        schedule_layout = QGridLayout(schedule_group)

        # Time
        schedule_layout.addWidget(QLabel("Time:"), 0, 0)
        self.schedule_time = QTimeEdit()
        self.schedule_time.setTime(QTime(2, 0))  # 2:00 AM default
        self.schedule_time.timeChanged.connect(self.on_schedule_changed)
        schedule_layout.addWidget(self.schedule_time, 0, 1)

        # Days of week
        schedule_layout.addWidget(QLabel("Days:"), 1, 0)

        days_widget = QWidget()
        days_layout = QHBoxLayout(days_widget)
        days_layout.setContentsMargins(0, 0, 0, 0)

        self.day_checkboxes = []
        day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for i, day in enumerate(day_names):
            cb = QCheckBox(day)
            cb.setChecked(True)  # Daily by default
            cb.stateChanged.connect(self.on_schedule_changed)
            self.day_checkboxes.append(cb)
            days_layout.addWidget(cb)

        days_layout.addStretch()
        schedule_layout.addWidget(days_widget, 1, 1)

        # Daily/Custom toggle
        self.daily_cb = QCheckBox("Daily backup")
        self.daily_cb.setChecked(True)
        self.daily_cb.stateChanged.connect(self.toggle_daily_backup)
        schedule_layout.addWidget(self.daily_cb, 2, 0, 1, 2)

        layout.addWidget(schedule_group)

        # Current status
        status_group = QGroupBox("Current Schedule Status")
        status_layout = QVBoxLayout(status_group)

        self.cron_status_label = QLabel("No backup scheduled")
        status_layout.addWidget(self.cron_status_label)

        layout.addWidget(status_group)

        layout.addStretch()

    def on_schedule_changed(self):
        """Called when schedule time or days change."""
        # Update the cron status to reflect changes
        self.update_cron_status()

        # If parent widget has a schedule status label, update it too
        if hasattr(self.parent_widget, 'update_schedule_status'):
            self.parent_widget.update_schedule_status()

        # Update the profile with current settings if we have one
        if (hasattr(self.parent_widget, 'current_profile') and
                self.parent_widget.current_profile):
            self.save_to_profile(self.parent_widget.current_profile)

    def toggle_daily_backup(self, state):
        """Toggle between daily and custom day selection."""
        is_daily = state == Qt.Checked
        for cb in self.day_checkboxes:
            cb.setEnabled(not is_daily)
            if is_daily:
                cb.setChecked(True)

        # Update status when toggling
        self.on_schedule_changed()

    def load_from_profile(self, profile: BackupProfile):
        """Load schedule from profile."""
        schedule = profile.schedule
        self.schedule_time.setTime(QTime(schedule.hour, schedule.minute))

        # Update day checkboxes
        if schedule.days_of_week == list(range(7)):
            self.daily_cb.setChecked(True)
            for cb in self.day_checkboxes:
                cb.setChecked(True)
                cb.setEnabled(False)
        else:
            self.daily_cb.setChecked(False)
            for i, cb in enumerate(self.day_checkboxes):
                cb.setChecked(i in schedule.days_of_week)
                cb.setEnabled(True)

        self.update_cron_status()

    def save_to_profile(self, profile: BackupProfile):
        """Save schedule to profile."""
        time = self.schedule_time.time()
        profile.schedule.hour = time.hour()
        profile.schedule.minute = time.minute()

        if self.daily_cb.isChecked():
            profile.schedule.days_of_week = list(range(7))
        else:
            profile.schedule.days_of_week = [
                i for i, cb in enumerate(self.day_checkboxes) if cb.isChecked()
            ]

    def update_cron_status(self):
        """Update the cron status display."""
        if (not self.parent_widget or
                not hasattr(self.parent_widget, 'current_profile') or
                not self.parent_widget.current_profile):
            self.cron_status_label.setText("No profile loaded")
            return

        # Check if schedule is enabled
        if not self.parent_widget.current_profile.schedule.enabled:
            self.cron_status_label.setText("Schedule disabled")
            return

        # Get current schedule info
        time = self.schedule_time.time()
        hour, minute = time.hour(), time.minute()

        if self.daily_cb.isChecked():
            days_text = "daily"
        else:
            selected_days = []
            day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            for i, cb in enumerate(self.day_checkboxes):
                if cb.isChecked():
                    selected_days.append(day_names[i])
            days_text = ", ".join(selected_days) if selected_days else "no days"

        # Format time
        time_str = f"{hour:02d}:{minute:02d}"

        self.cron_status_label.setText(f"Scheduled: {time_str} {days_text}")

        # Also check actual cron job status
        root_job = self.cron_manager.get_backup_job_status(use_root=True)
        if root_job:
            self.cron_status_label.setText(f"Active: {time_str} {days_text} (cron: {root_job})")
        else:
            self.cron_status_label.setText(f"Configured: {time_str} {days_text} (not in cron yet)")
