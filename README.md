# Concrete Backup

A Python-based backup management tool with a PyQt5 GUI for creating and managing backup profiles. This is not an elegant or well maintained project! Just quickly vibe coded and thrown together in about a day.

## Requirements

- Python 3.12+
- Linux (tested on Ubuntu)
- Poetry for dependency management

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd concrete-backup

# Install dependencies
poetry install
```

## Usage

### GUI Application

```bash
# Run with administrator privileges (recommended)
./run_backup_gui.sh

# Or run directly
poetry run python backup_gui.py
```

### Command Line

```bash
# Run backup for a specific profile
poetry run python backup_engine.py <profile-name>
```

## Configuration

- Backup profiles are stored in `~/.config/concrete-backup/profiles/` by default
- Profiles can be saved as YAML files
- Sources, destinations, and custom commands are configurable per profile

## Features

- **Backup Profiles**: Create and manage multiple backup configurations
- **Source Selection**: Choose directories to backup
- **Destination Management**: Local directories or external drives with auto-mounting
- **Custom Commands**: Pre/post-backup script execution  
- **Scheduling**: Cron-based automated backups
- **Drive Detection**: Automatic USB/external drive detection
- **Progress Tracking**: Real-time backup progress with logging

## Project Structure

```
concrete-backup/
├── backup_config.py      # Profile data models and management
├── backup_engine.py      # Core backup execution logic
├── backup_gui.py         # Main GUI application entry point
├── drive_manager.py      # Drive detection and mounting
├── cron_manager.py       # Scheduled backup management
├── gui/                  # GUI components
│   ├── controllers/      # UI logic controllers
│   ├── dialogs/         # Dialog windows
│   ├── tabs/            # Configuration tabs
│   ├── widgets/         # Reusable UI widgets
│   └── workers/         # Background task workers
└── run_backup_gui.sh    # Launcher script with privilege elevation
```

## Dependencies

- PyQt5: GUI framework
- PyYAML: Configuration file parsing
- psutil: System information
