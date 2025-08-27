#!/usr/bin/env python3
"""
GUI utilities for password prompts and system operations
"""

import subprocess
from typing import Tuple
from PyQt5.QtWidgets import QInputDialog, QMessageBox, QWidget


class SudoHelper:
    """Helper class for handling sudo operations with GUI password prompts."""

    @staticmethod
    def run_with_sudo(command: list, parent: QWidget = None, max_retries: int = 3) -> Tuple[bool, str]:
        """
        Run a command with sudo using graphical password prompt.

        Args:
            command: The command to run (without 'sudo' prefix)
            parent: Parent widget for dialogs
            max_retries: Maximum number of password attempts

        Returns:
            Tuple of (success, output_or_error_message)
        """
        try:
            # Check if we already have sudo privileges
            if SudoHelper._has_sudo_privileges():
                return SudoHelper._run_sudo_command(command)

            # Need to authenticate
            return SudoHelper._authenticate_and_run(command, parent, max_retries)

        except (subprocess.SubprocessError, OSError) as e:
            return False, f"Error running command: {str(e)}"

    @staticmethod
    def _has_sudo_privileges() -> bool:
        """Check if current user already has sudo privileges."""
        try:
            result = subprocess.run(['sudo', '-n', 'true'], capture_output=True, text=True)
            return result.returncode == 0
        except (subprocess.SubprocessError, OSError):
            return False

    @staticmethod
    def _run_sudo_command(command: list) -> Tuple[bool, str]:
        """Run a command with sudo."""
        try:
            result = subprocess.run(['sudo'] + command, capture_output=True, text=True)
            if result.returncode == 0:
                return True, result.stdout.strip()
            else:
                return False, result.stderr.strip()
        except (subprocess.SubprocessError, OSError) as e:
            return False, f"Error executing command: {str(e)}"

    @staticmethod
    def _authenticate_and_run(command: list, parent: QWidget, max_retries: int) -> Tuple[bool, str]:
        """Authenticate user and run command."""
        for attempt in range(max_retries):
            password, ok = QInputDialog.getText(
                parent, "Authentication Required",
                f"Enter password for sudo (attempt {attempt + 1}/{max_retries}):",
                QInputDialog.Password
            )

            if not ok:
                return False, "Authentication cancelled by user"

            success, message = SudoHelper._try_sudo_with_password(command, password)
            if success:
                return True, message

            if attempt < max_retries - 1:
                QMessageBox.warning(parent, "Authentication Failed", "Incorrect password. Please try again.")

        return False, "Authentication failed after maximum attempts"

    @staticmethod
    def _try_sudo_with_password(command: list, password: str) -> Tuple[bool, str]:
        """Try to run sudo command with provided password."""
        try:
            process = subprocess.Popen(
                ['sudo', '-S'] + command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            stdout, stderr = process.communicate(input=password + '\n', timeout=30)

            if process.returncode == 0:
                return True, stdout.strip()
            else:
                return False, stderr.strip()

        except subprocess.TimeoutExpired:
            process.kill()
            return False, "Command timed out"
        except (subprocess.SubprocessError, OSError) as e:
            return False, f"Error executing command: {str(e)}"

    @staticmethod
    def check_sudo_available() -> bool:
        """Check if sudo is available and user can use it."""
        try:
            result = subprocess.run(['sudo', '-v'], capture_output=True, text=True)
            return result.returncode == 0
        except (subprocess.SubprocessError, OSError):
            return False
