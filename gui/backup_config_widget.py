#!/usr/bin/env python3
"""
Main Backup Configuration Widget
"""

from typing import Optional
from pathlib import Path

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QPushButton, QLabel,
    QCheckBox, QGroupBox, QMessageBox, QInputDialog, QFileDialog
)
from PyQt5.QtCore import Qt

from backup_config import BackupConfigManager, BackupProfile
from cron_manager import CronManager
from drive_manager import DriveManager
from gui.sources_tab import SourcesTab
from gui.destinations_tab import DestinationsTab
from gui.schedule_tab import ScheduleTab
from gui.custom_commands_tab import CustomCommandsTab


class BackupConfigWidget(QWidget):
    """Widget for configuring backup settings."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_manager = BackupConfigManager()
        self.cron_manager = CronManager(parent_widget=self)
        self.drive_manager = DriveManager()
        
        self.current_profile: Optional[BackupProfile] = None
        self.current_profile_path: Optional[str] = None
        
        self.setup_ui()
    
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
        
        self.profile_status_label = QLabel("")
        profile_info_layout.addWidget(self.profile_status_label)
        
        layout.addWidget(profile_info_group)
        
        # Main configuration tabs
        self.tabs = QTabWidget()
        
        # Create tab widgets
        self.sources_tab = SourcesTab(self)
        self.destinations_tab = DestinationsTab(self)
        self.schedule_tab = ScheduleTab(self)
        self.custom_commands_tab = CustomCommandsTab(self)
        
        self.tabs.addTab(self.sources_tab, "Source Directories")
        self.tabs.addTab(self.destinations_tab, "Destinations")
        self.tabs.addTab(self.schedule_tab, "Schedule")
        self.tabs.addTab(self.custom_commands_tab, "Custom Commands")
        
        # Connect schedule changes to update status AND cron job
        self.schedule_tab.schedule_time.timeChanged.connect(self.on_schedule_changed)
        for cb in self.schedule_tab.day_checkboxes:
            cb.stateChanged.connect(self.on_schedule_changed)
        self.schedule_tab.daily_cb.stateChanged.connect(self.on_schedule_changed)
        
        layout.addWidget(self.tabs)
        
        # Status and actions
        status_group = QGroupBox("Backup Configuration & Actions")
        status_layout = QVBoxLayout(status_group)
        
        # Backup options
        options_layout = QHBoxLayout()
        self.dry_run_cb = QCheckBox("Dry Run (don't actually copy files)")
        options_layout.addWidget(self.dry_run_cb)
        
        self.log_enabled_cb = QCheckBox("Enable detailed logging")
        self.log_enabled_cb.setChecked(True)
        options_layout.addWidget(self.log_enabled_cb)
        
        options_layout.addStretch()
        status_layout.addLayout(options_layout)
        
        # Schedule status
        self.schedule_status_label = QLabel("Schedule: Not configured")
        status_layout.addWidget(self.schedule_status_label)
        
        # Enable/disable toggle
        schedule_control_layout = QHBoxLayout()
        self.schedule_enabled_cb = QCheckBox("Enable Scheduled Backup")
        self.schedule_enabled_cb.stateChanged.connect(self.toggle_schedule)
        schedule_control_layout.addWidget(self.schedule_enabled_cb)
        
        self.run_now_btn = QPushButton("Run Backup Now")
        self.run_now_btn.clicked.connect(self.run_backup_now)
        schedule_control_layout.addWidget(self.run_now_btn)
        
        status_layout.addLayout(schedule_control_layout)
        
        layout.addWidget(status_group)
    
    # Profile management methods
    def create_new_profile(self):
        """Create a new backup profile."""
        name, ok = QInputDialog.getText(self, "New Profile", "Enter profile name:")
        if ok and name:
            existing_profiles = self.config_manager.list_profiles()
            if name in existing_profiles:
                QMessageBox.warning(self, "Error", f"Profile '{name}' already exists!")
                return
            
            self.current_profile = self.config_manager.create_profile(name)
            self.current_profile_path = None
            self.load_profile_to_ui()
            self.update_profile_display()
    
    def save_current_profile(self):
        """Save the current profile."""
        if not self.current_profile:
            QMessageBox.warning(self, "Error", "No profile loaded!")
            return
        
        self.update_profile_from_ui()
        
        # Validate
        errors = self.config_manager.validate_profile(self.current_profile)
        if errors:
            QMessageBox.warning(self, "Validation Error", 
                              "Profile validation failed: " + ", ".join(errors))
            return
        
        # If profile was loaded from file, ask if user wants to save to same location or new location
        if self.current_profile_path:
            reply = QMessageBox.question(
                self, "Save Profile",
                f"Save to existing location ({Path(self.current_profile_path).name}) or choose new location?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Cancel:
                return
            elif reply == QMessageBox.Yes:
                # Save to existing location
                try:
                    import yaml
                    profile_dict = self.config_manager._profile_to_dict(self.current_profile)
                    with open(self.current_profile_path, 'w') as f:
                        yaml.dump(profile_dict, f, default_flow_style=False)
                    QMessageBox.information(self, "Success", "Profile saved successfully!")
                    return
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to save profile: {str(e)}")
                    return
        
        # Save As - choose new location
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Profile As", 
            str(self.config_manager.profiles_dir / f"{self.current_profile.name}.yaml"),
            "YAML files (*.yaml *.yml);;JSON files (*.json);;All files (*)"
        )
        
        if file_path:
            try:
                import yaml
                import json
                
                path = Path(file_path)
                profile_dict = self.config_manager._profile_to_dict(self.current_profile)
                
                with open(file_path, 'w') as f:
                    if path.suffix.lower() == '.json':
                        json.dump(profile_dict, f, indent=2)
                    else:
                        yaml.dump(profile_dict, f, default_flow_style=False)
                
                self.current_profile_path = file_path
                self.update_profile_display()
                QMessageBox.information(self, "Success", f"Profile saved to {path.name}!")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save profile: {str(e)}")
        
        # Also save to the default profiles directory if not already there
        if not self.config_manager.save_profile(self.current_profile):
            print("Warning: Failed to save profile to default location")
    
    def save_profile_as(self):
        """Save the current profile to a specific location."""
        if not self.current_profile:
            QMessageBox.warning(self, "Error", "No profile loaded!")
            return
        
        self.update_profile_from_ui()
        
        # Validate
        errors = self.config_manager.validate_profile(self.current_profile)
        if errors:
            QMessageBox.warning(self, "Validation Error", 
                              "Profile validation failed: " + ", ".join(errors))
            return
        
        # Save As - choose new location
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Profile As", 
            str(self.config_manager.profiles_dir / f"{self.current_profile.name}.yaml"),
            "YAML files (*.yaml *.yml);;JSON files (*.json);;All files (*)"
        )
        
        if file_path:
            try:
                import yaml
                import json
                
                path = Path(file_path)
                profile_dict = self.config_manager._profile_to_dict(self.current_profile)
                
                with open(file_path, 'w') as f:
                    if path.suffix.lower() == '.json':
                        json.dump(profile_dict, f, indent=2)
                    else:
                        yaml.dump(profile_dict, f, default_flow_style=False)
                
                self.current_profile_path = file_path
                self.update_profile_display()
                QMessageBox.information(self, "Success", f"Profile saved to {path.name}!")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save profile: {str(e)}")
    
    def open_profile_file(self):
        """Open a profile from file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Profile", 
            str(self.config_manager.profiles_dir),
            "Profile files (*.yaml *.yml *.json);;All files (*)"
        )
        
        if file_path:
            try:
                import yaml
                import json
                
                path = Path(file_path)
                
                with open(file_path, 'r') as f:
                    if path.suffix.lower() == '.json':
                        profile_dict = json.load(f)
                    else:
                        profile_dict = yaml.safe_load(f)
                
                self.current_profile = self.config_manager._dict_to_profile(profile_dict)
                self.current_profile_path = file_path
                self.load_profile_to_ui()
                self.update_profile_display()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load profile: {str(e)}")
    
    def load_profile_to_ui(self):
        """Load current profile data into the UI."""
        if not self.current_profile:
            return
        
        # Load data into tabs
        self.sources_tab.load_from_profile(self.current_profile)
        self.destinations_tab.load_from_profile(self.current_profile)
        self.schedule_tab.load_from_profile(self.current_profile)
        self.custom_commands_tab.load_from_profile(self.current_profile)
        
        # Load options
        self.dry_run_cb.setChecked(self.current_profile.dry_run)
        self.log_enabled_cb.setChecked(self.current_profile.log_enabled)
        
        # Update schedule status
        self.schedule_enabled_cb.setChecked(self.current_profile.schedule.enabled)
        self.update_schedule_status()
    
    def update_profile_from_ui(self):
        """Update the current profile from UI values."""
        if not self.current_profile:
            return
        
        # Update from tabs
        self.sources_tab.save_to_profile(self.current_profile)
        self.destinations_tab.save_to_profile(self.current_profile)
        self.schedule_tab.save_to_profile(self.current_profile)
        self.custom_commands_tab.save_to_profile(self.current_profile)
        
        # Update options
        self.current_profile.dry_run = self.dry_run_cb.isChecked()
        self.current_profile.log_enabled = self.log_enabled_cb.isChecked()
    
    def update_profile_display(self):
        """Update the profile display information."""
        if self.current_profile:
            display_name = self.current_profile.name
            if self.current_profile_path:
                display_name += f" ({Path(self.current_profile_path).name})"
            
            self.profile_name_label.setText(display_name)
            
            # Update status
            if self.current_profile.schedule.enabled:
                self.profile_status_label.setText("Scheduled")
                self.profile_status_label.setStyleSheet("color: green;")
            else:
                self.profile_status_label.setText("Manual")
                self.profile_status_label.setStyleSheet("color: orange;")
        else:
            self.profile_name_label.setText("No profile loaded")
            self.profile_status_label.setText("")
    
    def on_schedule_changed(self):
        """Handle schedule changes and update cron job if enabled."""
        self.update_schedule_status()
        
        # If schedule is enabled and we have a profile, update the cron job
        if (self.current_profile and 
            self.current_profile.schedule.enabled and 
            self.schedule_enabled_cb.isChecked()):
            
            # Check if profile is saved before updating schedule
            if not self._is_profile_saved():
                # Silently skip updating cron job if profile isn't saved
                # The user will be prompted to save when they enable the schedule
                return
            
            # Update profile with current UI values
            self.update_profile_from_ui()
            
            # Remove old job and add new one
            if self.cron_manager.remove_backup_jobs(use_root=True):
                success, message = self.cron_manager.add_backup_job(self.current_profile, use_root=True)
                if not success and "cancelled" not in message.lower():
                    # Only show warning for non-cancellation errors
                    QMessageBox.warning(self, "Schedule Update Error", 
                                      f"Failed to update schedule: {message}")
    
    def toggle_schedule(self, state):
        """Enable or disable the backup schedule."""
        if not self.current_profile:
            return
        
        enabled = state == Qt.Checked
        
        if enabled:
            # Check if profile is saved before allowing scheduling
            if not self._is_profile_saved():
                reply = QMessageBox.question(
                    self, "Save Profile First",
                    "The profile must be saved before scheduling.\n\nWould you like to save it now?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )
                
                if reply == QMessageBox.Yes:
                    # Try to save the profile
                    self.save_current_profile()
                    # Check if it was actually saved
                    if not self._is_profile_saved():
                        # Save was cancelled or failed
                        self.schedule_enabled_cb.setChecked(False)
                        return
                else:
                    # User chose not to save
                    self.schedule_enabled_cb.setChecked(False)
                    return
            
            # Profile is saved, proceed with scheduling
            self.current_profile.schedule.enabled = enabled
            self.update_profile_from_ui()
            success, message = self.cron_manager.add_backup_job(self.current_profile, use_root=True)
            if not success:
                # Check if it was cancelled by user
                if "cancelled" in message.lower() or "password prompt cancelled" in message.lower():
                    # User cancelled, just disable the checkbox without showing error
                    self.schedule_enabled_cb.setChecked(False)
                    self.current_profile.schedule.enabled = False
                else:
                    # Show error for other failures
                    QMessageBox.critical(self, "Error", f"Failed to schedule backup: {message}")
                    self.schedule_enabled_cb.setChecked(False)
                    self.current_profile.schedule.enabled = False
        else:
            # Disabling schedule
            self.current_profile.schedule.enabled = enabled
            success = self.cron_manager.remove_backup_jobs(use_root=True)
            if not success:
                # Don't show error for cancellation when disabling
                pass
        
        self.update_schedule_status()
        self.update_profile_display()
        
        # Update the schedule tab status too
        self.schedule_tab.update_cron_status()
    
    def _is_profile_saved(self) -> bool:
        """Check if the current profile is saved to disk."""
        if not self.current_profile:
            return False
        
        # Check if profile exists in the default profiles directory
        profile_path = self.config_manager.profiles_dir / f"{self.current_profile.name}.yaml"
        if profile_path.exists():
            return True
        
        # Check if we have a specific file path (for Save As)
        if self.current_profile_path and Path(self.current_profile_path).exists():
            return True
        
        return False
    
    def update_schedule_status(self):
        """Update the schedule status display."""
        if not self.current_profile:
            self.schedule_status_label.setText("No profile loaded")
            return
        
        schedule = self.current_profile.schedule
        
        if schedule.enabled:
            next_run = self.cron_manager.get_next_run_time(schedule)
            self.schedule_status_label.setText(f"Schedule: {next_run or 'Active'}")
        else:
            self.schedule_status_label.setText("Schedule: Disabled")
    
    def run_backup_now(self):
        """Run backup immediately."""
        if not self.current_profile:
            QMessageBox.warning(self, "Error", "No profile loaded!")
            return
        
        # Check if profile is saved before running backup
        if not self._is_profile_saved():
            reply = QMessageBox.question(
                self, "Save Profile First",
                "The profile must be saved before running a backup.\n\nWould you like to save it now?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                # Try to save the profile
                self.save_current_profile()
                # Check if it was actually saved
                if not self._is_profile_saved():
                    # Save was cancelled or failed
                    return
            else:
                # User chose not to save
                return
        
        # Save profile first to ensure latest changes are persisted
        self.update_profile_from_ui()
        if not self.config_manager.save_profile(self.current_profile):
            QMessageBox.critical(self, "Error", "Failed to save profile!")
            return
        
        # Validate
        errors = self.config_manager.validate_profile(self.current_profile)
        if errors:
            QMessageBox.warning(self, "Validation Error", 
                              "Profile validation failed: " + ", ".join(errors))
            return
        
        # Show backup progress dialog
        from .backup_progress_dialog import BackupProgressDialog
        
        progress_dialog = BackupProgressDialog(self.current_profile.name, self)
        progress_dialog.exec_()
