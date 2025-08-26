#!/usr/bin/env python3
"""
Command list widget for GUI components.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QGroupBox, QListWidget, QListWidgetItem, QInputDialog, QMessageBox
)
from PyQt5.QtCore import Qt


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
        
        self.add_button = QPushButton("Add Command")
        self.add_button.clicked.connect(self.add_command)
        buttons_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Edit Selected")
        self.edit_button.clicked.connect(self.edit_command)
        buttons_layout.addWidget(self.edit_button)
        
        self.remove_button = QPushButton("Remove Selected")
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
            item = QListWidgetItem(command.strip())
            item.setData(Qt.UserRole, command.strip())
            self.command_list.addItem(item)
    
    def edit_command(self):
        """Edit the selected command."""
        current_item = self.command_list.currentItem()
        if not current_item:
            QMessageBox.information(self, "No Selection", "Please select a command to edit.")
            return
        
        current_command = current_item.data(Qt.UserRole)
        command, ok = QInputDialog.getText(
            self, "Edit Command", 
            "Edit shell command:",
            text=current_command
        )
        
        if ok and command.strip():
            current_item.setText(command.strip())
            current_item.setData(Qt.UserRole, command.strip())
    
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
    
    def clear_commands(self):
        """Clear all commands from the list."""
        self.command_list.clear()
    
    def add_command_item(self, command: str):
        """Add a command item to the list."""
        item = QListWidgetItem(command)
        item.setData(Qt.UserRole, command)
        self.command_list.addItem(item)
    
    def get_commands(self) -> list:
        """Get all commands as a list."""
        commands = []
        for i in range(self.command_list.count()):
            item = self.command_list.item(i)
            commands.append(item.data(Qt.UserRole))
        return commands
    
    def set_commands(self, commands: list):
        """Set the commands list."""
        self.clear_commands()
        for command in commands:
            self.add_command_item(command)
