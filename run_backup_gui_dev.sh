#!/bin/bash
# Development startup script for Concrete Backup GUI
# Runs with sudo but no password prompt - for development use only

echo "Starting Concrete Backup GUI in development mode (with admin privileges)..."

# Get the absolute path to the script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Get the Poetry virtual environment Python path
POETRY_VENV_PYTHON=$(poetry env info --path)/bin/python

# Verify the virtual environment Python exists
if [ ! -f "$POETRY_VENV_PYTHON" ]; then
    echo "Error: Poetry virtual environment not found at $POETRY_VENV_PYTHON"
    echo "Please run 'poetry install' first."
    exit 1
fi

# Run with sudo using the exact command from sudoers (no password required)
sudo DISPLAY="$DISPLAY" XAUTHORITY="$XAUTHORITY" "$POETRY_VENV_PYTHON" "$SCRIPT_DIR/backup_gui.py"

echo "Concrete Backup GUI closed."
