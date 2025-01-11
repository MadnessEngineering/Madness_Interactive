#!/bin/bash

# Initialize a new Rust project from a template
# Usage: ./init_rust_project.sh [template-name] [project-name]

set -e

# Check if correct number of arguments
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 [template-name] [project-name]"
    echo "Available templates:"
    ls -1 ../templates/rust/
    exit 1
fi

TEMPLATE_NAME=$1
PROJECT_NAME=$2
TEMPLATE_PATH="templates/rust/$TEMPLATE_NAME"
TARGET_PATH="$PROJECT_NAME"

# Check if template exists
if [ ! -d "$TEMPLATE_PATH" ]; then
    echo "Error: Template '$TEMPLATE_NAME' not found in templates/rust/"
    echo "Available templates:"
    ls -1 templates/rust/
    exit 1
fi

# Check if target directory already exists
if [ -d "$TARGET_PATH" ]; then
    echo "Error: Directory '$TARGET_PATH' already exists"
    exit 1
fi

# Copy template to new project directory
echo "Creating new Rust project '$PROJECT_NAME' from template '$TEMPLATE_NAME'..."
cp -r "$TEMPLATE_PATH" "$TARGET_PATH"

# Initialize git repository
cd "$TARGET_PATH"
git init

# Initialize cargo if Cargo.toml doesn't exist
if [ ! -f "Cargo.toml" ]; then
    cargo init
fi

# Update project name in Cargo.toml
sed -i '' "s/name = \".*\"/name = \"$PROJECT_NAME\"/" Cargo.toml

# Build project
cargo build

echo "Project initialized successfully!"
echo "To get started:"
echo "  cd $PROJECT_NAME"
echo "  cargo build"
echo "  cargo run"
echo "  # Start coding!" 
