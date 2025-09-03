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
    return parser.parse_args()


def main():
    """Main application entry point."""
    # Check privileges first
    check_privileges()
    
    # Parse command line arguments
    args = parse_arguments()

    # Handle special modes
    if args.headless_test:
        return handle_headless_test()

    # Run normal GUI application
    return run_gui_application()


def handle_headless_test() -> int:
    """Handle headless test mode for CI/CD."""
    print("Headless test mode: checking imports...")
    try:
        # Test imports without creating GUI - MainWindow is already imported above
        print("✓ All GUI imports successful")
        return 0
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return 1
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return 1


def run_gui_application() -> int:
    """Run the GUI application."""
    print("Starting Concrete Backup GUI...")

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Concrete Backup")
    app.setStyle('Fusion')

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
