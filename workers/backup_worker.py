#!/usr/bin/env python3
"""
Backup Worker Thread
"""

import logging
import sys
from PyQt5.QtCore import QThread, pyqtSignal
from backup_config import BackupProfile
from backup_engine import BackupEngine


class QtLogHandler(logging.Handler):
    """Custom logging handler that emits Qt signals."""

    def __init__(self, signal):
        super().__init__()
        self.signal = signal

    def emit(self, record):
        """Emit log record as Qt signal."""
        msg = self.format(record)
        self.signal.emit(msg)


class StdoutCapture:
    """Capture stdout and emit as Qt signal."""

    def __init__(self, signal):
        self.signal = signal
        self.original_stdout = sys.stdout

    def write(self, text):
        """Write to both original stdout and emit signal."""
        if text.strip():  # Only emit non-empty lines
            self.signal.emit(text.strip())
        self.original_stdout.write(text)

    def flush(self):
        """Flush original stdout."""
        self.original_stdout.flush()


class BackupWorker(QThread):
    """Worker thread for running backups in the background."""

    progress = pyqtSignal(str)
    error = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    log_message = pyqtSignal(str)  # New signal for detailed logs

    def __init__(self, profile: BackupProfile):
        super().__init__()
        self.profile = profile
        self.backup_engine = BackupEngine()

    def run(self):
        """Run the backup process."""
        try:
            self.progress.emit(f"Starting backup for profile: {self.profile.name}")

            # Setup logging capture
            self._setup_logging_capture()

            # Use the profile object directly instead of loading by name
            profile = self.profile

            if not profile:
                self.error.emit("Profile not found or failed to load")
                self.finished.emit(False, "Profile not found or failed to load")
                return

            success = self.backup_engine.run_backup(profile)
            if success:
                success_msg = "Backup completed successfully!"
                self.progress.emit(success_msg)
                self.finished.emit(True, success_msg)
            else:
                error_msg = "Backup failed - check logs for details"
                self.error.emit(error_msg)
                self.finished.emit(False, error_msg)

        except Exception as e:
            error_msg = f"Backup error: {str(e)}"
            self.error.emit(error_msg)
            self.finished.emit(False, error_msg)
        finally:
            # Restore stdout
            self._restore_stdout()

    def _setup_logging_capture(self):
        """Setup logging to capture backup engine output."""
        # Capture stdout (print statements)
        self.stdout_capture = StdoutCapture(self.log_message)
        sys.stdout = self.stdout_capture

        # Create a custom handler for loggers
        self.qt_handler = QtLogHandler(self.log_message)
        self.qt_handler.setLevel(logging.INFO)

        # Set up formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.qt_handler.setFormatter(formatter)

        # Add handler to root logger to catch all logging
        root_logger = logging.getLogger()
        root_logger.addHandler(self.qt_handler)
        root_logger.setLevel(logging.INFO)
        
        # Also add to backup-specific loggers to ensure we catch everything
        backup_logger = logging.getLogger('backup_engine')
        backup_logger.addHandler(self.qt_handler)
        backup_logger.setLevel(logging.INFO)

    def _restore_stdout(self):
        """Restore original stdout and remove logging handlers."""
        if hasattr(self, 'stdout_capture'):
            sys.stdout = self.stdout_capture.original_stdout

        if hasattr(self, 'qt_handler'):
            root_logger = logging.getLogger()
            root_logger.removeHandler(self.qt_handler)
            
            # Also remove from backup-specific loggers
            backup_logger = logging.getLogger('backup_engine')
            backup_logger.removeHandler(self.qt_handler)
