[![concrete-backup](https://snapcraft.io/concrete-backup/badge.svg)](https://snapcraft.io/concrete-backup)

# Concrete Backup

A Python-based backup management tool with a PyQt5 GUI for creating and managing backup profiles. This is not an elegant or well maintained project! Just quickly vibe coded and thrown together in a couple days.

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
App icon created by [juicy_fish - Flaticon](https://www.flaticon.com/free-icons/firewall).

## Internationalization

The application supports multiple languages using Qt's internationalization system. The interface automatically detects the system language and displays translations when available.

### Available Languages

- **German (de)**: Fully translated
- **French (fr)**: Translation files available (needs translation)
- **Spanish (es)**: Translation files available (needs translation)

### Translation Workflow

The project includes a translation management script to help with internationalization tasks:

```bash
# Extract translatable strings from source code
python localization/manage_translations.py extract

# Create a new translation file for a language
python localization/manage_translations.py create <language_code>

# Edit translations using Qt Linguist (if installed)
python localization/manage_translations.py edit <language_code>

# Compile translation files for the application
python localization/manage_translations.py compile
```

### For Developers

1. **Adding Translatable Strings**: Use `self.tr("Your text here")` in PyQt widgets
2. **Extract Strings**: Run the extract command to update .ts files with new strings
3. **Translate**: Edit the .ts files manually or use Qt Linguist
4. **Compile**: Generate .qm files that the application loads at runtime

### For Translators

Translation files are located in `localization/translations/`:
- `concrete_backup_de.ts` - German translations
- `concrete_backup_fr.ts` - French translations  
- `concrete_backup_es.ts` - Spanish translations

To contribute translations:
1. Edit the appropriate .ts file with your translations
2. Run `python localization/manage_translations.py compile` to test
3. Submit a pull request
