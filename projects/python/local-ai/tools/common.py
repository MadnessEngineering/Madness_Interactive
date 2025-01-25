#!/usr/bin/env python3
"""
Common utilities for setup scripts.
"""

import os
from pathlib import Path

def setup_env(env_string: str):
    """Setup environment configuration."""
    env_path = Path(".env")
    
    if not env_path.exists():
        print("Creating .env file...")
        with open(env_path, "w") as f:
            f.write(env_string)
        print("Created .env file with default settings")
    else:
        print(".env file already exists, Appending..")
        with open(env_path, "a") as f:
            f.write(env_string) 