#!/usr/bin/env python3
"""
Advanced Settings Tab
Contains advanced backup configuration options.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QCheckBox, QGroupBox, QLabel
)
from PyQt5.QtCore import QCoreApplication

from backup_config import BackupProfile
from localization.tr import tr


class AdvancedSettingsTab(QWidget):
    """Tab for advanced backup settings."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_widget = parent
        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)

        # Execution Options Group
        execution_group = QGroupBox(tr("Execution Options"))
        execution_layout = QVBoxLayout(execution_group)

        # Dry Run checkbox
        self.dry_run_cb = QCheckBox(tr("Dry Run"))
        self.dry_run_cb.setToolTip("Test mode - shows what would be backed up without actually copying files")
        self.dry_run_cb.stateChanged.connect(self.on_setting_changed)
        execution_layout.addWidget(self.dry_run_cb)

        # Logging checkbox
        self.log_enabled_cb = QCheckBox(tr("Enable Logging"))
        self.log_enabled_cb.setChecked(True)
        self.log_enabled_cb.setToolTip("Save backup operations to log files")
        self.log_enabled_cb.stateChanged.connect(self.on_setting_changed)
        execution_layout.addWidget(self.log_enabled_cb)

        layout.addWidget(execution_group)
        layout.addStretch()

    def on_setting_changed(self):
        """Handle setting changes."""
        if hasattr(self.parent_widget, 'on_profile_changed'):
            self.parent_widget.on_profile_changed()

    def load_from_profile(self, profile: BackupProfile):
        """Load settings from profile."""
        if profile:
            self.dry_run_cb.setChecked(profile.dry_run)
            self.log_enabled_cb.setChecked(profile.log_enabled)

    def save_to_profile(self, profile: BackupProfile):
        """Save settings to profile."""
        if profile:
            profile.dry_run = self.dry_run_cb.isChecked()
            profile.log_enabled = self.log_enabled_cb.isChecked()

    def get_dry_run_enabled(self) -> bool:
        """Get dry run setting."""
        return self.dry_run_cb.isChecked()

    def get_log_enabled(self) -> bool:
        """Get logging enabled setting."""
        return self.log_enabled_cb.isChecked()
