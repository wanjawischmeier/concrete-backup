#!/usr/bin/env python3
"""
Destinations Tab for selecting backup destinations with drive-specific functionality
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton,
    QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt

from backup_config import BackupProfile, BackupDestination
from .widgets import DriveSelectionWidget, DirectoryListWidget
from drive_manager import DriveManager


class DestinationsTab(QWidget):
    """Tab for configuring backup destinations."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_widget = parent
        self.current_drive = None
        self.drive_manager = DriveManager()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Drive selection widget with auto-mount option
        self.drive_selector = DriveSelectionWidget("Destination Drive Selection", show_auto_mount=True)
        self.drive_selector.driveSelected.connect(self.on_drive_selected)
        layout.addWidget(self.drive_selector)
        
        # Destinations directory list widget
        self.destinations_list = DirectoryListWidget("Backup Destinations")
        self.destinations_list.connect_buttons(
            self.add_destination,
            self.remove_destination
        )
        layout.addWidget(self.destinations_list)
    
    def on_drive_selected(self, drive):
        """Handle drive selection change."""
        self.current_drive = drive
    
    def add_destination(self):
        """Add a destination with the selected drive and configuration."""
        if not self.parent_widget.current_profile:
            QMessageBox.warning(self, "No Profile", "Please create or load a profile first.")
            return
        
        drive = self.current_drive
        
        # Determine base path for browsing
        if drive and drive.is_mounted:
            base_path = f"{drive.mountpoint}/backup"
        else:
            base_path = "/"
        
        directory = QFileDialog.getExistingDirectory(
            self, "Select Destination Directory", base_path
        )
        
        if directory:
            destination = BackupDestination(
                drive_device=drive.device if drive else "",
                mount_point=drive.mountpoint if drive else "",
                target_path=directory,
                auto_mount=self.drive_selector.get_auto_mount()
            )
            self.parent_widget.current_profile.destinations.append(destination)
            self.load_from_profile(self.parent_widget.current_profile)
    def remove_destination(self):
        """Remove selected destination."""
        dest = self.destinations_list.get_selected_item_data()
        if dest and self.parent_widget.current_profile:
            self.parent_widget.current_profile.destinations.remove(dest)
            self.load_from_profile(self.parent_widget.current_profile)
    
    def load_from_profile(self, profile: BackupProfile):
        """Load destinations from profile."""
        self.destinations_list.clear_items()
        for dest in profile.destinations:
            # Include partition info if available
            if dest.drive_device and dest.mount_point:
                text = f"{'✓' if dest.enabled else '✗'} {dest.drive_device} → {dest.target_path}"
                if dest.auto_mount:
                    text += " (auto-mount)"
            else:
                text = f"{'✓' if dest.enabled else '✗'} {dest.target_path}"
            
            self.destinations_list.add_item(text, dest)
    
    def save_to_profile(self, profile: BackupProfile):
        """Save destinations to profile."""
        # Destinations are already saved to profile objects
        pass
