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
from cron_manager import CronManager
from gui.tabs.sources_tab import SourcesTab
from gui.tabs.destinations_tab import DestinationsTab
from gui.tabs.schedule_tab import ScheduleTab
from gui.tabs.custom_commands_tab import CustomCommandsTab
from gui.controllers.profile_ui_controller import ProfileUIController
from gui.controllers.schedule_ui_controller import ScheduleUIController
from gui.dialogs.backup_progress_dialog import BackupProgressDialog


class BackupConfigView(QWidget):
    """Widget for configuring backup settings."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.drive_manager = DriveManager()
        self.cron_manager = CronManager(parent_widget=self)

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

    def _truncate_text(self, text: str, max_length: int = 40) -> str:
        """Truncate text if it's too long, adding '...' at the end."""
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + "..."

    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)

        # Profile info section
        self.profile_info_group = QGroupBox("")
        # Set a gray border by default
        self.profile_info_group.setStyleSheet("QGroupBox { border: 2px solid #CCCCCC; }")
        profile_info_layout = QVBoxLayout(self.profile_info_group)

        # Profile name and status
        name_status_layout = QHBoxLayout()

        profile_name_container = QVBoxLayout()
        self.profile_name_label = QLabel("No profile loaded")
        self.profile_name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.profile_name_label.setWordWrap(False)
        profile_name_container.addWidget(self.profile_name_label)

        self.schedule_mode_label = QLabel("Manual Mode")
        self.schedule_mode_label.setStyleSheet("font-size: 11px; color: #666;")
        self.schedule_mode_label.setWordWrap(False)
        profile_name_container.addWidget(self.schedule_mode_label)

        name_status_layout.addLayout(profile_name_container)
        name_status_layout.addStretch()

        # Profile buttons
        buttons_layout = QHBoxLayout()
        new_btn = QPushButton("New")
        new_btn.clicked.connect(self.create_new_profile)
        buttons_layout.addWidget(new_btn)

        open_btn = QPushButton("Open")
        open_btn.clicked.connect(self.open_profile_file)
        buttons_layout.addWidget(open_btn)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_current_profile)
        buttons_layout.addWidget(save_btn)

        save_as_btn = QPushButton("Save As")
        save_as_btn.clicked.connect(self.save_profile_as)
        buttons_layout.addWidget(save_as_btn)

        self.profile_status_label = QLabel("")
        buttons_layout.addWidget(self.profile_status_label)

        name_status_layout.addLayout(buttons_layout)
        profile_info_layout.addLayout(name_status_layout)

        layout.addWidget(self.profile_info_group)

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
        self.status_group = QGroupBox("")
        status_layout = QVBoxLayout(self.status_group)

        # Options
        options_layout = QHBoxLayout()
        self.dry_run_cb = QCheckBox("Dry Run (don't actually copy files)")
        self.dry_run_cb.stateChanged.connect(self.on_profile_changed)
        options_layout.addWidget(self.dry_run_cb)

        self.log_enabled_cb = QCheckBox("Enable detailed logging")
        self.log_enabled_cb.stateChanged.connect(self.on_profile_changed)
        options_layout.addWidget(self.log_enabled_cb)
        options_layout.addStretch()
        status_layout.addLayout(options_layout)

        # Actions
        actions_layout = QHBoxLayout()

        # Schedule toggle button
        self.schedule_toggle_btn = QPushButton("Enable Scheduling")
        self.schedule_toggle_btn.setCheckable(True)
        self.schedule_toggle_btn.clicked.connect(self.toggle_schedule_button)
        self.update_schedule_button_style()
        actions_layout.addWidget(self.schedule_toggle_btn)

        actions_layout.addStretch()

        self.run_now_btn = QPushButton("Run Backup Now")
        self.run_now_btn.clicked.connect(self.run_backup_now)
        self.run_now_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border: 2px solid #45a049;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        actions_layout.addWidget(self.run_now_btn)

        status_layout.addLayout(actions_layout)
        layout.addWidget(self.status_group)

        # Initialize UI state (everything disabled until profile loaded)
        self.update_ui_state()

    def validate_profile_for_backup(self) -> bool:
        """
        Validate that the current profile has at least one source and one destination.
        Shows a message box and returns False if validation fails.
        """
        if not self.current_profile:
            QMessageBox.warning(self, "No Profile", "No profile loaded. Please create or open a profile first.")
            return False

        if not self.current_profile.sources:
            QMessageBox.warning(self, "No Sources", "No backup sources defined. Please add at least one source directory.")
            return False

        if not self.current_profile.destinations:
            QMessageBox.warning(
                self, "No Destinations",
                "No backup destinations defined. Please add at least one destination."
            )
            return False

        return True

    def update_ui_state(self):
        """Update the enabled/disabled state of UI elements based on profile status."""
        has_profile = self.current_profile is not None

        # Enable/disable tabs
        self.tabs.setEnabled(has_profile)

        # Enable/disable bottom section
        self.dry_run_cb.setEnabled(has_profile)
        self.log_enabled_cb.setEnabled(has_profile)
        self.schedule_toggle_btn.setEnabled(has_profile)
        self.run_now_btn.setEnabled(has_profile)

        # Apply visual styling for disabled state
        if has_profile:
            self.tabs.setStyleSheet("")
            self.status_group.setStyleSheet("")
        else:
            self.tabs.setStyleSheet("QTabWidget { color: #999999; }")
            self.status_group.setStyleSheet("QGroupBox { color: #999999; }")

    def setup_controllers(self):
        """Initialize controllers after UI is set up."""
        self.profile_controller = ProfileUIController(
            self, self.profile_name_label, self.profile_status_label
        )

        # Schedule controller - create dummy widgets since we use a button now
        dummy_label = QLabel()  # Not used anymore
        dummy_checkbox = QCheckBox()  # Not used anymore
        self.schedule_controller = ScheduleUIController(
            self, dummy_label, dummy_checkbox
        )

        # Register tabs with profile controller
        self.profile_controller.register_tabs(
            self.sources_tab, self.destinations_tab,
            self.schedule_tab, self.custom_commands_tab
        )

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

        # Update schedule status display
        self.update_schedule_status()

        # Update UI state (enable/disable elements)
        self.update_ui_state()

        # Mark as clean after loading (important: do this after all UI updates)
        if self.profile_controller:
            self.profile_controller.mark_clean()

    def on_profile_changed(self):
        """Called when any profile setting is changed."""
        if self.profile_controller and self.current_profile:
            self.profile_controller.mark_dirty()

    def mark_profile_dirty(self):
        """Public method for tabs to mark profile as dirty."""
        self.on_profile_changed()

    def has_unsaved_changes(self) -> bool:
        """Check if the current profile has unsaved changes."""
        if self.profile_controller:
            return self.profile_controller.is_profile_dirty()
        return False

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
        else:
            # Update the schedule tab's status display
            self.schedule_tab.update_cron_status()
            # Update the main view status as well
            self.update_schedule_status()

    def update_schedule_button_style(self):
        """Update the schedule button appearance based on state."""
        if not self.current_profile:
            enabled = False
        else:
            # Check if schedule is configured AND actually active in cron
            schedule_configured = self.current_profile.schedule.enabled
            cron_job_active = bool(self.cron_manager.get_backup_job_status())
            enabled = schedule_configured and cron_job_active

        if enabled:
            self.schedule_toggle_btn.setText("Disable Scheduling")
            self.schedule_toggle_btn.setStyleSheet("""
                QPushButton {
                    background-color: #FF6B6B;
                    color: white;
                    font-weight: bold;
                    padding: 8px 16px;
                    border: 2px solid #FF5252;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #FF5252;
                }
            """)
            self.schedule_toggle_btn.setChecked(True)
        else:
            self.schedule_toggle_btn.setText("Enable Scheduling")
            self.schedule_toggle_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    font-weight: bold;
                    padding: 8px 16px;
                    border: 2px solid #1976D2;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
            """)
            self.schedule_toggle_btn.setChecked(False)

    def toggle_schedule_button(self):
        """Handle schedule button toggle."""
        if not self.validate_profile_for_backup():
            self.schedule_toggle_btn.setChecked(False)
            self.update_schedule_button_style()
            return

        # Auto-save before enabling/disabling schedule
        if self.profile_controller.is_profile_dirty():
            if not self.save_current_profile():
                # If save failed, revert button state
                self.schedule_toggle_btn.setChecked(False)
                self.update_schedule_button_style()
                return
            # Continue with the action after successful save

        # Convert button state to checkbox state for compatibility
        new_state = Qt.Checked if self.schedule_toggle_btn.isChecked() else Qt.Unchecked

        # Call the existing toggle method
        self.toggle_schedule(new_state)

        # Update button appearance
        self.update_schedule_button_style()

    def update_schedule_status(self):
        """Update the schedule status display in the main view."""
        if not self.current_profile:
            self.schedule_mode_label.setText("Manual Mode")
            self.schedule_mode_label.setStyleSheet("font-size: 11px; color: #666;")
            self.profile_info_group.setStyleSheet("QGroupBox { border: 2px solid #CCCCCC; }")
        else:
            # Check if schedule is configured AND actually active in cron
            schedule_configured = self.current_profile.schedule.enabled
            cron_job_active = bool(self.cron_manager.get_backup_job_status())
            
            if schedule_configured and cron_job_active:
                # Get schedule details for display
                hour = self.current_profile.schedule.hour
                minute = self.current_profile.schedule.minute
                time_str = f"{hour:02d}:{minute:02d}"

                days_of_week = self.current_profile.schedule.days_of_week
                # Check if all 7 days are selected (Daily)
                if len(days_of_week) == 7 and set(days_of_week) == set(range(7)):
                    days_text = "Daily"
                elif len(days_of_week) == 0:
                    days_text = "Never"
                else:
                    day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
                    selected_days = [day_names[i] for i in sorted(days_of_week) if i < len(day_names)]
                    days_text = ", ".join(selected_days)

                schedule_text = f"Scheduled Mode - {time_str} {days_text}"
                truncated_text = self._truncate_text(schedule_text)
                self.schedule_mode_label.setText(truncated_text)
                self.schedule_mode_label.setStyleSheet("font-size: 11px; color: #007ACC; font-weight: bold;")
                self.profile_info_group.setStyleSheet("QGroupBox { border: 2px solid #007ACC; }")
            else:
                self.schedule_mode_label.setText("Manual Mode")
                self.schedule_mode_label.setStyleSheet("font-size: 11px; color: #666;")
                self.profile_info_group.setStyleSheet("QGroupBox { border: 2px solid #CCCCCC; }")

        # Update the schedule button appearance
        self.update_schedule_button_style()

    def run_backup_now(self):
        """Run backup immediately with progress dialog."""
        if not self.validate_profile_for_backup():
            return

        # Auto-save before running backup
        if self.profile_controller.is_profile_dirty():
            if not self.save_current_profile():
                # If save failed, don't run backup
                return
            # Continue with backup after successful save

        try:
            # Create and show progress dialog - pass the profile object directly
            progress_dialog = BackupProgressDialog(self.current_profile, self)
            progress_dialog.exec_()

        except (ValueError, OSError, PermissionError) as e:
            QMessageBox.critical(self, "Backup Error", f"Failed to start backup: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Backup Error", f"Unexpected error starting backup: {str(e)}")
            import traceback
            traceback.print_exc()
