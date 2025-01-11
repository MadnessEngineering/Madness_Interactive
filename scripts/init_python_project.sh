#!/bin/bash

# Initialize a new Python project from a template
# Usage: ./init_python_project.sh [template-name] [project-name]

set -e

# Check if correct number of arguments
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 [template-name] [project-name]"
    echo "Available templates:"
    ls -1 ../templates/python/
    exit 1
fi

TEMPLATE_NAME=$1
PROJECT_NAME=$2
TEMPLATE_PATH="templates/python/$TEMPLATE_NAME"
TARGET_PATH="$PROJECT_NAME"

# Check if template exists
if [ ! -d "$TEMPLATE_PATH" ]; then
    echo "Error: Template '$TEMPLATE_NAME' not found in templates/python/"
    echo "Available templates:"
    ls -1 templates/python/
    exit 1
fi

# Check if target directory already exists
if [ -d "$TARGET_PATH" ]; then
    echo "Error: Directory '$TARGET_PATH' already exists"
    exit 1
fi

# Copy template to new project directory
echo "Creating new Python project '$PROJECT_NAME' from template '$TEMPLATE_NAME'..."
cp -r "$TEMPLATE_PATH" "$TARGET_PATH"

# Initialize git repository
cd "$TARGET_PATH"
git init

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

echo "Project initialized successfully!"
echo "To get started:"
echo "  cd $PROJECT_NAME"
echo "  source venv/bin/activate  # On Windows use: venv\\Scripts\\activate"
echo "  # Start coding!" 
