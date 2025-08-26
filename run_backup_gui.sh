#!/bin/bash
# Startup script for Concrete Backup GUI

echo "Starting Concrete Backup GUI..."

# Change to the script directory
cd "$(dirname "$0")"

# Activate poetry environment and run the GUI
poetry run python backup_gui.py

echo "Concrete Backup GUI closed."
