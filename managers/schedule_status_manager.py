#!/usr/bin/env python3
"""
Schedule Status Management
Centralizes schedule status logic to avoid duplication.
"""

from typing import Optional, Tuple
from backup_config import BackupProfile
from managers.cron_manager import CronManager


class ScheduleStatusManager:
    """Manages schedule status checking and formatting."""

    def __init__(self, cron_manager: CronManager):
        self.cron_manager = cron_manager

    def is_schedule_active(self, profile: Optional[BackupProfile]) -> bool:
        """Check if schedule is both configured and active in cron."""
        if not profile:
            return False

        schedule_configured = profile.schedule.enabled
        cron_job_active = bool(self.cron_manager.get_backup_job_status())
        return schedule_configured and cron_job_active

    def get_schedule_display_info(self, profile: Optional[BackupProfile]) -> Tuple[str, str]:
        """Get schedule display text and CSS color.

        Returns:
            Tuple of (display_text, css_color)
        """
        if not profile:
            return "Manual Mode", "#666"

        if self.is_schedule_active(profile):
            time_str = f"{profile.schedule.hour:02d}:{profile.schedule.minute:02d}"
            days_text = self._format_days(profile.schedule.days_of_week)
            return f"Scheduled Mode - {time_str} {days_text}", "#007ACC"
        else:
            return "Manual Mode", "#666"

    def _format_days(self, days_of_week: list) -> str:
        """Format days of week for display."""
        if len(days_of_week) == 7 and set(days_of_week) == set(range(7)):
            return "Daily"
        elif len(days_of_week) == 0:
            return "Never"
        else:
            day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            selected_days = [day_names[i] for i in sorted(days_of_week) if i < len(day_names)]
            return ", ".join(selected_days)
