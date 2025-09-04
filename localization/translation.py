#!/usr/bin/env python3
"""
Qt-based translation system for Concrete Backup using QTranslator
"""

import os
import sys
from PyQt5.QtCore import QTranslator, QLocale, QCoreApplication
from PyQt5.QtWidgets import QApplication


class QtTranslationManager:
    """Translation manager using Qt's built-in internationalization system."""
    
    def __init__(self):
        self.current_language = "en"
        self.translator = None
        self.translations_dir = os.path.join(os.path.dirname(__file__), "translations")
        
        # Ensure translations directory exists
        os.makedirs(self.translations_dir, exist_ok=True)
    
    def set_language(self, language_code: str = None) -> bool:
        """Set the current language and load appropriate translation."""
        app = QApplication.instance()
        if not app:
            print("No QApplication instance found")
            return False
        
        # If no language specified, use system locale
        if language_code is None:
            system_locale = QLocale.system()
            language_code = system_locale.name()  # e.g., 'en_US', 'de_DE'
            # Extract just the language part (e.g., 'en' from 'en_US')
            if '_' in language_code:
                language_code = language_code.split('_')[0]
            print(f"Using system language: {language_code}")
        
        # Remove existing translator
        if self.translator:
            app.removeTranslator(self.translator)
            self.translator = None
        
        # For English, no translation file needed
        if language_code == "en":
            self.current_language = "en"
            print("Set language to: en (default)")
            return True
        
        # Load translation file
        self.translator = QTranslator()
        translation_file = f"concrete_backup_{language_code}"
        translation_path = os.path.join(self.translations_dir, translation_file)
        
        if self.translator.load(translation_path):
            app.installTranslator(self.translator)
            self.current_language = language_code
            print(f"Loaded translation: {language_code}")
            return True
        else:
            print(f"Translation file not found for {language_code}, using English")
            self.current_language = "en"
            return False
    
    def get_available_languages(self) -> list:
        """Get list of available language codes."""
        languages = ["en"]  # English is always available
        
        if os.path.exists(self.translations_dir):
            for filename in os.listdir(self.translations_dir):
                if filename.startswith("concrete_backup_") and filename.endswith(".qm"):
                    # Extract language code from filename
                    lang_code = filename[len("concrete_backup_"):-3]
                    if lang_code not in languages:
                        languages.append(lang_code)
        
        return sorted(languages)
    
    def get_current_language(self) -> str:
        """Get current language code."""
        return self.current_language
    
    def retranslate_ui(self):
        """Trigger UI retranslation for all widgets."""
        app = QApplication.instance()
        if app:
            # Send LanguageChange event to all widgets
            for widget in app.allWidgets():
                if hasattr(widget, 'retranslateUi'):
                    widget.retranslateUi()


# Global translation manager instance
_qt_translation_manager = QtTranslationManager()


def set_language(language_code: str = None) -> bool:
    """Set the current language."""
    return _qt_translation_manager.set_language(language_code)


def get_available_languages() -> list:
    """Get available languages."""
    return _qt_translation_manager.get_available_languages()


def get_current_language() -> str:
    """Get current language."""
    return _qt_translation_manager.get_current_language()


def retranslate_ui():
    """Retranslate all UI elements."""
    _qt_translation_manager.retranslate_ui()
