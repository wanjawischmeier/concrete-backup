[![concrete-backup](https://snapcraft.io/concrete-backup/badge.svg)](https://snapcraft.io/concrete-backup)

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

## Features

- **Backup Profiles**: Create and manage multiple backup configurations
- **Source Selection**: Choose directories to backup
- **Destination Management**: Local directories or external drives with auto-mounting
- **Custom Commands**: Pre/post-backup script execution  
- **Scheduling**: Cron-based automated backups
- **Drive Detection**: Automatic USB/external drive detection
- **Progress Tracking**: Real-time backup progress with logging

## Project Structure

```bash
concrete-backup/
├── backup_gui.py          # Main GUI application entry point
├── backup_engine.py       # Core backup execution logic
├── backup_runner.py       # Backup execution runner
├── backup_config.py       # Profile data models and management
├── ...
├── managers/              # Core management modules
├── workers/               # Background task workers
├── gui/                   # GUI components
│   ├── controllers/       # UI logic controllers
│   ├── dialogs/           # Dialog windows
│   ├── tabs/              # Configuration tabs
│   └── ...
├── .github/               # GitHub Actions CI/CD
├── pyproject.toml         # Poetry project configuration
└── run_backup_gui.sh      # Launcher script with privilege elevation
```

## Dependencies

- PyQt5: GUI framework
- PyYAML: Configuration file parsing
- psutil: System information

## Credit
App icon created by (juicy_fish - Flaticon)[https://www.flaticon.com/free-icons/firewall]
