#!/bin/bash

# install_git_hooks.sh
# Install Git hooks from templates to a target repository
# Usage: ./install_git_hooks.sh [target_path]

set -e

# Define colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Current script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Path to the hook templates directory
HOOKS_TEMPLATE_DIR="${SCRIPT_DIR}/git_hooks_template"

# Target path (use argument if provided, otherwise use current directory)
TARGET_PATH="${1:-.}"

# Print header
echo -e "${YELLOW}=== MADNESS INTERACTIVE GIT HOOKS INSTALLER ===${NC}"
echo -e "Template directory: ${HOOKS_TEMPLATE_DIR}"
echo -e "Target repository: ${TARGET_PATH}"

# Check if target is a Git repository
if [ ! -d "${TARGET_PATH}/.git" ]; then
    echo -e "${RED}Error: ${TARGET_PATH} is not a Git repository!${NC}"
    echo "Please provide a valid Git repository path."
    exit 1
fi

# Copy hook templates to the target repository
echo -e "Installing hooks to ${TARGET_PATH}/.git/hooks/..."
cp -f "${HOOKS_TEMPLATE_DIR}/"* "${TARGET_PATH}/.git/hooks/"

# Make all hooks executable
chmod +x "${TARGET_PATH}/.git/hooks/"*

echo -e "${GREEN}Git hooks installed successfully!${NC}"
echo -e "${YELLOW}Happy coding, you mad genius!${NC}" 
