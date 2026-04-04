#!/usr/bin/env python3
"""
Config Module - Handles loading environment variables from .env file.
"""

import os
from pathlib import Path


def load_env_file(env_path: Path = None) -> None:
    """
    Load environment variables from a .env file.

    Args:
        env_path: Path to the .env file. If None, looks for .env in project root.
    """
    if env_path is None:
        # Find project root (where .env should be)
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent
        env_path = project_root / ".env"

    if not env_path.exists():
        return

    with open(env_path, "r") as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue
            # Parse KEY=VALUE
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                # Only set if not already in environment
                if key not in os.environ:
                    os.environ[key] = value


# Load .env file when module is imported
load_env_file()
