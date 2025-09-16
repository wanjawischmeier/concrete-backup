#!/usr/bin/env python3
"""
Concrete Backup - Main GUI Application (Modular)
Main application for configuring and managing backup profiles.
"""

import sys
import os
import argparse
import logging
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QIcon
from gui.main_window import MainWindow
from version import get_version
from utils.logging_helper import get_ui_logger


def check_privileges():
    """Check if the application is running with root privileges."""
    logger = get_ui_logger(__name__)
    
    # Check if running in a snap environment
    if os.environ.get('SNAP'):
        # Show info dialog for snap users
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Snap Version Not Available")
        msg.setText("Scheduling functionality is not available in the Snap version.")
        msg.setDetailedText(
            "The Snap version of Concrete Backup cannot access system scheduling \
            due to security restrictions. Please download the .deb package from the GitHub releases page."
        )
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
        sys.exit(0)
    
    if os.geteuid() != 0:
        logger.error("Application requires root privileges to manage system backups")
        logger.error("Please run with sudo: sudo concrete-backup")
        sys.exit(1)


def parse_arguments():
    """Parse command line arguments."""
    version = get_version()
    parser = argparse.ArgumentParser(
        description="Concrete Backup - GUI application for managing backup profiles"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"Concrete Backup {version}"
    )
    parser.add_argument(
        "--headless-test",
        action="store_true",
        help="Test that the application can be imported (for CI/CD)"
    )
    parser.add_argument(
        "--language", "-l",
        type=str,
        help="Set the interface language (e.g., en, de, fr, es). If not specified, uses system locale."
    )
    parser.add_argument(
        "--list-languages",
        action="store_true",
        help="List available interface languages and exit"
    )
    parser.add_argument(
        "--dev", 
        action="store_true", 
        help="Run in development mode"
    )
    parser.add_argument(
        "--debug", 
        action="store_true", 
        help="Enable debug logging"
    )
    parser.add_argument(
        "profile", 
        nargs="?", 
        help="Profile YAML file to load"
    )
    return parser.parse_args()


def list_available_languages():
    """List available interface languages."""
    logger = get_ui_logger(__name__)
    
    logger.ui("Available interface languages:")
    logger.ui("  en - English (default)")
    
    # Check for available translation files
    localization_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "localization", "translations")
    if os.path.exists(localization_dir):
        for file in os.listdir(localization_dir):
            if file.endswith('.qm'):
                # Extract language code from filename (e.g., concrete_backup_de.qm -> de)
                lang_code = file.replace('concrete_backup_', '').replace('.qm', '')
                if lang_code != 'en':  # Don't list English twice
                    lang_name = {
                        'de': 'German',
                        'fr': 'French',
                        'es': 'Spanish',
                        'it': 'Italian',
                        'pt': 'Portuguese',
                        'ru': 'Russian',
                        'zh': 'Chinese',
                        'ja': 'Japanese'
                    }.get(lang_code, f'Language ({lang_code})')
                    logger.ui(f"  {lang_code} - {lang_name}")


def main():
    """Main application entry point."""
    logger = get_ui_logger(__name__)
    
    # Parse command line arguments using the existing parse_arguments function
    args = parse_arguments()
    
    # Handle special modes first
    if args.headless_test:
        return handle_headless_test()
    
    if args.list_languages:
        list_available_languages()
        return 0
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    # Check privileges before starting GUI
    check_privileges()
    
    # Run the GUI application with specified language
    return run_gui_application(args.language, args.profile)


def handle_headless_test() -> int:
    """Handle headless test mode for CI/CD."""
    logger = get_ui_logger(__name__)
    
    logger.info("Headless test mode: checking imports...")
    try:
        # Test imports without creating GUI - MainWindow is already imported above
        logger.info("✓ All GUI imports successful")
        return 0
    except ImportError as e:
        logger.error(f"Import error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1


def run_gui_application(language_code: str = None, profile_path: str = None) -> int:
    """Run the GUI application."""
    logger = get_ui_logger(__name__)
    
    logger.info("Starting Concrete Backup GUI...")

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Concrete Backup")
    app.setApplicationVersion("1.0")
    app.setStyle('Fusion')

    # Set the application icon
    icon_path = os.path.join(os.path.dirname(__file__), 'icon.png')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    else:
        logger.warning(f"Icon file not found: {icon_path}")

    # Initialize translation system
    from localization import set_language
    if language_code:
        logger.info(f"Setting language to: {language_code}")
        success = set_language(language_code)
        if not success:
            logger.warning(f"Could not load language '{language_code}', falling back to system default")
            set_language()
    else:
        set_language()

    try:
        return start_main_window(app, profile_path)
    except ImportError as e:
        logger.error(f"Missing dependency: {e}")
        return 1
    except (OSError, PermissionError) as e:
        logger.error(f"System error starting GUI: {e}")
        return 1
    except KeyboardInterrupt:
        logger.warning("GUI startup interrupted by user")
        return 130
    except Exception as e:
        return handle_gui_error(e)


def start_main_window(app: QApplication, profile_path: str = None) -> int:
    """Create and show the main window."""
    logger = get_ui_logger(__name__)
    
    logger.debug("Creating main window...")
    window = MainWindow()

    # Load profile if specified
    if profile_path:
        if os.path.exists(profile_path):
            try:
                window.load_profile(profile_path)
                logger.info(f"Loaded profile: {profile_path}")
            except Exception as e:
                logger.error(f"Failed to load profile {profile_path}: {e}")
        else:
            logger.error(f"Profile file not found: {profile_path}")

    logger.debug("Showing main window...")
    window.show()

    logger.debug("Window should now be visible. Starting event loop...")

    # Start the event loop
    exit_code = app.exec_()
    logger.info(f"Application exited with code: {exit_code}")
    return exit_code


def handle_gui_error(e: Exception) -> int:
    """Handle GUI startup errors."""
    logger = get_ui_logger(__name__)
    
    logger.error(f"Unexpected error starting GUI: {e}")
    traceback.print_exc()

    # Show error dialog if possible
    try:
        QMessageBox.critical(None, "Startup Error", f"Failed to start GUI: {str(e)}")
    except Exception:
        pass

    return 1


if __name__ == "__main__":
    sys.exit(main())
