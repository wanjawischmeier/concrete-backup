#!/usr/bin/env python3
"""
Concrete Backup - Main GUI Application (Modular)
Main application for configuring and managing backup profiles.
"""

import sys
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox
from gui.main_window import MainWindow


def main():
    """Main application entry point."""
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
