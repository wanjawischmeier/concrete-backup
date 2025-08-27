#!/bin/bash
# Startup script for Concrete Backup GUI

echo "Starting Concrete Backup GUI with administrator privileges..."

# Get the absolute path to the script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Use pkexec for graphical sudo prompt (Ubuntu's built-in GUI)
# If pkexec fails, fall back to sudo with askpass
if command -v pkexec >/dev/null 2>&1; then
    # Use pkexec for GUI password prompt, ensuring we run from the correct directory
    pkexec env DISPLAY="$DISPLAY" XAUTHORITY="$XAUTHORITY" PATH="$PATH" PWD="$SCRIPT_DIR" bash -c "cd '$SCRIPT_DIR' && poetry run python backup_gui.py"
else
    # Fallback to sudo with graphical askpass
    export SUDO_ASKPASS=/usr/bin/ssh-askpass
    sudo -A -E bash -c "cd '$SCRIPT_DIR' && poetry run python backup_gui.py"
fi

echo "Concrete Backup GUI closed."
