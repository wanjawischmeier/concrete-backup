#!/usr/bin/env python3
"""
Main Window for Concrete Backup GUI
"""

import sys
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtCore import Qt

from gui.backup_config_widget import BackupConfigWidget


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Concrete Backup")
        self.setGeometry(100, 100, 1000, 700)
        
        # Central widget
        self.backup_config = BackupConfigWidget()
        self.setCentralWidget(self.backup_config)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
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
        QMessageBox.about(self, "About Concrete Backup", 
                         "Concrete Backup v1.0\n\n"
                         "A comprehensive backup management system for Ubuntu.")
