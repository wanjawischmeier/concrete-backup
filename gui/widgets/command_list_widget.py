#!/usr/bin/env python3
"""
Command list widget for GUI components.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QGroupBox, QListWidget, QListWidgetItem, QInputDialog, QMessageBox
)
from PyQt5.QtCore import Qt
from backup_config import CustomCommand


class CommandListWidget(QWidget):
    """Reusable widget for displaying and managing command lists."""

    def __init__(self, title="Commands", parent=None):
        super().__init__(parent)
        self.title = title
        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)

        # Command list
        list_group = QGroupBox(self.title)
        list_layout = QVBoxLayout(list_group)

        self.command_list = QListWidget()
        list_layout.addWidget(self.command_list)

        # Buttons
        buttons_layout = QHBoxLayout()

        self.add_button = QPushButton(self.tr("Add Command"))
        self.add_button.clicked.connect(self.add_command)
        buttons_layout.addWidget(self.add_button)

        self.edit_button = QPushButton(self.tr("Edit Selected"))
        self.edit_button.clicked.connect(self.edit_command)
        buttons_layout.addWidget(self.edit_button)

        self.remove_button = QPushButton(self.tr("Remove Selected"))
        self.remove_button.clicked.connect(self.remove_command)
        buttons_layout.addWidget(self.remove_button)

        buttons_layout.addStretch()
        list_layout.addLayout(buttons_layout)

        layout.addWidget(list_group)

    def add_command(self):
        """Add a new command."""
        command, ok = QInputDialog.getText(
            self, "Add Command",
            "Enter shell command:"
        )

        if ok and command.strip():
            # Create a CustomCommand object
            custom_cmd = CustomCommand(command=command.strip(), description=command.strip())
            item = QListWidgetItem(command.strip())
            item.setData(Qt.UserRole, custom_cmd)
            self.command_list.addItem(item)

            # Notify parent of change
            self._notify_parent_of_change()

    def edit_command(self):
        """Edit the selected command."""
        current_item = self.command_list.currentItem()
        if not current_item:
            QMessageBox.information(self, "No Selection", "Please select a command to edit.")
            return

        current_cmd_obj = current_item.data(Qt.UserRole)
        # Handle both CustomCommand objects and strings for backward compatibility
        if isinstance(current_cmd_obj, CustomCommand):
            current_command = current_cmd_obj.command
        else:
            current_command = str(current_cmd_obj)

        command, ok = QInputDialog.getText(
            self, "Edit Command",
            "Edit shell command:",
            text=current_command
        )

        if ok and command.strip():
            # Create a new CustomCommand object
            custom_cmd = CustomCommand(command=command.strip(), description=command.strip())
            current_item.setText(command.strip())
            current_item.setData(Qt.UserRole, custom_cmd)

            # Notify parent of change
            self._notify_parent_of_change()

    def remove_command(self):
        """Remove the selected command."""
        current_item = self.command_list.currentItem()
        if not current_item:
            QMessageBox.information(self, "No Selection", "Please select a command to remove.")
            return

        reply = QMessageBox.question(
            self, "Confirm Removal",
            f"Remove command: {current_item.text()}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            row = self.command_list.row(current_item)
            self.command_list.takeItem(row)

            # Notify parent of change
            self._notify_parent_of_change()

    def clear_commands(self):
        """Clear all commands from the list."""
        self.command_list.clear()

    def add_command_item(self, command):
        """Add a command item to the list."""
        # Handle both CustomCommand objects and strings
        if isinstance(command, CustomCommand):
            item = QListWidgetItem(command.command)
            item.setData(Qt.UserRole, command)
        else:
            # Convert string to CustomCommand for backward compatibility
            custom_cmd = CustomCommand(command=str(command), description=str(command))
            item = QListWidgetItem(str(command))
            item.setData(Qt.UserRole, custom_cmd)
        self.command_list.addItem(item)

    def get_commands(self) -> list:
        """Get all commands as a list of CustomCommand objects."""
        commands = []
        for i in range(self.command_list.count()):
            item = self.command_list.item(i)
            cmd_data = item.data(Qt.UserRole)
            # Ensure we return CustomCommand objects
            if isinstance(cmd_data, CustomCommand):
                commands.append(cmd_data)
            else:
                # Convert string to CustomCommand for backward compatibility
                custom_cmd = CustomCommand(command=str(cmd_data), description=str(cmd_data))
                commands.append(custom_cmd)
        return commands

    def set_commands(self, commands: list):
        """Set the commands list."""
        self.clear_commands()
        for command in commands:
            self.add_command_item(command)

    def _notify_parent_of_change(self):
        """Notify parent widget that commands have changed."""
        # Walk up the parent chain to find the tab, then the main view
        parent = self.parent()
        while parent:
            if hasattr(parent, 'parent_widget') and hasattr(parent.parent_widget, 'mark_profile_dirty'):
                parent.parent_widget.mark_profile_dirty()
                break
            parent = parent.parent()
