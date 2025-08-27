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
        self.setWindowTitle("Concrete Backup")
        self.setGeometry(100, 100, 700, 700)

        # Central widget
        self.backup_config = BackupConfigView()
        self.setCentralWidget(self.backup_config)

        # Create menu bar
        self.create_menu_bar()

        # Status bar
        self.statusBar()

    def create_menu_bar(self):
        """Create the application menu bar."""
        menubar = self.menuBar()

        # Profile menu
        profile_menu = menubar.addMenu('Profile')

        new_action = profile_menu.addAction('New Profile')
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.backup_config.create_new_profile)

        profile_menu.addSeparator()

        open_action = profile_menu.addAction('Open Profile...')
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.backup_config.open_profile_file)

        save_action = profile_menu.addAction('Save Profile')
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.backup_config.save_current_profile)

        save_as_action = profile_menu.addAction('Save Profile As...')
        save_as_action.setShortcut('Ctrl+Shift+S')
        save_as_action.triggered.connect(self.backup_config.save_profile_as)

        # Actions menu
        actions_menu = menubar.addMenu('Actions')

        run_now_action = actions_menu.addAction('Run Backup Now')
        run_now_action.setShortcut('F5')
        run_now_action.triggered.connect(self.backup_config.run_backup_now)

        # Help menu
        help_menu = menubar.addMenu('Help')

        about_action = help_menu.addAction('About')
        about_action.triggered.connect(self.show_about)

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
