#!/usr/bin/env python3
"""
Backup Worker for running backups in separate thread.
"""

from PyQt5.QtCore import QThread, pyqtSignal
from backup_engine import BackupEngine
from backup_config import BackupConfigManager


class BackupWorker(QThread):
    """Worker thread for running backups."""
    
    # Signals
    progress = pyqtSignal(str)  # Progress message
    error = pyqtSignal(str)     # Error message
    finished = pyqtSignal(bool, str)  # Success, final message
    
    def __init__(self, profile_name: str, parent=None):
        super().__init__(parent)
        self.profile_name = profile_name
        self.config_manager = BackupConfigManager()
    
    def run(self):
        """Run the backup in the background thread."""
        try:
            self.progress.emit(f"Starting backup for profile: {self.profile_name}")
            
            # Load profile
            profile = self.config_manager.load_profile(self.profile_name)
            if not profile:
                self.error.emit(f"Profile '{self.profile_name}' not found")
                self.finished.emit(False, "Profile not found")
                return
            
            # Validate profile
            errors = self.config_manager.validate_profile(profile)
            if errors:
                error_msg = "Profile validation failed: " + ", ".join(errors)
                self.error.emit(error_msg)
                self.finished.emit(False, error_msg)
                return
            
            # Initialize backup engine
            engine = BackupEngine(self.profile_name, self.config_manager)
            
            self.progress.emit(f"Backup engine initialized for {len(profile.sources)} sources")
            
            # Run backup for each destination
            total_success = True
            backup_results = []
            
            for i, destination in enumerate(profile.destinations):
                if not destination.enabled:
                    self.progress.emit(f"Skipping disabled destination: {destination.target_path}")
                    continue
                
                self.progress.emit(f"Backing up to destination {i+1}/{len(profile.destinations)}: {destination.target_path}")
                
                try:
                    success, message = engine.run_backup_to_destination(destination)
                    if success:
                        self.progress.emit(f"✓ Backup to {destination.target_path} completed successfully")
                        backup_results.append(f"✓ {destination.target_path}: Success")
                    else:
                        self.error.emit(f"✗ Backup to {destination.target_path} failed: {message}")
                        backup_results.append(f"✗ {destination.target_path}: {message}")
                        total_success = False
                        
                except Exception as e:
                    error_msg = f"Error backing up to {destination.target_path}: {str(e)}"
                    self.error.emit(error_msg)
                    backup_results.append(f"✗ {destination.target_path}: {str(e)}")
                    total_success = False
            
            # Final result
            final_message = f"Backup completed. Results:\n" + "\n".join(backup_results)
            self.finished.emit(total_success, final_message)
            
        except Exception as e:
            error_msg = f"Backup failed with error: {str(e)}"
            self.error.emit(error_msg)
            self.finished.emit(False, error_msg)
