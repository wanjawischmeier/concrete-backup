#!/usr/bin/env python3
"""
Drive selection widget for GUI components.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, 
    QGroupBox, QCheckBox
)
from PyQt5.QtCore import pyqtSignal

from drive_manager import DriveManager


class DriveSelectionWidget(QWidget):
    """Reusable widget for selecting drives."""

    driveSelected = pyqtSignal(object)  # Emits DriveInfo object

    def __init__(self, title="Drive Selection", show_auto_mount=False, parent=None):
        super().__init__(parent)
        self.drive_manager = DriveManager()
        self.title = title
        self.show_auto_mount = show_auto_mount
        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)

        # Drive selection section
        drive_group = QGroupBox(self.title)
        drive_layout = QVBoxLayout(drive_group)

        # Drive selection
        drive_selection_layout = QHBoxLayout()
        drive_selection_layout.addWidget(QLabel("Select Drive:"))

        self.drive_combo = QComboBox()
        self.drive_combo.currentTextChanged.connect(self.on_drive_selected)
        drive_selection_layout.addWidget(self.drive_combo)

        refresh_drives_btn = QPushButton("Refresh Drives")
        refresh_drives_btn.clicked.connect(self.refresh_drives)
        drive_selection_layout.addWidget(refresh_drives_btn)

        drive_layout.addLayout(drive_selection_layout)

        # Drive info
        self.drive_info_label = QLabel("No drive selected")
        drive_layout.addWidget(self.drive_info_label)

        # Auto-mount checkbox (only for destinations)
        if self.show_auto_mount:
            self.auto_mount_cb = QCheckBox("Auto-mount drive before backup")
            drive_layout.addWidget(self.auto_mount_cb)

        layout.addWidget(drive_group)

        # Initialize drives
        self.refresh_drives()

    def refresh_drives(self):
        """Refresh the list of available drives."""
        # Remember the currently selected drive
        current_drive = self.drive_combo.currentData()
        current_device = current_drive.device if current_drive else None

        self.drive_combo.clear()
        self.drive_combo.addItem("No drive selected", None)

        drives = self.drive_manager.refresh_drives()
        selected_index = 0  # Default to "No drive selected"

        for i, drive in enumerate(drives):
            display_text = f"{drive.device}"
            if drive.label:
                display_text += f" ({drive.label})"
            if drive.size:
                display_text += f" - {drive.size}"
            if drive.is_mounted and drive.mountpoint:
                display_text += f" - mounted at {drive.mountpoint}"

            self.drive_combo.addItem(display_text, drive)

            # Check if this is the previously selected drive
            if current_device and drive.device == current_device:
                selected_index = i + 1  # +1 because of "No drive selected" at index 0

        # Restore the previous selection
        self.drive_combo.setCurrentIndex(selected_index)

    def on_drive_selected(self, text):
        """Handle drive selection change."""
        drive = self.drive_combo.currentData()
        if drive:
            info_text = f"Device: {drive.device}\n"
            if drive.label:
                info_text += f"Label: {drive.label}\n"
            if drive.fstype:
                info_text += f"Filesystem: {drive.fstype}\n"
            if drive.size:
                info_text += f"Size: {drive.size}\n"
            info_text += f"Mounted: {'Yes' if drive.is_mounted else 'No'}"
            if drive.is_mounted and drive.mountpoint:
                info_text += f" at {drive.mountpoint}"

            self.drive_info_label.setText(info_text)
        else:
            self.drive_info_label.setText("No drive selected")

        # Emit signal
        self.driveSelected.emit(drive)

    def get_selected_drive(self):
        """Get the currently selected drive."""
        return self.drive_combo.currentData()

    def get_auto_mount(self):
        """Get auto-mount setting (if applicable)."""
        if self.show_auto_mount:
            return self.auto_mount_cb.isChecked()
        return False

    def set_auto_mount(self, enabled):
        """Set auto-mount setting (if applicable)."""
        if self.show_auto_mount:
            self.auto_mount_cb.setChecked(enabled)
