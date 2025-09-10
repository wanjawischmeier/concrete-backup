#!/usr/bin/env python3
"""
Qt-based localization module for Concrete Backup
"""

from .translation import set_language, get_available_languages, get_current_language, retranslate_ui

__all__ = ['set_language', 'get_available_languages', 'get_current_language', 'retranslate_ui']
