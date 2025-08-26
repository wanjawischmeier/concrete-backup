# Concrete Backup

A comprehensive backup management system for Ubuntu with a modern Qt5 GUI interface, featuring profile-based configuration, automatic scheduling, and drive management.

## Features

- **Modern Qt5 GUI**: Intuitive tabbed interface with menu system
- **Profile Management**: Create, save, load, and manage multiple backup profiles with YAML/JSON support
- **Smart Drive Selection**: Auto-detect removable drives with mounting capabilities
- **Flexible Sources**: Add source directories with visual file picker and drive association
- **Multiple Destinations**: Configure multiple backup destinations per profile
- **Custom Commands**: Pre and post-backup shell command execution
- **Automatic Scheduling**: Cron-based scheduling with graphical sudo integration
- **Detailed Logging**: Comprehensive logs written to each destination with rotation
- **Dry Run Mode**: Test configurations without actually copying files
- **Progress Monitoring**: Real-time backup progress with threaded execution

## Requirements

- Ubuntu 20.04 or later (or compatible Linux distribution)
- Python 3.12+
- Poetry (for dependency management)
- PyQt5
- rsync
- udisksctl (for drive mounting)
- sudo access (for drive operations and cron jobs)

## Installation

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd concrete-backup
   ```

2. Install Poetry if not already installed:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. Install dependencies:
   ```bash
   poetry install
   ```

4. Make the startup script executable:
   ```bash
   chmod +x run_backup_gui.sh
   ```

## Usage

### GUI Application

Start the main backup configuration GUI:

```bash
./run_backup_gui.sh
```

### Main Interface

The application features a modern tabbed interface:

#### **File Menu**
- **New Profile**: Create a new backup profile
- **Open Profile**: Load an existing profile from file
- **Save Profile**: Save current profile (prompts for location if needed)
- **Save Profile As**: Save profile to a specific location
- **Exit**: Close the application

#### **Source Directories Tab**
- Select drives to browse for source directories
- Add multiple source directories with file picker
- Visual indication of drive associations (e.g., `/dev/sda2 → /home/user/Documents`)
- Enable/disable individual sources

#### **Destinations Tab**
- Select destination drives with auto-mount options
- Configure target paths on selected drives
- Support for multiple backup destinations
- Drive information display with mount status

#### **Schedule Tab**
- Set backup time (hour and minute)
- Choose specific days of the week or daily backup
- Real-time schedule status display
- Integration with system cron

#### **Backup Configuration & Actions**
- **Dry Run**: Test mode that doesn't actually copy files
- **Detailed Logging**: Enable comprehensive logging
- **Schedule Control**: Enable/disable automatic scheduling
- **Run Now**: Execute backup immediately

### Profile Management

Profiles are automatically saved to `~/.config/concrete-backup/profiles/` as YAML files, but can be saved anywhere using the "Save Profile As" option.

Each profile contains:
- Source directories with optional drive associations
- Multiple destination configurations
- Schedule settings (time, days, enabled status)
- Backup options (dry run, logging)
- Pre/post backup commands (when implemented)

### Scheduling & Permissions

When enabling scheduling:
- The system prompts for sudo password (with graphical dialog)
- Creates root cron jobs for reliable execution
- Generates backup scripts in `~/.config/concrete-backup/scripts/`
- Provides retry mechanism for password entry
- Allows cancellation without errors

**Important**: Profiles must be saved before scheduling can be enabled.

### Command Line Usage

Execute backups directly via command line:

```bash
# Run a specific profile
poetry run python backup_engine.py <profile_name>

# Example
poetry run python backup_engine.py MyBackupProfile
```

## Architecture

### Core Components

- **`backup_gui.py`** - Main application entry point
- **`gui/main_window.py`** - Main window with menu system
- **`gui/backup_config_widget.py`** - Central configuration widget
- **`backup_engine.py`** - Core backup execution engine with rsync
- **`backup_config.py`** - Configuration management and data classes
- **`cron_manager.py`** - Cron job management with sudo integration
- **`drive_manager.py`** - Drive detection and management

### GUI Components

- **`gui/sources_tab.py`** - Source directory configuration
- **`gui/destinations_tab.py`** - Destination configuration  
- **`gui/schedule_tab.py`** - Schedule configuration
- **`gui/backup_worker.py`** - Threaded backup execution
- **`gui/backup_progress_dialog.py`** - Progress monitoring
- **`gui/gui_utils.py`** - Graphical sudo password helper

### Reusable Widgets

- **`gui/widgets/drive_selection_widget.py`** - Drive selection with auto-mount
- **`gui/widgets/directory_list_widget.py`** - Directory list management

## Configuration Files

- **Profiles**: `~/.config/concrete-backup/profiles/*.yaml`
- **Generated Scripts**: `~/.config/concrete-backup/scripts/backup_*.sh`
- **Cron Logs**: `~/.config/concrete-backup/cron.log`
- **Backup Logs**: `<destination>/backup_logs/backup_YYYYMMDD_HHMMSS.log`

## Backup Process

1. **Validation**: Verify profile configuration and source/destination availability
2. **Pre-commands**: Execute custom pre-backup commands (if configured)
3. **Drive Operations**: Auto-mount destination drives if required
4. **Synchronization**: Use rsync with archive mode to mirror sources to destinations
5. **Post-commands**: Execute custom post-backup commands (if configured)
6. **Cleanup**: Unmount drives that were auto-mounted during the process
7. **Logging**: Write detailed logs with timestamps to each destination

### Rsync Options Used

- `-a` (archive): Preserve permissions, ownership, timestamps
- `-v` (verbose): Detailed output for logging
- `--delete`: Remove files from destination that don't exist in source
- `--progress`: Show transfer progress
- `--dry-run`: Test mode (when enabled)

## Examples

### Home Directory Backup

**Configuration:**
- **Sources**: `/home/user/Documents`, `/home/user/Pictures`, `/home/user/Videos`
- **Destination**: External USB drive (`/dev/sdb1`) → `/media/backup/home`
- **Schedule**: Daily at 2:00 AM
- **Options**: Detailed logging enabled

### Multi-Drive Server Backup

**Configuration:**
- **Sources**: `/var/www/html`, `/etc`, `/home`
- **Destinations**: 
  - Primary: External HDD (`/dev/sdc1`) → `/mnt/backup-primary`
  - Secondary: USB drive (`/dev/sdd1`) → `/media/backup-secondary`
- **Schedule**: Weekdays at 1:00 AM
- **Options**: Dry run for testing, then live backup

## Troubleshooting

### Common Issues

**Backup Fails with Exit Code 1:**
- Check if the profile exists in `~/.config/concrete-backup/profiles/`
- Verify source directories are accessible
- Ensure destination drives are properly mounted

**Drive Not Detected:**
- Click "Refresh Drives" button
- Check if drive is properly connected
- Verify drive has a valid filesystem

**Schedule Not Working:**
- Ensure profile is saved before enabling schedule
- Check `~/.config/concrete-backup/cron.log` for execution logs
- Verify cron job with `sudo crontab -l`

**Permission Issues:**
- Sudo password prompt appears for drive mounting and cron operations
- Use "Cancel" in password dialog to abort operations cleanly
- Check that user has sudo privileges

### Log Locations

- **Cron execution**: `~/.config/concrete-backup/cron.log`
- **Detailed backup logs**: `<destination>/backup_logs/backup_YYYYMMDD_HHMMSS.log`
- **Application errors**: Terminal output when running `./run_backup_gui.sh`

### Testing

Use "Dry Run" mode to test configurations:
- Enables rsync `--dry-run` flag
- Shows what would be copied without actually copying
- Useful for verifying source/destination configuration
- Logs show simulated operations

## Development

The application follows a modular architecture with:
- Separation of GUI and core logic
- Reusable widget components
- Clean separation of concerns
- Comprehensive error handling
- Type hints and documentation

To contribute or modify:
1. Follow the existing code structure
2. Use type hints for new functions
3. Add proper error handling
4. Update this README for new features
