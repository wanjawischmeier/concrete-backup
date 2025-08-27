#!/usr/bin/env python3
"""
Simple directory picker for root-privileged application.
"""

from typing import Optional

from PyQt5.QtWidgets import QFileDialog, QMessageBox, QWidget


class EnhancedDirectoryPicker:
    """Simple directory picker that works with root privileges."""

    @staticmethod
    def get_directory(parent: QWidget = None, 
                     caption: str = "Select Directory",
                     base_path: str = "/",
                     require_drive_selection: bool = False,
                     selected_drive = None) -> Optional[str]:
        """
        Get a directory path using the standard file dialog.

        Args:
            parent: Parent widget
            caption: Dialog title
            base_path: Starting directory
            require_drive_selection: Whether to require a drive to be selected first
            selected_drive: The currently selected drive (if any)

        Returns:
            Selected directory path or None if cancelled
        """
        # Check if drive selection is required
        if require_drive_selection and not selected_drive:
            QMessageBox.warning(
                parent,
                "No Drive Selected",
                "Please select a drive first before choosing directories.\n\n"
                "Use the drive selection dropdown to choose a drive."
            )
            return None

        # Use standard file dialog (works fine with root privileges)
        return QFileDialog.getExistingDirectory(parent, caption, base_path)
