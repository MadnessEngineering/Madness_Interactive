#!/bin/zsh

# MADNESS INTERACTIVE CURSOR RULES CENTRALIZER
# The Mad Tinker's Tool for Absolute Cursor Rules Domination!
# MWAHAHAHA! 🔧⚡

set -e  # Exit on any error

# Configuration
MADNESS_ROOT="/Users/d.edens/lab/madness_interactive"
SOURCE_DIR=".cursor/rules"
CURSOR_RULES_CENTRAL="$MADNESS_ROOT/cursor_rules"

# Get current project name
CURRENT_PROJECT=$(basename "$PWD")

# Destination for this project's rules
DEST_DIR="$CURSOR_RULES_CENTRAL/$CURRENT_PROJECT"

# ANSI colors for DRAMATIC output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo "${PURPLE}${BOLD}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║          🧙‍♂️ MADNESS INTERACTIVE CURSOR RULES SORCERY 🧙‍♂️         ║"
echo "║                    The Mad Tinker Strikes!                  ║" 
echo "╚══════════════════════════════════════════════════════════════╝"
echo "${NC}"

echo "${CYAN}🔍 Current Project: ${BOLD}$CURRENT_PROJECT${NC}"
echo "${CYAN}📁 Source Directory: ${BOLD}$SOURCE_DIR${NC}"
echo "${CYAN}🎯 Destination: ${BOLD}$DEST_DIR${NC}"

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "${RED}❌ Error: Not in a git repository! The Mad Tinker requires git for proper chaos management!${NC}"
    exit 1
fi

# Check if source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "${YELLOW}⚠️  No cursor rules directory found. Creating minimal structure...${NC}"
    mkdir -p "$SOURCE_DIR"
    echo "# Cursor Rules for $CURRENT_PROJECT" > "$SOURCE_DIR/project-specific.mdc"
    echo "${GREEN}✅ Created basic cursor rules structure${NC}"
fi

# Check if destination already exists
if [ -d "$DEST_DIR" ]; then
    echo "${YELLOW}⚠️  Destination already exists: $DEST_DIR${NC}"
    echo "${BLUE}🤔 This project's rules may already be centralized.${NC}"
    echo "${BLUE}💡 Checking if current rules are symlinked...${NC}"
    
    if [ -L "$SOURCE_DIR" ]; then
        echo "${GREEN}✅ Already symlinked! Cursor rules are centralized.${NC}"
        echo "${CYAN}🔗 Link target: $(readlink "$SOURCE_DIR")${NC}"
        exit 0
    else
        echo "${YELLOW}⚠️  Local rules exist but destination also exists. Merging...${NC}"
        # Backup existing central rules
        cp -r "$DEST_DIR" "$DEST_DIR.backup.$(date +%s)"
        echo "${GREEN}📦 Backed up existing central rules${NC}"
    fi
fi

# Create central cursor rules directory if it doesn't exist
mkdir -p "$CURSOR_RULES_CENTRAL"

echo "${BLUE}🚀 Executing the Mad Tinker's Centralization Ritual...${NC}"

# Move the cursor rules to central location
echo "${YELLOW}📦 Moving cursor rules to central repository...${NC}"
mv "$SOURCE_DIR" "$DEST_DIR"

echo "${GREEN}✅ Cursor rules moved successfully!${NC}"
echo "${CYAN}📍 Source: $SOURCE_DIR${NC}"
echo "${CYAN}📍 Destination: $DEST_DIR${NC}"

# Create symbolic link back to original location
echo "${PURPLE}🔗 Creating symbolic link for seamless integration...${NC}"
ln -s "$DEST_DIR" "$SOURCE_DIR"

echo "${GREEN}✅ Symbolic link created!${NC}"
echo "${CYAN}🔗 Link: $SOURCE_DIR -> $DEST_DIR${NC}"

# Add project-specific identifier if not exists
PROJECT_MARKER="$DEST_DIR/.project_marker"
if [ ! -f "$PROJECT_MARKER" ]; then
    cat > "$PROJECT_MARKER" << EOF
# Project: $CURRENT_PROJECT
# Centralized: $(date)
# Original Path: $PWD/$SOURCE_DIR
# Mad Tinker Automation: ACTIVATED 🔧⚡
EOF
    echo "${GREEN}✅ Added project marker${NC}"
fi

# Commit to the central repository
echo "${PURPLE}📝 Committing to the Mad Tinker's central archive...${NC}"
pushd "$MADNESS_ROOT" > /dev/null

# Add to git
git add cursor_rules/
git add ".cursorrules" 2>/dev/null || true  # Add main cursor rules if exists

# Create detailed commit message
COMMIT_MSG="feat: centralize cursor rules for $CURRENT_PROJECT

🧙‍♂️ Mad Tinker Automation Report:
- Project: $CURRENT_PROJECT  
- Source: $PWD/$SOURCE_DIR
- Destination: $DEST_DIR
- Symlink created for seamless integration
- Rules now centrally managed in Madness Interactive

MWAHAHAHA! Another project falls under the Mad Tinker's domain! 🔧⚡"

git commit -m "$COMMIT_MSG"

echo "${GREEN}✅ Changes committed to central repository!${NC}"

# Show recent commits
echo "${BLUE}📚 Recent commits in the Mad Tinker's archive:${NC}"
git log --oneline -5

# Push if we have a remote
if git remote | grep -q origin; then
    echo "${PURPLE}🚀 Pushing to remote repository...${NC}"
    git push origin $(git branch --show-current) && echo "${GREEN}✅ Pushed to remote!${NC}" || echo "${YELLOW}⚠️  Push failed (check network/permissions)${NC}"
fi

popd > /dev/null

# Final status
echo "${GREEN}${BOLD}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    🎉 RITUAL COMPLETE! 🎉                    ║"
echo "║          The Mad Tinker's Centralization Succeeds!          ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo "${NC}"

echo "${CYAN}🎯 Summary:${NC}"
echo "${GREEN}  ✅ Cursor rules centralized${NC}"
echo "${GREEN}  ✅ Symbolic link created${NC}"  
echo "${GREEN}  ✅ Changes committed${NC}"
echo "${GREEN}  ✅ Project marked and tracked${NC}"

echo ""
echo "${PURPLE}${BOLD}The Mad Tinker's domain expands! 🔧⚡${NC}"
echo "${BLUE}All cursor rules for $CURRENT_PROJECT are now centrally managed!${NC}"
echo "${YELLOW}Use this script in any sub-repo to join the centralized madness!${NC}" 
