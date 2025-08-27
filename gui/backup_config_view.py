#!/usr/bin/env python3
"""
Main Backup Configuration Widget - Refactored
"""

from typing import Optional

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QPushButton, QLabel,
    QCheckBox, QGroupBox, QMessageBox
)
from PyQt5.QtCore import Qt

from backup_config import BackupProfile
from drive_manager import DriveManager
from gui.tabs.sources_tab import SourcesTab
from gui.tabs.destinations_tab import DestinationsTab
from gui.tabs.schedule_tab import ScheduleTab
from gui.tabs.custom_commands_tab import CustomCommandsTab
from gui.controllers.profile_ui_controller import ProfileUIController
from gui.controllers.schedule_ui_controller import ScheduleUIController
from gui.dialogs.backup_progress_dialog import BackupProgressDialog
from gui.workers.backup_worker import BackupWorker


class BackupConfigView(QWidget):
    """Widget for configuring backup settings."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.drive_manager = DriveManager()

        # UI elements
        self.profile_name_label = None
        self.profile_status_label = None
        self.schedule_status_label = None
        self.schedule_enabled_cb = None
        self.dry_run_cb = None
        self.log_enabled_cb = None
        self.run_now_btn = None

        # Tabs
        self.sources_tab = None
        self.destinations_tab = None
        self.schedule_tab = None
        self.custom_commands_tab = None

        # Controllers
        self.profile_controller = None
        self.schedule_controller = None

        self.setup_ui()
        self.setup_controllers()

    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)

        # Profile info section
        profile_info_group = QGroupBox("Current Profile")
        profile_info_layout = QHBoxLayout(profile_info_group)

        self.profile_name_label = QLabel("No profile loaded")
        self.profile_name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        profile_info_layout.addWidget(self.profile_name_label)

        profile_info_layout.addStretch()

        # Profile buttons
        new_btn = QPushButton("New")
        new_btn.clicked.connect(self.create_new_profile)
        profile_info_layout.addWidget(new_btn)

        open_btn = QPushButton("Open")
        open_btn.clicked.connect(self.open_profile_file)
        profile_info_layout.addWidget(open_btn)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_current_profile)
        profile_info_layout.addWidget(save_btn)

        save_as_btn = QPushButton("Save As")
        save_as_btn.clicked.connect(self.save_profile_as)
        profile_info_layout.addWidget(save_as_btn)

        self.profile_status_label = QLabel("")
        profile_info_layout.addWidget(self.profile_status_label)

        layout.addWidget(profile_info_group)

        # Main tabs
        self.tabs = QTabWidget()

        self.sources_tab = SourcesTab(self)
        self.destinations_tab = DestinationsTab(self)
        self.schedule_tab = ScheduleTab(self)
        self.custom_commands_tab = CustomCommandsTab(self)

        self.tabs.addTab(self.sources_tab, "Sources")
        self.tabs.addTab(self.destinations_tab, "Destinations")
        self.tabs.addTab(self.schedule_tab, "Schedule")
        self.tabs.addTab(self.custom_commands_tab, "Custom Commands")

        layout.addWidget(self.tabs)

        # Configuration and actions section
        status_group = QGroupBox("Backup Configuration & Actions")
        status_layout = QVBoxLayout(status_group)

        # Options
        options_layout = QHBoxLayout()
        self.dry_run_cb = QCheckBox("Dry Run (don't actually copy files)")
        options_layout.addWidget(self.dry_run_cb)

        self.log_enabled_cb = QCheckBox("Enable detailed logging")
        options_layout.addWidget(self.log_enabled_cb)
        status_layout.addLayout(options_layout)

        # Schedule status
        schedule_status_layout = QHBoxLayout()
        self.schedule_status_label = QLabel("Schedule: Not configured")
        schedule_status_layout.addWidget(self.schedule_status_label)
        schedule_status_layout.addStretch()
        status_layout.addLayout(schedule_status_layout)

        # Schedule and backup controls
        schedule_control_layout = QHBoxLayout()
        self.schedule_enabled_cb = QCheckBox("Enable Scheduled Backup")
        schedule_control_layout.addWidget(self.schedule_enabled_cb)

        self.run_now_btn = QPushButton("Run Backup Now")
        self.run_now_btn.clicked.connect(self.run_backup_now)
        schedule_control_layout.addWidget(self.run_now_btn)

        status_layout.addLayout(schedule_control_layout)
        layout.addWidget(status_group)

    def setup_controllers(self):
        """Initialize controllers after UI is set up."""
        self.profile_controller = ProfileUIController(
            self, self.profile_name_label, self.profile_status_label
        )
        self.schedule_controller = ScheduleUIController(
            self, self.schedule_status_label, self.schedule_enabled_cb
        )

        # Register tabs with profile controller
        self.profile_controller.register_tabs(
            self.sources_tab, self.destinations_tab,
            self.schedule_tab, self.custom_commands_tab
        )

        # Connect schedule toggle
        self.schedule_enabled_cb.stateChanged.connect(self.toggle_schedule)

    @property
    def current_profile(self) -> Optional[BackupProfile]:
        """Get the current profile from profile controller."""
        return self.profile_controller.current_profile if self.profile_controller else None

    # Profile management methods - delegate to controller
    def create_new_profile(self):
        """Create a new backup profile."""
        if self.profile_controller.create_new_profile():
            self.load_profile_to_ui()

    def save_current_profile(self):
        """Save the current profile."""
        self.profile_controller.save_current_profile(
            self.dry_run_cb.isChecked(),
            self.log_enabled_cb.isChecked()
        )

    def save_profile_as(self):
        """Save the current profile to a new location."""
        self.profile_controller.save_profile_as(
            self.dry_run_cb.isChecked(),
            self.log_enabled_cb.isChecked()
        )

    def open_profile_file(self):
        """Open a profile from file."""
        if self.profile_controller.open_profile_file():
            self.load_profile_to_ui()

    def load_profile_to_ui(self):
        """Load current profile data into the UI."""
        self.profile_controller.load_profile_to_ui()

        # Update local UI elements
        if self.current_profile:
            self.dry_run_cb.setChecked(self.current_profile.dry_run)
            self.log_enabled_cb.setChecked(self.current_profile.log_enabled)
            self.schedule_controller.load_schedule_from_profile(self.current_profile)

    def toggle_schedule(self, state):
        """Toggle schedule enabled/disabled."""
        if not self.current_profile:
            self.schedule_enabled_cb.setChecked(False)
            return

        enabled = state == Qt.Checked
        result = self.schedule_controller.handle_schedule_toggle(
            enabled,
            self.current_profile,
            lambda: self.profile_controller.is_profile_saved()
        )

        if result == "save_required":
            # Save the profile first, then try again
            if self.save_current_profile():
                self.toggle_schedule(state)

    def run_backup_now(self):
        """Run backup immediately with progress dialog."""
        if not self.current_profile:
            QMessageBox.warning(self, "No Profile", "No profile loaded. Please create or open a profile first.")
            return

        try:
            # Create progress dialog
            progress_dialog = BackupProgressDialog(self)

            # Create backup worker
            backup_worker = BackupWorker(self.current_profile)

            # Connect signals
            backup_worker.progress_update.connect(progress_dialog.update_progress)
            backup_worker.status_update.connect(progress_dialog.update_status)
            backup_worker.finished.connect(progress_dialog.backup_finished)
            backup_worker.error.connect(progress_dialog.backup_error)

            # Start backup
            progress_dialog.start_backup(backup_worker)
            progress_dialog.exec_()

        except (ValueError, OSError, PermissionError) as e:
            QMessageBox.critical(self, "Backup Error", f"Failed to start backup: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Backup Error", f"Unexpected error starting backup: {str(e)}")
            import traceback
            traceback.print_exc()
