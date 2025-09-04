#!/usr/bin/env python3
"""
UI Builder for Backup Configuration View
Separates UI creation logic from business logic.
"""

from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QTabWidget, QPushButton, QLabel,
    QCheckBox, QGroupBox, QWidget
)


class BackupConfigUIBuilder:
    """Builds UI components for the backup configuration view."""

    @staticmethod
    def create_complete_ui(parent_widget):
        """Create the complete UI for the backup configuration view."""
        layout = QVBoxLayout(parent_widget)

        # Create profile info section
        (profile_info_group, profile_name_label, schedule_mode_label,
         new_profile_btn, open_profile_btn, save_profile_btn, save_as_profile_btn) = (
            BackupConfigUIBuilder.create_profile_info_section()
        )

        layout.addWidget(profile_info_group)

        # Create tabs
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)

        # Create actions section
        (actions_layout, schedule_toggle_btn, run_now_btn) = (
            BackupConfigUIBuilder.create_actions_section()
        )
        layout.addLayout(actions_layout)

        return {
            'profile_info_group': profile_info_group,
            'profile_name_label': profile_name_label,
            'schedule_mode_label': schedule_mode_label,
            'new_profile_btn': new_profile_btn,
            'open_profile_btn': open_profile_btn,
            'save_profile_btn': save_profile_btn,
            'save_as_profile_btn': save_as_profile_btn,
            'tab_widget': tab_widget,
            'schedule_toggle_btn': schedule_toggle_btn,
            'run_now_btn': run_now_btn
        }

    @staticmethod
    def create_profile_info_section():
        """Create the profile information section."""
        profile_info_group = QGroupBox("")
        profile_info_group.setStyleSheet("QGroupBox { border: 2px solid #CCCCCC; }")
        profile_info_layout = QVBoxLayout(profile_info_group)

        # Profile name and status
        name_status_layout = QHBoxLayout()

        profile_name_container = QVBoxLayout()
        profile_name_label = QLabel("No profile loaded")
        profile_name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        profile_name_label.setWordWrap(False)
        profile_name_container.addWidget(profile_name_label)

        schedule_mode_label = QLabel("Manual Mode")
        schedule_mode_label.setStyleSheet("font-size: 11px; color: #666;")
        schedule_mode_label.setWordWrap(False)
        profile_name_container.addWidget(schedule_mode_label)

        name_status_layout.addLayout(profile_name_container)
        name_status_layout.addStretch()

        # Profile buttons
        buttons_layout = QHBoxLayout()
        new_profile_btn = QPushButton("New")
        open_profile_btn = QPushButton("Open")
        save_profile_btn = QPushButton("Save")
        save_as_profile_btn = QPushButton("Save As")

        buttons_layout.addWidget(new_profile_btn)
        buttons_layout.addWidget(open_profile_btn)
        buttons_layout.addWidget(save_profile_btn)
        buttons_layout.addWidget(save_as_profile_btn)
        buttons_layout.addStretch()

        name_status_layout.addLayout(buttons_layout)
        profile_info_layout.addLayout(name_status_layout)

        return (profile_info_group, profile_name_label, schedule_mode_label,
                new_profile_btn, open_profile_btn, save_profile_btn, save_as_profile_btn)

    @staticmethod
    def create_actions_section():
        """Create the actions section with schedule and run buttons in a horizontal layout."""
        # Main actions layout - horizontal for buttons
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(15)

        # Add stretch before buttons to center them
        actions_layout.addStretch()

        # Schedule button on the left
        schedule_toggle_btn = QPushButton("Enable Scheduling")
        schedule_toggle_btn.setCheckable(True)
        schedule_toggle_btn.setMinimumHeight(45)
        schedule_toggle_btn.setMinimumWidth(160)
        BackupConfigUIBuilder._apply_schedule_button_style(schedule_toggle_btn, enabled=False)
        actions_layout.addWidget(schedule_toggle_btn)

        # Run backup button on the right
        run_now_btn = QPushButton("Run Backup Now")
        run_now_btn.setMinimumHeight(45)
        run_now_btn.setMinimumWidth(160)
        run_now_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 12px 20px;
                border: 2px solid #388E3C;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #45a049;
                border: 2px solid #2E7D32;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
                border: 2px solid #cccccc;
            }
        """)
        actions_layout.addWidget(run_now_btn)

        # Add stretch after buttons to center them
        actions_layout.addStretch()

        return actions_layout, schedule_toggle_btn, run_now_btn

    @staticmethod
    def _apply_schedule_button_style(button: QPushButton, enabled: bool):
        """Apply styling to the schedule button based on enabled state."""
        if enabled:
            button.setText("Disable Scheduling")
            button.setStyleSheet("""
                QPushButton {
                    background-color: #FF6B6B;
                    color: white;
                    font-weight: bold;
                    font-size: 14px;
                    padding: 12px 20px;
                    border: 2px solid #FF5252;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #FF5252;
                    border: 2px solid #F44336;
                }
                QPushButton:disabled {
                    background-color: #cccccc;
                    color: #666666;
                    border: 2px solid #cccccc;
                }
            """)
            button.setChecked(True)
        else:
            button.setText("Enable Scheduling")
            button.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    font-weight: bold;
                    font-size: 14px;
                    padding: 12px 20px;
                    border: 2px solid #1976D2;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                    border: 2px solid #1565C0;
                }
                QPushButton:disabled {
                    background-color: #cccccc;
                    color: #666666;
                    border: 2px solid #cccccc;
                }
            """)
            button.setChecked(False)

    @staticmethod
    def apply_schedule_button_style(button: QPushButton, enabled: bool):
        """Public method to apply schedule button styling."""
        BackupConfigUIBuilder._apply_schedule_button_style(button, enabled)
