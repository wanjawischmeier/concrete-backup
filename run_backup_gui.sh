#!/bin/bash
# Startup script for Concrete Backup GUI

echo "Starting Concrete Backup GUI with administrator privileges..."

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

# Use pkexec for graphical sudo prompt (Ubuntu's built-in GUI)
# If pkexec fails, fall back to sudo with askpass
if command -v pkexec >/dev/null 2>&1; then
    # Use pkexec for GUI password prompt, using the Poetry virtual environment Python directly
    pkexec env DISPLAY="$DISPLAY" XAUTHORITY="$XAUTHORITY" PATH="$PATH" PWD="$SCRIPT_DIR" bash -c "cd '$SCRIPT_DIR' && '$POETRY_VENV_PYTHON' backup_gui.py"
else
    # Fallback to sudo with graphical askpass
    export SUDO_ASKPASS=/usr/bin/ssh-askpass
    sudo -A -E bash -c "cd '$SCRIPT_DIR' && '$POETRY_VENV_PYTHON' backup_gui.py"
fi

echo "Concrete Backup GUI closed."
