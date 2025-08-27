#!/usr/bin/env python3
"""
Sources Tab for selecting source directories with drive-specific functionality
"""

from typing import Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QMessageBox
)

from backup_config import BackupProfile, BackupSource
from gui.widgets.drive_selection_widget import DriveSelectionWidget
from gui.widgets.directory_list_widget import DirectoryListWidget
from gui.widgets.directory_picker import EnhancedDirectoryPicker
from managers.drive_manager import DriveManager


class SourcesTab(QWidget):
    """Tab for configuring source directories."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_widget = parent
        self.current_drive = None
        self.drive_manager = DriveManager()
        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)

        # Drive selection widget
        self.drive_selector = DriveSelectionWidget("Source Drive Selection")
        self.drive_selector.driveSelected.connect(self.on_drive_selected)
        layout.addWidget(self.drive_selector)

        # Sources directory list widget
        self.sources_list = DirectoryListWidget("Source Directories")
        self.sources_list.connect_buttons(
            self.add_source_directory,
            self.remove_source_directory
        )
        layout.addWidget(self.sources_list)

    def on_drive_selected(self, drive):
        """Handle drive selection change."""
        self.current_drive = drive

    def add_source_directory(self):
        """Add a source directory from the selected drive."""
        drive = self.current_drive

        if not self.parent_widget.current_profile:
            QMessageBox.warning(self, "No Profile", "Please create or load a profile first.")
            return

        # Determine base path for browsing
        if drive and drive.is_mounted:
            base_path = drive.mountpoint
        else:
            base_path = "/"

        directory = EnhancedDirectoryPicker.get_directory(
            self, "Select Source Directory", base_path,
            require_drive_selection=True, selected_drive=drive
        )

        if directory:
            source = BackupSource(path=directory)
            self.parent_widget.current_profile.sources.append(source)
            self.load_from_profile(self.parent_widget.current_profile)

            # Mark profile as dirty
            if hasattr(self.parent_widget, 'mark_profile_dirty'):
                self.parent_widget.mark_profile_dirty()

    def remove_source_directory(self):
        """Remove selected source directory."""
        source = self.sources_list.get_selected_item_data()
        if source and self.parent_widget.current_profile:
            self.parent_widget.current_profile.sources.remove(source)
            self.load_from_profile(self.parent_widget.current_profile)

            # Mark profile as dirty
            if hasattr(self.parent_widget, 'mark_profile_dirty'):
                self.parent_widget.mark_profile_dirty()

    def _get_drive_for_path(self, path: str) -> Optional[str]:
        """Get drive info for a given path."""
        # Refresh drives to get current mounts
        drives = self.drive_manager.refresh_drives()

        # Find the drive that contains this path
        best_match = None
        best_length = 0

        for drive in drives:
            if drive.is_mounted and drive.mountpoint:
                if path.startswith(drive.mountpoint):
                    # Find the longest matching mountpoint (most specific)
                    if len(drive.mountpoint) > best_length:
                        best_match = drive
                        best_length = len(drive.mountpoint)

        return f"{best_match.device} → " if best_match else ""

    def load_from_profile(self, profile: BackupProfile):
        """Load sources from profile."""
        self.sources_list.clear_items()
        for source in profile.sources:
            # Get drive info for this path
            drive_info = self._get_drive_for_path(source.path)

            self.sources_list.add_item(
                f"{'✓' if source.enabled else '✗'} {drive_info}{source.path}",
                source
            )

    def save_to_profile(self, profile: BackupProfile):
        """Save sources to profile."""
        # Sources are already saved to profile objects
        pass
