#!/usr/bin/env python3
"""
Cron Job Management
Handles creating, updating, and removing cron jobs for backup schedules.
"""

import os
import subprocess
import tempfile
from typing import List, Optional, Tuple
from pathlib import Path

from backup_config import BackupProfile, ScheduleConfig


class CronManager:
    """Manages cron jobs for backup scheduling."""
    
    def __init__(self, parent_widget=None):
        """Initialize the cron manager."""
        self.backup_script_path = Path(__file__).parent / "backup_engine.py"
        self.job_comment = "# Concrete Backup Job"
        self.parent_widget = parent_widget
    
    def generate_cron_expression(self, schedule: ScheduleConfig) -> str:
        """Generate a cron expression from schedule config."""
        if not schedule.enabled:
            return ""
        
        minute = str(schedule.minute)
        hour = str(schedule.hour)
        
        # Day of week: 0=Sunday in cron, but we use 0=Monday
        # Convert: our 0-6 (Mon-Sun) to cron 1-7 (Mon-Sun) and 0 (Sun)
        if schedule.days_of_week == list(range(7)):  # Daily
            day_of_week = "*"
        else:
            cron_days = []
            for day in schedule.days_of_week:
                if day == 6:  # Sunday
                    cron_days.append("0")
                else:
                    cron_days.append(str(day + 1))
            day_of_week = ",".join(cron_days)
        
        return f"{minute} {hour} * * {day_of_week}"
    
    def create_backup_script(self, profile_name: str) -> str:
        """Create a shell script that runs the backup with proper environment."""
        script_dir = Path.home() / ".config" / "concrete-backup" / "scripts"
        script_dir.mkdir(parents=True, exist_ok=True)
        
        script_path = script_dir / f"backup_{profile_name}.sh"
        
        # Get the path to the backup engine
        engine_path = Path(__file__).parent.absolute() / "backup_engine.py"
        
        # Get the current Python interpreter path
        python_path = subprocess.check_output([
            "which", "python3"
        ], text=True).strip()
        
        # Create the script content
        script_content = f"""#!/bin/bash
# Concrete Backup Script for profile: {profile_name}
# Generated automatically - do not edit manually

# Set environment
export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"
export HOME="{Path.home()}"

# Create log file if it doesn't exist
LOG_FILE="$HOME/.config/concrete-backup/cron.log"
mkdir -p "$(dirname "$LOG_FILE")"

# Log start time
echo "$(date): Starting backup for profile '{profile_name}'" >> "$LOG_FILE"

# Change to backup directory
cd "{Path(__file__).parent.absolute()}"

# Activate poetry environment and run backup
if poetry run python "{engine_path}" "{profile_name}"; then
    echo "$(date): Backup for '{profile_name}' completed successfully" >> "$LOG_FILE"
    exit 0
else
    EXIT_CODE=$?
    echo "$(date): Backup for '{profile_name}' failed with exit code: $EXIT_CODE" >> "$LOG_FILE"
    exit $EXIT_CODE
fi
"""
        
        # Write the script
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # Make it executable
        os.chmod(script_path, 0o755)
        
        return str(script_path)
    
    def get_current_crontab(self) -> str:
        """Get the current root crontab."""
        try:
            result = subprocess.run(['crontab', '-l'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout
            else:
                return ""  # No crontab exists
        except Exception:
            return ""
    
    def set_crontab(self, content: str) -> bool:
        """Set the root crontab content."""
        try:
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.cron') as f:
                f.write(content)
                temp_file = f.name
            
            result = subprocess.run(['crontab', temp_file], 
                                  capture_output=True, text=True)
            os.unlink(temp_file)
            return result.returncode == 0
        
        except (OSError, subprocess.SubprocessError, PermissionError) as e:
            print(f"Error setting crontab: {e}")
            if 'temp_file' in locals():
                try:
                    os.unlink(temp_file)
                except:
                    pass
            return False
    
    def remove_backup_jobs(self) -> bool:
        """Remove all concrete backup jobs from root crontab."""
        current_crontab = self.get_current_crontab()
        
        # Split into lines
        lines = current_crontab.split('\n')
        
        # Filter out backup job lines
        filtered_lines = []
        skip_next = False
        
        for line in lines:
            if self.job_comment in line:
                skip_next = True
                continue
            elif skip_next and line.strip() and not line.startswith('#'):
                skip_next = False
                continue
            else:
                skip_next = False
                if line.strip():  # Don't add empty lines
                    filtered_lines.append(line)
        
        # Set the new crontab
        new_content = '\n'.join(filtered_lines)
        if new_content and not new_content.endswith('\n'):
            new_content += '\n'
        
        return self.set_crontab(new_content)
    
    def add_backup_job(self, profile: BackupProfile) -> Tuple[bool, str]:
        """Add a backup job to root crontab."""
        if not profile.schedule.enabled:
            return False, "Schedule is not enabled"
        
        try:
            # Remove existing backup jobs first
            self.remove_backup_jobs()
            
            # Create the backup script
            script_path = self.create_backup_script(profile.name)
            
            # Generate cron expression
            cron_expr = self.generate_cron_expression(profile.schedule)
            
            # Get current crontab
            current_crontab = self.get_current_crontab()
            
            # Add the new job
            backup_job = f"{self.job_comment} - {profile.name}\n"
            backup_job += f"{cron_expr} {script_path}\n"
            
            new_crontab = current_crontab
            if new_crontab and not new_crontab.endswith('\n'):
                new_crontab += '\n'
            new_crontab += backup_job
            
            # Set the new crontab
            if self.set_crontab(new_crontab):
                return True, f"Backup job scheduled in root crontab: {cron_expr}"
            else:
                return False, "Failed to update crontab"
        
        except (OSError, subprocess.SubprocessError, PermissionError) as e:
            return False, f"Error adding backup job: {str(e)}"
    
    def get_backup_job_status(self) -> Optional[str]:
        """Get the current backup job status."""
        current_crontab = self.get_current_crontab()
        
        lines = current_crontab.split('\n')
        for i, line in enumerate(lines):
            if self.job_comment in line:
                # Next line should be the actual cron job
                if i + 1 < len(lines):
                    job_line = lines[i + 1].strip()
                    if job_line and not job_line.startswith('#'):
                        return job_line
        
        return None
    
    def is_backup_scheduled(self) -> bool:
        """Check if a backup job is currently scheduled."""
        return self.get_backup_job_status() is not None
    
    def validate_schedule(self, schedule: ScheduleConfig) -> List[str]:
        """Validate a schedule configuration."""
        errors = []
        
        if schedule.enabled:
            if not (0 <= schedule.hour <= 23):
                errors.append("Hour must be between 0 and 23")
            
            if not (0 <= schedule.minute <= 59):
                errors.append("Minute must be between 0 and 59")
            
            if schedule.days_of_week:
                for day in schedule.days_of_week:
                    if not (0 <= day <= 6):
                        errors.append("Days of week must be between 0 (Monday) and 6 (Sunday)")
        
        return errors
    
    def get_next_run_time(self, schedule: ScheduleConfig) -> Optional[str]:
        """Get a human-readable description of when the backup will next run."""
        if not schedule.enabled:
            return None
        
        try:
            from datetime import datetime, timedelta
            import calendar
            
            now = datetime.now()
            
            # Day names
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 
                        'Friday', 'Saturday', 'Sunday']
            
            # Format time
            time_str = f"{schedule.hour:02d}:{schedule.minute:02d}"
            
            # Daily backup
            if schedule.days_of_week == list(range(7)):
                # Find next occurrence
                target_time = now.replace(hour=schedule.hour, minute=schedule.minute, 
                                        second=0, microsecond=0)
                
                if target_time <= now:
                    target_time += timedelta(days=1)
                
                if target_time.date() == now.date():
                    return f"Today at {time_str}"
                elif target_time.date() == (now + timedelta(days=1)).date():
                    return f"Tomorrow at {time_str}"
                else:
                    return f"Daily at {time_str}"
            
            # Specific days
            else:
                days_str = ", ".join([day_names[day] for day in sorted(schedule.days_of_week)])
                return f"{days_str} at {time_str}"
        
        except Exception:
            return "Invalid schedule"
