#!/bin/bash
set -e

case "$1" in
    remove|upgrade|deconfigure)
        echo "Cleaning up Concrete Backup..."
        # Remove any created cron jobs
        if command -v crontab >/dev/null 2>&1; then
            # Remove jobs for all users who might have them
            for user_home in /home/*; do
                if [ -d "$user_home" ]; then
                    user=$(basename "$user_home")
                    sudo -u "$user" crontab -l 2>/dev/null | grep -v "concrete-backup" | sudo -u "$user" crontab - 2>/dev/null || true
                fi
            done
            # Also clean root crontab
            crontab -l 2>/dev/null | grep -v "concrete-backup" | crontab - 2>/dev/null || true
        fi
        ;;
esac

exit 0
