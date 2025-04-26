#!/usr/bin/env python
"""
GRIMOIRE CLI
============
Command-line interface for the Grimoire documentation generator.
"""

import sys
from pathlib import Path
from grimoire.grimoire import app

if __name__ == "__main__":
    app() 