#!/usr/bin/env python3
"""
Version utilities for Concrete Backup.
"""

import os
import tomllib
from pathlib import Path


def get_version():
    """Get version from environment, hardcoded constant, or pyproject.toml."""
    # First, check if version is provided as environment variable (for builds)
    env_version = os.environ.get('CONCRETE_BACKUP_VERSION')
    if env_version:
        return env_version
    
    # Second, check if there's a hardcoded version constant (for PyInstaller builds)
    try:
        import importlib
        version_const = importlib.import_module('version_const')
        return version_const.CONCRETE_BACKUP_VERSION
    except ImportError:
        pass
    
    # Finally, fall back to reading from pyproject.toml (for development)
    try:
        pyproject_path = Path(__file__).parent / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
        return data["tool"]["poetry"]["version"]
    except (FileNotFoundError, KeyError, tomllib.TOMLDecodeError):
        return "unknown"


def get_version_info():
    """Get detailed version information."""
    version = get_version()
    return {
        "version": version,
        "name": "Concrete Backup",
        "full_name": f"Concrete Backup {version}"
    }


if __name__ == "__main__":
    # When run as a script, output version to stdout
    import sys
    print(get_version(), file=sys.stdout)
