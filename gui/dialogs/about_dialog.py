#!/usr/bin/env python3
"""
About Dialog for Concrete Backup
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap

from version import get_version_info
from localization.tr import tr


class AboutDialog(QDialog):
    """Dialog showing application information, version, and credits."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Setup the dialog UI."""
        self.setWindowTitle(tr("About Concrete Backup"))
        self.setModal(True)
        self.setFixedSize(500, 400)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Header section with app name and version
        header_layout = QVBoxLayout()
        
        # App name
        app_name_label = QLabel("Concrete Backup")
        app_name_font = QFont()
        app_name_font.setPointSize(18)
        app_name_font.setBold(True)
        app_name_label.setFont(app_name_font)
        app_name_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(app_name_label)

        # Version info
        version_info = get_version_info()
        version_label = QLabel(f"{tr('Version')}: {version_info['version']}")
        version_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(version_label)

        # Build info if available
        if version_info.get('build_date'):
            build_label = QLabel(f"{tr('Build Date')}: {version_info['build_date']}")
            build_label.setAlignment(Qt.AlignCenter)
            header_layout.addWidget(build_label)

        layout.addLayout(header_layout)

        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)

        # Description
        description_label = QLabel(tr("A comprehensive backup management system for Ubuntu."))
        description_label.setWordWrap(True)
        description_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(description_label)

        # Features section
        features_text = QTextEdit()
        features_text.setReadOnly(True)
        features_text.setMaximumHeight(120)
        features_content = f"""
<b>{tr('Features')}:</b>
<ul>
<li>{tr('Automatic and scheduled backups')}</li>
<li>{tr('Multiple destination support')}</li>
<li>{tr('Custom pre/post backup commands')}</li>
<li>{tr('Drive detection and auto-mounting')}</li>
<li>{tr('Comprehensive logging')}</li>
<li>{tr('User-friendly GUI interface')}</li>
</ul>
"""
        features_text.setHtml(features_content)
        layout.addWidget(features_text)

        # Credits section
        credits_label = QLabel(f"<b>{tr('Credits')}:</b>")
        layout.addWidget(credits_label)

        credits_text = QLabel()
        credits_text.setWordWrap(True)
        credits_text.setMaximumHeight(80)
        credits_content = f"""
{tr('App icon created by juicy_fish - Flaticon')}<br>
<a href="https://www.flaticon.com/free-icons/firewall">https://www.flaticon.com/free-icons/firewall</a><br><br>
{tr('Developed with PyQt5 and Python')}
"""
        credits_text.setText(credits_content)
        credits_text.setOpenExternalLinks(True)
        layout.addWidget(credits_text)

        # Button section
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_button = QPushButton(tr("Close"))
        close_button.clicked.connect(self.accept)
        close_button.setDefault(True)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)

    def show_dialog(self):
        """Show the about dialog."""
        self.exec_()
