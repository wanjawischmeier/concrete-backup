#!/bin/bash

# Concrete Backup - GUI Launcher with privilege escalation
EXECUTABLE="/opt/concrete-backup/concrete-backup-bin"

# Check if we're running in a graphical environment
if [ -z "$DISPLAY" ]; then
    echo "Error: This application requires a graphical environment."
    echo "Please run from a desktop session."
    exit 1
fi

# Check if executable exists
if [ ! -f "$EXECUTABLE" ]; then
    echo "Error: Concrete Backup executable not found at $EXECUTABLE"
    exit 1
fi

# Use pkexec for graphical privilege escalation
if command -v pkexec >/dev/null 2>&1; then
    echo "Starting Concrete Backup with elevated privileges..."
    exec pkexec env DISPLAY="$DISPLAY" XAUTHORITY="$XAUTHORITY" "$EXECUTABLE" "$@"
else
    echo "Error: pkexec not found. Please install policykit-1."
    echo "Attempting to run without elevation..."
    exec "$EXECUTABLE" "$@"
fi
