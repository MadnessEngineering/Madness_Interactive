"""
Omnispindle API package.

This package provides API interfaces for the Omnispindle distributed task system.
"""

from .server import app, init_server

__all__ = [
    "app",
    "init_server",
] 