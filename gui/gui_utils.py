#!/usr/bin/env python3
"""
GUI utilities for password prompts and system operations
"""

import subprocess
from typing import Tuple, Optional
from PyQt5.QtWidgets import QInputDialog, QLineEdit, QMessageBox, QWidget


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
            # First check if we already have sudo privileges
            check_result = subprocess.run(['sudo', '-n', 'true'], 
                                        capture_output=True, text=True)
            
            if check_result.returncode == 0:
                # We already have sudo privileges, run command directly
                result = subprocess.run(['sudo'] + command, 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    return True, result.stdout
                else:
                    return False, result.stderr
            
            # We need to prompt for password
            for attempt in range(max_retries):
                title = "Administrator Password Required"
                if attempt > 0:
                    title = f"Administrator Password Required (Attempt {attempt + 1}/{max_retries})"
                
                password, ok = QInputDialog.getText(
                    parent, 
                    title,
                    "Enter your password to perform administrative operations:",
                    QLineEdit.Password
                )
                
                if not ok:
                    # User cancelled
                    return False, "Operation cancelled by user"
                
                if not password:
                    # Empty password, show warning and try again
                    if attempt < max_retries - 1:
                        QMessageBox.warning(parent, "Empty Password", 
                                          "Password cannot be empty. Please try again.")
                        continue
                    else:
                        return False, "Maximum password attempts exceeded"
                
                # Use the password with sudo
                full_command = ['sudo', '-S'] + command
                process = subprocess.Popen(
                    full_command,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                stdout, stderr = process.communicate(input=password + '\n')
                
                if process.returncode == 0:
                    return True, stdout
                else:
                    # Check if it's a password error
                    if ("password" in stderr.lower() or 
                        "incorrect" in stderr.lower() or
                        "authentication failure" in stderr.lower()):
                        
                        if attempt < max_retries - 1:
                            QMessageBox.warning(parent, "Authentication Failed", 
                                              f"Incorrect password. Please try again.\n\n"
                                              f"Attempts remaining: {max_retries - attempt - 1}")
                            continue
                        else:
                            return False, "Maximum password attempts exceeded"
                    else:
                        # Some other error
                        return False, stderr
            
            return False, "Maximum password attempts exceeded"
                
        except Exception as e:
            return False, f"Error running sudo command: {str(e)}"
    
    @staticmethod
    def check_sudo_available() -> bool:
        """Check if sudo is available and user can use it."""
        try:
            result = subprocess.run(['sudo', '-v'], capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
