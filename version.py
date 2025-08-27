#!/usr/bin/env python3
"""
Version utilities for Concrete Backup.
"""

import tomllib
from pathlib import Path


def get_version():
    """Get version from pyproject.toml."""
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
    print(get_version())
