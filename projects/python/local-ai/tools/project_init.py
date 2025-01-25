"""
Project Initialization Tool
Helps create and setup new project repositories with proper structure and configuration
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from typing import Literal, Optional

def init_python_project(name: str, description: str) -> None:
    """Initialize a Python project with standard structure"""
    project_dir = Path("src")
    project_dir.mkdir(exist_ok=True)

    # Create basic Python project structure
    (project_dir / name).mkdir(exist_ok=True)
    (project_dir / name / "__init__.py").touch()
    (project_dir / "tests").mkdir(exist_ok=True)
    (project_dir / "tests" / "__init__.py").touch()

    # Create requirements.txt
    with open("requirements.txt", "w") as f:
        f.write("# Core dependencies\n")

    # Create setup.py
    with open("setup.py", "w") as f:
        f.write(f'''from setuptools import setup, find_packages

setup(
    name="{name}",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={{"": "src"}},
    install_requires=[],
    python_requires=">=3.8",
)''')

def init_rust_project(name: str, description: str) -> None:
    """Initialize a Rust project using cargo"""
    subprocess.run(["cargo", "init", "--name", name], check=True)

def init_common_project(name: str, description: str) -> None:
    """Initialize a common project with basic structure"""
    Path("src").mkdir(exist_ok=True)
    Path("docs").mkdir(exist_ok=True)
    Path("examples").mkdir(exist_ok=True)

def create_readme(name: str, description: str, project_type: str) -> None:
    """Create a README.md file with project information"""
    with open("README.md", "w") as f:
        f.write(f"""# {name}

{description}

## Overview

This is a {project_type} project created with the project initialization tool.

## Setup

""")
        if project_type == "python":
            f.write("""
1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
""")
        elif project_type == "rust":
            f.write("""
1. Build the project:
   ```bash
   cargo build
   ```
2. Run tests:
   ```bash
   cargo test
   ```
""")

def init_project(name: str, description: str, project_type: Literal["python", "rust", "common"]) -> None:
    """
    Initialize a new project with the given name and type.
    
    Args:
        name: Project name (will be used for directory name)
        description: Short project description
        project_type: Type of project to create (python/rust/common)
    """
    # Create base project directory in appropriate location
    base_dir = Path("projects") / project_type
    project_dir = base_dir / name

    if project_dir.exists():
        print(f"Error: Project directory {project_dir} already exists!")
        sys.exit(1)

    project_dir.mkdir(parents=True)
    os.chdir(project_dir)

    # Initialize based on project type
    if project_type == "python":
        init_python_project(name, description)
    elif project_type == "rust":
        init_rust_project(name, description)
    else:  # common
        init_common_project(name, description)

    # Create README
    create_readme(name, description, project_type)

    print(f"\nProject {name} created successfully in {project_dir}")
    print(f"Type: {project_type}")
    print(f"Description: {description}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python project_init.py <name> <project_type> <description>")
        print("project_type must be one of: python, rust, common")
        sys.exit(1)

    name = sys.argv[1]
    project_type = sys.argv[2]
    description = sys.argv[3]

    if project_type not in ["python", "rust", "common"]:
        print("Error: project_type must be one of: python, rust, common")
        sys.exit(1)

    init_project(name, description, project_type)
