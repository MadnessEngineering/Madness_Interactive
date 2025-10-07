#!/bin/bash

# A script to open the git repository root of a given file in GitHub Desktop.

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Functions ---

# Function to print error messages to stderr
error() {
  echo "Error: $1" >&2
  exit 1
}

# --- Main Script ---

# Check for required commands
command -v git >/dev/null 2>&1 || error "git is not installed. Please install it to use this script."

# Check if a file path is provided as an argument
if [ -z "$1" ]; then
  echo "Usage: $0 <path_to_file>"
  exit 1
fi

FILE_PATH="$1"

# The file path provided might be relative, so we get the absolute path.
# Note: realpath might not be available on all macOS versions by default.
# 'greadlink -f' from coreutils is a good alternative if available.
# A more portable way using python is also an option.
# For simplicity, we'll try to work with the path as given, but this is a point of fragility.
# A more robust solution would be to ensure an absolute path.
if [[ "$FILE_PATH" != /* ]]; then
    # Attempt to make it absolute from the current directory.
    # This assumes the script is called with a path relative to the current working directory.
    FILE_PATH="$(pwd)/$FILE_PATH"
fi


# Check if the file or directory exists
if [ ! -e "$FILE_PATH" ]; then
  error "File or directory not found at '$FILE_PATH'"
fi

# If it's a file, get its directory. If it's a directory, use it directly.
if [ -f "$FILE_PATH" ]; then
  TARGET_DIR=$(dirname "$FILE_PATH")
else
  TARGET_DIR="$FILE_PATH"
fi

# Change to the target directory to run git command
cd "$TARGET_DIR" || error "Could not change to directory '$TARGET_DIR'"

# Find the git repository root
# The '2>/dev/null' suppresses error messages if it's not a git repo
GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)

# Check if we successfully found a git root
if [ -z "$GIT_ROOT" ]; then
  error "'$FILE_PATH' is not part of a git repository."
fi

echo "Project root found at: $GIT_ROOT"
echo "Opening in GitHub Desktop..."

# Open the repository root in GitHub Desktop
open -a "GitHub Desktop" "$GIT_ROOT"

echo "Done." 
