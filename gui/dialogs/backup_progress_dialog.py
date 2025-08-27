#!/usr/bin/env python3
"""
Backup Progress Dialog
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QProgressBar, QMessageBox
)
from gui.workers.backup_worker import BackupWorker
from backup_config import BackupProfile


class BackupProgressDialog(QDialog):
    """Dialog showing backup progress."""

    def __init__(self, profile: BackupProfile, parent=None):
        super().__init__(parent)
        self.profile = profile
        self.worker = None
        self.backup_successful = False
        self.setup_ui()
        self.start_backup()

    def setup_ui(self):
        """Setup the dialog UI."""
        self.setWindowTitle("Backup Progress")
        self.setModal(True)
        self.resize(600, 400)

        layout = QVBoxLayout(self)

        # Status label
        self.status_label = QLabel("Preparing backup...")
        layout.addWidget(self.status_label)

        # Progress bar (indeterminate for now)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        layout.addWidget(self.progress_bar)

        # Log output
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

        # Buttons
        button_layout = QHBoxLayout()

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        self.close_button.setEnabled(False)  # Disabled until backup finishes
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

    def start_backup(self):
        """Start the backup process."""
        self.worker = BackupWorker(self.profile)

        # Connect signals
        self.worker.progress.connect(self.on_progress)
        self.worker.error.connect(self.on_error)
        self.worker.finished.connect(self.on_finished)
        self.worker.log_message.connect(self.on_log_message)  # Connect new signal

        # Start the worker
        self.worker.start()

    def on_log_message(self, message: str):
        """Handle detailed log messages from the backup engine."""
        self.log_text.append(message)

        # Scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def on_progress(self, message: str):
        """Handle progress updates."""
        self.status_label.setText(message)
        self.log_text.append(f"[INFO] {message}")

        # Scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def on_error(self, message: str):
        """Handle error messages."""
        self.log_text.append(f"[ERROR] {message}")

        # Scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def on_finished(self, success: bool, final_message: str):
        """Handle backup completion."""
        self.backup_successful = success
        self.status_label.setText(final_message)
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setValue(int(success))

        # Enable close button
        self.close_button.setEnabled(True)

    def closeEvent(self, event):
        """Handle dialog close event."""
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(self, "Backup Running",
                                         "Backup is still running. Are you sure you want to close?",
                                         QMessageBox.Yes | QMessageBox.No,
                                         QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.worker.terminate()
                self.worker.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
