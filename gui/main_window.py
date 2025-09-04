#!/usr/bin/env python3
"""
Main Window for Concrete Backup GUI
"""

from PyQt5.QtWidgets import QMainWindow, QMessageBox

from gui.backup_config_view import BackupConfigView
from version import get_version_info


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(self.tr("Concrete Backup"))
        self.setGeometry(100, 100, 700, 700)

        # Central widget
        self.backup_config = BackupConfigView()
        self.setCentralWidget(self.backup_config)

        # Create menu bar
        self.create_menu_bar()

        # Status bar
        self.statusBar()

        # Set initial menu state (no profile loaded initially)
        self.update_menu_state(False)

    def create_menu_bar(self):
        """Create the application menu bar."""
        menubar = self.menuBar()

        # Profile menu
        profile_menu = menubar.addMenu(self.tr('Profile'))

        new_action = profile_menu.addAction(self.tr('New Profile'))
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.backup_config.create_new_profile)

        profile_menu.addSeparator()

        open_action = profile_menu.addAction(self.tr('Open Profile...'))
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.backup_config.open_profile_file)

        # Store references to actions that should be disabled when no profile is loaded
        self.save_action = profile_menu.addAction(self.tr('Save Profile'))
        self.save_action.setShortcut('Ctrl+S')
        self.save_action.triggered.connect(self.backup_config.save_current_profile)

        self.save_as_action = profile_menu.addAction(self.tr('Save Profile As...'))
        self.save_as_action.setShortcut('Ctrl+Shift+S')
        self.save_as_action.triggered.connect(self.backup_config.save_profile_as)

        # Actions menu
        actions_menu = menubar.addMenu(self.tr('Actions'))

        self.run_now_action = actions_menu.addAction(self.tr('Run Backup Now'))
        self.run_now_action.setShortcut('F5')
        self.run_now_action.triggered.connect(self.backup_config.run_backup_now)

        # Help menu
        help_menu = menubar.addMenu(self.tr('Help'))

        about_action = help_menu.addAction(self.tr('About'))
        about_action.triggered.connect(self.show_about)

    def update_menu_state(self, has_profile: bool):
        """Update the enabled state of menu actions based on whether a profile is loaded."""
        self.save_action.setEnabled(has_profile)
        self.save_as_action.setEnabled(has_profile)
        self.run_now_action.setEnabled(has_profile)

    def show_about(self):
        """Show about dialog."""
        version_info = get_version_info()
        QMessageBox.about(self, "About Concrete Backup",
                          f"{version_info['full_name']}\n\n"
                          "A comprehensive backup management system for Ubuntu.\n\n"
                          "App icon created by juicy_fish - Flaticon\n"
                          "https://www.flaticon.com/free-icons/firewall")

    def closeEvent(self, event):
        """Handle window close event - check for unsaved changes."""
        # Check if there are unsaved changes
        if self.backup_config.has_unsaved_changes():
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save before exiting?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save
            )

            if reply == QMessageBox.Save:
                # Try to save
                if self.backup_config.save_current_profile():
                    event.accept()  # Save successful, allow close
                else:
                    event.ignore()  # Save failed, don't close
            elif reply == QMessageBox.Discard:
                event.accept()  # Don't save, allow close
            else:  # Cancel
                event.ignore()  # Don't close
        else:
            # No unsaved changes, allow close
            event.accept()
