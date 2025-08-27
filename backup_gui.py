#!/usr/bin/env python3
"""
Concrete Backup - Main GUI Application (Modular)
Main application for configuring and managing backup profiles.
"""

import sys
import argparse
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox
from gui.main_window import MainWindow
from version import get_version


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
    # Parse command line arguments first
    args = parse_arguments()
    
    # Handle headless test mode (for CI/CD)
    if args.headless_test:
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

    print("Starting Concrete Backup GUI...")

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Concrete Backup")
    app.setStyle('Fusion')

    try:
        print("Creating main window...")
        window = MainWindow()

        print("Showing main window...")
        window.show()

        print("Window should now be visible. Starting event loop...")

        # Start the event loop
        exit_code = app.exec_()
        print(f"Application exited with code: {exit_code}")
        sys.exit(exit_code)

    except ImportError as e:
        print(f"Missing dependency: {e}")
        sys.exit(1)
    except (OSError, PermissionError) as e:
        print(f"System error starting GUI: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nGUI startup interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"Unexpected error starting GUI: {e}")
        traceback.print_exc()

        # Show error dialog if possible
        try:
            QMessageBox.critical(None, "Startup Error", f"Failed to start GUI: {str(e)}")
        except Exception:
            pass

        sys.exit(1)


if __name__ == "__main__":
    main()
