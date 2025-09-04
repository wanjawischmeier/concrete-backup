#!/usr/bin/env python3
"""
Main Backup Configuration Widget - Simplified
"""

from typing import Optional

from PyQt5.QtWidgets import QWidget, QMessageBox

from backup_config import BackupProfile
from managers.drive_manager import DriveManager
from managers.cron_manager import CronManager
from managers.schedule_status_manager import ScheduleStatusManager
from gui.backup_config_ui_builder import BackupConfigUIBuilder
from gui.controllers.main_view_controller import MainViewController
from gui.tabs.sources_tab import SourcesTab
from gui.tabs.destinations_tab import DestinationsTab
from gui.tabs.schedule_tab import ScheduleTab
from gui.tabs.custom_commands_tab import CustomCommandsTab
from gui.controllers.profile_ui_controller import ProfileUIController
from gui.tabs.advanced_settings_tab import AdvancedSettingsTab
from gui.controllers.schedule_ui_controller import ScheduleUIController


class BackupConfigView(QWidget):
    """Simplified widget for configuring backup settings."""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Initialize managers
        self.drive_manager = DriveManager()
        self.cron_manager = CronManager(parent_widget=self)
        self.schedule_status_manager = ScheduleStatusManager(self.cron_manager)
        self.main_view_controller = MainViewController(self, self.schedule_status_manager)

        # Initialize UI and controllers
        self.setup_ui()
        self.setup_controllers()

        # Set initial UI state (disable tabs and buttons when no profile loaded)
        self.update_ui_state()

    def _truncate_text(self, text: str, max_length: int = 40) -> str:
        """Truncate text if it's too long, adding '...' at the end."""
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + "..."

    def setup_ui(self):
        """Setup the user interface using the UI builder."""
        ui_components = BackupConfigUIBuilder.create_complete_ui(self)

        # Store references to UI components
        self.profile_info_group = ui_components['profile_info_group']
        self.profile_name_label = ui_components['profile_name_label']
        self.schedule_mode_label = ui_components['schedule_mode_label']
        self.tab_widget = ui_components['tab_widget']
        self.schedule_toggle_btn = ui_components['schedule_toggle_btn']
        self.run_now_btn = ui_components['run_now_btn']
        self.save_profile_btn = ui_components['save_profile_btn']
        self.save_as_profile_btn = ui_components['save_as_profile_btn']

        # Connect signals
        ui_components['new_profile_btn'].clicked.connect(self.create_new_profile)
        ui_components['open_profile_btn'].clicked.connect(self.open_profile_file)
        self.save_profile_btn.clicked.connect(self.save_current_profile)
        self.save_as_profile_btn.clicked.connect(self.save_profile_as)
        self.schedule_toggle_btn.clicked.connect(self.toggle_schedule_button)
        self.run_now_btn.clicked.connect(self.run_backup_now)

        # Create tabs
        self.setup_tabs()

    def setup_tabs(self):
        """Setup the tab widgets."""
        self.sources_tab = SourcesTab(self)
        self.destinations_tab = DestinationsTab(self)
        self.schedule_tab = ScheduleTab(self)
        self.custom_commands_tab = CustomCommandsTab(self)
        self.advanced_settings_tab = AdvancedSettingsTab(self)

        self.tab_widget.addTab(self.sources_tab, self.tr("Sources"))
        self.tab_widget.addTab(self.destinations_tab, self.tr("Destinations"))
        self.tab_widget.addTab(self.schedule_tab, self.tr("Schedule"))
        self.tab_widget.addTab(self.custom_commands_tab, self.tr("Custom Commands"))
        self.tab_widget.addTab(self.advanced_settings_tab, self.tr("Advanced"))

    def setup_controllers(self):
        """Setup the controllers."""
        self.profile_controller = ProfileUIController(
            self, self.profile_name_label, None  # profile_status_label removed
        )
        self.schedule_controller = ScheduleUIController(
            self, self.schedule_mode_label, self.schedule_toggle_btn
        )

        # Register tabs with profile controller
        self.profile_controller.register_tabs([
            self.sources_tab, 
            self.destinations_tab, 
            self.schedule_tab, 
            self.custom_commands_tab, 
            self.advanced_settings_tab
        ])

    @property
    def current_profile(self) -> Optional[BackupProfile]:
        """Get the current profile from the controller."""
        return self.profile_controller.current_profile if self.profile_controller else None

    # Profile operations - delegate to controller
    def create_new_profile(self):
        """Create a new profile."""
        self.profile_controller.create_new_profile()
        self.update_ui_state()

    def save_current_profile(self):
        """Save the current profile."""
        return self.profile_controller.save_current_profile(
            self.advanced_settings_tab.get_dry_run_enabled(),
            self.advanced_settings_tab.get_log_enabled()
        )

    def save_profile_as(self):
        """Save the profile with a new name."""
        return self.profile_controller.save_profile_as(
            self.advanced_settings_tab.get_dry_run_enabled(),
            self.advanced_settings_tab.get_log_enabled()
        )

    def open_profile_file(self):
        """Open a profile file."""
        self.profile_controller.open_profile_file()
        self.load_profile_to_ui()

    def load_profile_to_ui(self):
        """Load the current profile to all UI components."""
        if self.current_profile:
            self.sources_tab.load_from_profile(self.current_profile)
            self.destinations_tab.load_from_profile(self.current_profile)
            self.schedule_tab.load_from_profile(self.current_profile)
            self.custom_commands_tab.load_from_profile(self.current_profile)
            self.advanced_settings_tab.load_from_profile(self.current_profile)

        self.update_schedule_status()
        self.update_ui_state()

    # UI state management
    def on_profile_changed(self):
        """Handle profile change events."""
        self.mark_profile_dirty()

    def mark_profile_dirty(self):
        """Mark the profile as having unsaved changes."""
        self.profile_controller.mark_dirty()

    def has_unsaved_changes(self) -> bool:
        """Check if there are unsaved changes."""
        return self.profile_controller.is_profile_dirty()

    def update_ui_state(self):
        """Update UI state based on current profile."""
        has_profile = self.current_profile is not None

        # Enable/disable action buttons
        self.schedule_toggle_btn.setEnabled(has_profile)
        self.run_now_btn.setEnabled(has_profile)

        # Enable/disable save buttons
        self.save_profile_btn.setEnabled(has_profile)
        self.save_as_profile_btn.setEnabled(has_profile)

        # Enable/disable tabs
        self.tab_widget.setEnabled(has_profile)

        # Update schedule button styling to ensure disabled state is properly styled
        if has_profile:
            self.update_schedule_button_style()
        else:
            # When no profile is loaded, ensure the button is styled as disabled
            from gui.backup_config_ui_builder import BackupConfigUIBuilder
            BackupConfigUIBuilder.apply_schedule_button_style(self.schedule_toggle_btn, False)

        # Update menu bar actions in the main window
        main_window = self.window()
        if hasattr(main_window, 'update_menu_state'):
            main_window.update_menu_state(has_profile)

    # Schedule operations - delegate to main view controller
    def toggle_schedule_button(self):
        """Handle schedule button toggle."""
        if not self.main_view_controller.validate_profile_for_backup(self.current_profile):
            self.schedule_toggle_btn.setChecked(False)
            self.update_schedule_button_style()
            return

        # Auto-save before toggling schedule
        if not self.save_current_profile():
            self.schedule_toggle_btn.setChecked(False)
            self.update_schedule_button_style()
            return

        # Update the profile's schedule enabled state
        is_enabled = self.schedule_toggle_btn.isChecked()
        if self.current_profile:
            self.current_profile.schedule.enabled = is_enabled

            if is_enabled:
                # Enable scheduling - add cron job
                success, message = self.cron_manager.add_backup_job(self.current_profile)
                if not success:
                    QMessageBox.warning(self, "Scheduling Error", f"Failed to schedule backup: {message}")
                    self.schedule_toggle_btn.setChecked(False)
                    self.current_profile.schedule.enabled = False
            else:
                # Disable scheduling - remove cron job
                self.cron_manager.remove_backup_jobs()

            # Update the schedule tab to reflect the changes
            self.schedule_tab.update_cron_status()

        self.update_schedule_status()

    def update_schedule_button_style(self):
        """Update the schedule button appearance based on state."""
        enabled = self.schedule_status_manager.is_schedule_active(self.current_profile)
        BackupConfigUIBuilder.apply_schedule_button_style(self.schedule_toggle_btn, enabled)

    def update_schedule_status(self):
        """Update the schedule status display in the main view."""
        self.main_view_controller.update_schedule_display(
            self.current_profile, self.schedule_mode_label,
            self.profile_info_group, self._truncate_text
        )
        self.update_schedule_button_style()

    # Backup operations - delegate to main view controller
    def run_backup_now(self):
        """Run backup immediately with progress dialog."""
        # Auto-save before running backup
        if not self.save_current_profile():
            return

        self.main_view_controller.run_backup_now(self.current_profile)
