#!/usr/bin/env python
"""Setup script for Omnispindle."""

import os
from setuptools import setup, find_packages

# Get the long description from the README file
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# Get version
with open(os.path.join(here, "omnispindle", "__init__.py"), encoding="utf-8") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.strip().split("=")[1].strip(" \"'")
            break
    else:
        version = "0.0.0"

setup(
    name="omnispindle",
    version=version,
    description="A lightweight, flexible distributed task execution system for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/omnispindle",
    author="Your Name",
    author_email="your.email@example.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="distributed, task, queue, worker, scheduler",
    packages=find_packages(include=["omnispindle", "omnispindle.*"]),
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "redis": ["redis>=4.0.0"],
        "postgresql": ["psycopg2-binary>=2.9.0", "sqlalchemy>=1.4.0"],
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.12.0",
            "black>=21.5b0",
            "isort>=5.9.0",
            "flake8>=3.9.0",
            "mypy>=0.812",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=0.5.0",
            "myst-parser>=0.15.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "omnispindle-server=omnispindle.server:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/yourusername/omnispindle/issues",
        "Source": "https://github.com/yourusername/omnispindle",
    },
) 