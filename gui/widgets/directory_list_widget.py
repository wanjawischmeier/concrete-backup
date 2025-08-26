#!/usr/bin/env python3
"""
Directory list widget for GUI components.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QGroupBox, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt


class DirectoryListWidget(QWidget):
    """Reusable widget for displaying and managing directories."""
    
    def __init__(self, title="Directories", parent=None):
        super().__init__(parent)
        self.title = title
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Directory list
        list_group = QGroupBox(self.title)
        list_layout = QVBoxLayout(list_group)
        
        self.directory_list = QListWidget()
        list_layout.addWidget(self.directory_list)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Add Directory")
        buttons_layout.addWidget(self.add_button)
        
        self.remove_button = QPushButton("Remove Selected")
        buttons_layout.addWidget(self.remove_button)
        
        buttons_layout.addStretch()
        list_layout.addLayout(buttons_layout)
        
        layout.addWidget(list_group)
    
    def clear_items(self):
        """Clear all items from the list."""
        self.directory_list.clear()
    
    def add_item(self, text, data=None):
        """Add an item to the list."""
        item = QListWidgetItem(text)
        if data:
            item.setData(Qt.UserRole, data)
        self.directory_list.addItem(item)
    
    def get_selected_item_data(self):
        """Get the data of the currently selected item."""
        current_item = self.directory_list.currentItem()
        if current_item:
            return current_item.data(Qt.UserRole)
        return None
    
    def connect_buttons(self, add_callback, remove_callback):
        """Connect the add and remove buttons to callbacks."""
        self.add_button.clicked.connect(add_callback)
        self.remove_button.clicked.connect(remove_callback)
