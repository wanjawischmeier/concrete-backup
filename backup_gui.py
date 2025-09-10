#!/usr/bin/env python3
"""
Concrete Backup - Main GUI Application (Modular)
Main application for configuring and managing backup profiles.
"""

import sys
import os
import argparse
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox
from gui.main_window import MainWindow
from version import get_version


def check_privileges():
    """Check if the application is running with root privileges."""
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
            "The Snap version of Concrete Backup cannot access system scheduling "
            "due to security restrictions. Please download the .deb package from the GitHub releases page."
        )
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
        sys.exit(0)
    
    if os.geteuid() != 0:
        print("Error: Concrete Backup requires root privileges to manage system backups.")
        print("Please run with sudo:")
        print("  sudo concrete-backup")
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
    return parser.parse_args()


def list_available_languages():
    """List available interface languages."""
    print("Available interface languages:")
    print("  en - English (default)")
    
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
                    print(f"  {lang_code} - {lang_name}")


def main():
    """Main entry point for the backup GUI application."""
    args = parse_arguments()
    
    if args.list_languages:
        list_available_languages()
        sys.exit(0)
    
    if args.headless_test:
        print("Headless test passed: Application can be imported successfully")
        sys.exit(0)
    
    try:
        run_gui_application(args.language)
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)


def handle_headless_test() -> int:
    """Handle headless test mode for CI/CD."""
    print("Headless test mode: checking imports...")
    try:
        # Test imports without creating GUI - MainWindow is already imported above
        print("✓ All GUI imports successful")
        return 0
    except ImportError as e:
        print(f"Import error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1


def run_gui_application(language_code: str = None) -> int:
    """Run the GUI application."""
    print("Starting Concrete Backup GUI...")

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Concrete Backup")
    app.setStyle('Fusion')

    # Initialize translation system
    from localization import set_language
    if language_code:
        print(f"Setting language to: {language_code}")
        success = set_language(language_code)
        if not success:
            print(f"Warning: Could not load language '{language_code}', falling back to system default")
            set_language()
    else:
        set_language()

    try:
        return start_main_window(app)
    except ImportError as e:
        print(f"Missing dependency: {e}")
        return 1
    except (OSError, PermissionError) as e:
        print(f"System error starting GUI: {e}")
        return 1
    except KeyboardInterrupt:
        print("\nGUI startup interrupted by user")
        return 130
    except Exception as e:
        return handle_gui_error(e)


def start_main_window(app: QApplication) -> int:
    """Create and show the main window."""
    print("Creating main window...")
    window = MainWindow()

    print("Showing main window...")
    window.show()

    print("Window should now be visible. Starting event loop...")

    # Start the event loop
    exit_code = app.exec_()
    print(f"Application exited with code: {exit_code}")
    return exit_code


def handle_gui_error(e: Exception) -> int:
    """Handle GUI startup errors."""
    print(f"Unexpected error starting GUI: {e}")
    traceback.print_exc()

    # Show error dialog if possible
    try:
        QMessageBox.critical(None, "Startup Error", f"Failed to start GUI: {str(e)}")
    except Exception:
        pass

    return 1


if __name__ == "__main__":
    sys.exit(main())
