#!/usr/bin/env python3
"""
Global translation utility for Concrete Backup
Provides a simple tr() function that uses the correct context.
"""

from PyQt5.QtCore import QCoreApplication


def tr(text: str) -> str:
    """
    Global translation function that uses the MainWindow context.
    
    Args:
        text: The English text to translate
        
    Returns:
        The translated text in the current language, or the original text if no translation exists
    """
    return QCoreApplication.translate("MainWindow", text)
