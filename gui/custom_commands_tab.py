#!/usr/bin/env python3
"""
Custom Commands Tab for configuring pre/post backup commands
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel
)

from backup_config import BackupProfile
from .widgets import CommandListWidget


class CustomCommandsTab(QWidget):
    """Tab for configuring custom pre and post backup commands."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_widget = parent
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Info label
        info_label = QLabel(
            "Configure shell commands to run before and after backup operations.\n"
            "Commands are executed in the order they appear in the list."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; font-style: italic; margin-bottom: 10px;")
        layout.addWidget(info_label)
        
        # Pre-backup commands
        self.pre_commands_widget = CommandListWidget("Pre-Backup Commands")
        layout.addWidget(self.pre_commands_widget)
        
        # Post-backup commands
        self.post_commands_widget = CommandListWidget("Post-Backup Commands")
        layout.addWidget(self.post_commands_widget)
        
        layout.addStretch()
    
    def load_from_profile(self, profile: BackupProfile):
        """Load custom commands from profile."""
        self.pre_commands_widget.set_commands(profile.pre_commands)
        self.post_commands_widget.set_commands(profile.post_commands)
    
    def save_to_profile(self, profile: BackupProfile):
        """Save custom commands to profile."""
        profile.pre_commands = self.pre_commands_widget.get_commands()
        profile.post_commands = self.post_commands_widget.get_commands()
