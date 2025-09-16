#!/usr/bin/env python3
"""
Logging Helper
Centralized logging configuration to avoid code duplication.
"""

import logging
import sys
from pathlib import Path

# Custom log level for UI operations
UI_LEVEL = 25  # Between INFO (20) and WARNING (30)
logging.addLevelName(UI_LEVEL, "UI")

def ui(self, message, *args, **kwargs):
    """Log a UI operation message."""
    if self.isEnabledFor(UI_LEVEL):
        self._log(UI_LEVEL, message, args, **kwargs)

# Add the ui method to Logger class
logging.Logger.ui = ui


def setup_logger(name: str, level: int = logging.INFO, include_ui: bool = True) -> logging.Logger:
    """
    Set up a logger with consistent formatting across all components.
    
    Args:
        name: The name of the logger (usually __name__ from the calling module)
        level: The logging level (default: INFO)
        include_ui: Whether to include UI-level messages (default: True)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Set the level - if include_ui is False, keep INFO level but filter out UI messages
    logger.setLevel(level)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Create a filter for UI messages if needed
    if not include_ui:
        def filter_ui_messages(record):
            return record.levelno != UI_LEVEL
        console_handler.addFilter(filter_ui_messages)
    
    # Create formatter - shows component name, level, and message
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    # Prevent propagation to root logger to avoid duplicate messages
    logger.propagate = False
    
    return logger


def get_logger(name: str, include_ui: bool = True) -> logging.Logger:
    """
    Get a logger for a component. Convenience function that calls setup_logger.
    
    Args:
        name: The name of the logger (usually __name__ from the calling module)
        include_ui: Whether to include UI-level messages (default: True)
    
    Returns:
        Configured logger instance
    """
    return setup_logger(name, include_ui=include_ui)


def get_ui_logger(name: str) -> logging.Logger:
    """
    Get a logger specifically for UI components that includes UI-level messages.
    
    Args:
        name: The name of the logger (usually __name__ from the calling module)
    
    Returns:
        Configured logger instance with UI logging enabled
    """
    return setup_logger(name, level=UI_LEVEL, include_ui=True)


def get_backend_logger(name: str) -> logging.Logger:
    """
    Get a logger for backend components that excludes UI-level messages.
    
    Args:
        name: The name of the logger (usually __name__ from the calling module)
    
    Returns:
        Configured logger instance without UI logging
    """
    return setup_logger(name, include_ui=False)
