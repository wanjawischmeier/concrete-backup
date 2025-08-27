#!/usr/bin/env python3
"""
Backup Runner
Thread for running backups in the background.
"""

from PyQt5.QtCore import QThread, pyqtSignal

from backup_engine import BackupEngine


class BackupRunner(QThread):
    """Thread for running backups without blocking the UI."""

    finished = pyqtSignal(bool, str)  # success, message

    def __init__(self, profile_name: str):
        super().__init__()
        self.profile_name = profile_name

    def run(self):
        """Run the backup in a separate thread."""
        try:
            engine = BackupEngine(self.profile_name)
            success = engine.run_backup()

            if success:
                self.finished.emit(True, "Backup completed successfully")
            else:
                self.finished.emit(False, "Backup completed with errors")

        except (ValueError, OSError, PermissionError) as e:
            self.finished.emit(False, f"Backup failed: {str(e)}")
        except KeyboardInterrupt:
            self.finished.emit(False, "Backup was interrupted")
        except Exception as e:
            self.finished.emit(False, f"Unexpected backup error: {str(e)}")
            import traceback
            traceback.print_exc()
