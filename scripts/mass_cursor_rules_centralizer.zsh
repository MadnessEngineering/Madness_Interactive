#!/bin/zsh

# MADNESS INTERACTIVE MASS CURSOR RULES CENTRALIZER
# The Mad Tinker's ULTIMATE Tool for Repository Domination!
# MWAHAHAHA! 🔧⚡👑

set -e

# Configuration
MADNESS_ROOT="/Users/d.edens/lab/madness_interactive"
CENTRALIZER_SCRIPT="$MADNESS_ROOT/scripts/cursor_rules_centralizer.zsh"

# ANSI colors for MAXIMUM DRAMA
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
BLINK='\033[5m'
NC='\033[0m'

echo "${PURPLE}${BOLD}${BLINK}"
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║    👑 MADNESS INTERACTIVE MASS CURSOR RULES DOMINATION PROTOCOL 👑    ║"
echo "║              The Mad Tinker's ULTIMATE Power Move!                   ║"
echo "║                      MWAHAHAHA! 🔧⚡🌪️                               ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo "${NC}"

# Check if centralizer script exists
if [ ! -f "$CENTRALIZER_SCRIPT" ]; then
    echo "${RED}❌ Fatal Error: Individual centralizer script not found at $CENTRALIZER_SCRIPT${NC}"
    echo "${YELLOW}💡 Run this from the Madness Interactive root directory!${NC}"
    exit 1
fi

# Function to find all git repositories with cursor rules
find_cursor_repos() {
    echo "${BLUE}🔍 Scanning the realm for repositories with cursor rules...${NC}"
    
    # Search for .cursor/rules directories in git repositories
    find "$MADNESS_ROOT" -type d -name ".cursor" -exec test -d "{}/rules" \; -print | while read cursor_dir; do
        repo_dir=$(dirname "$cursor_dir")
        if [ -d "$repo_dir/.git" ]; then
            echo "$repo_dir"
        fi
    done
}

# Function to check if rules are already centralized
is_centralized() {
    local repo_dir="$1"
    local cursor_rules="$repo_dir/.cursor/rules"
    
    if [ -L "$cursor_rules" ]; then
        return 0  # True - is symlink (centralized)
    else
        return 1  # False - not centralized
    fi
}

# Get list of repositories
echo "${CYAN}📊 Gathering intelligence on cursor rules repositories...${NC}"
repos_with_cursor=()

while IFS= read -r repo; do
    if [ -n "$repo" ]; then
        repos_with_cursor+=("$repo")
    fi
done < <(find_cursor_repos)

echo "${GREEN}📋 Found ${#repos_with_cursor[@]} repositories with cursor rules:${NC}"

# Status report
centralized_count=0
needs_centralization=()

for repo in "${repos_with_cursor[@]}"; do
    project_name=$(basename "$repo")
    if is_centralized "$repo"; then
        echo "${GREEN}  ✅ $project_name (already centralized)${NC}"
        ((centralized_count++))
    else
        echo "${YELLOW}  📦 $project_name (needs centralization)${NC}"
        needs_centralization+=("$repo")
    fi
done

echo ""
echo "${CYAN}📊 Status Summary:${NC}"
echo "${GREEN}  ✅ Already centralized: $centralized_count${NC}"
echo "${YELLOW}  📦 Need centralization: ${#needs_centralization[@]}${NC}"

if [ ${#needs_centralization[@]} -eq 0 ]; then
    echo ""
    echo "${GREEN}${BOLD}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                  🎉 ULTIMATE VICTORY! 🎉                     ║"
    echo "║            All repositories are already under                ║"
    echo "║              the Mad Tinker's control!                      ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo "${NC}"
    exit 0
fi

echo ""
echo "${PURPLE}⚡ Beginning mass centralization ritual...${NC}"

# Ask for confirmation
echo "${YELLOW}${BOLD}⚠️  WARNING: This will centralize cursor rules for ${#needs_centralization[@]} repositories!${NC}"
echo "${BLUE}📝 The following repositories will be affected:${NC}"
for repo in "${needs_centralization[@]}"; do
    echo "${CYAN}    • $(basename "$repo")${NC}"
done

echo ""
read -q "REPLY?${BOLD}🤔 Continue with the Mad Tinker's mass centralization? (y/N): ${NC}"
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "${YELLOW}🛑 Mass centralization aborted. The repositories remain independent... for now.${NC}"
    exit 0
fi

echo ""
echo "${PURPLE}${BOLD}🚀 INITIATING MASS CENTRALIZATION PROTOCOL! 🚀${NC}"

# Centralize each repository
success_count=0
failure_count=0
failed_repos=()

for repo in "${needs_centralization[@]}"; do
    project_name=$(basename "$repo")
    echo ""
    echo "${BLUE}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo "${PURPLE}🎯 Centralizing: $project_name${NC}"
    echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    # Change to repository directory and run centralizer
    if pushd "$repo" > /dev/null 2>&1; then
        if "$CENTRALIZER_SCRIPT"; then
            echo "${GREEN}✅ Successfully centralized $project_name${NC}"
            ((success_count++))
        else
            echo "${RED}❌ Failed to centralize $project_name${NC}"
            ((failure_count++))
            failed_repos+=("$project_name")
        fi
        popd > /dev/null 2>&1
    else
        echo "${RED}❌ Could not access $repo${NC}"
        ((failure_count++))
        failed_repos+=("$project_name")
    fi
done

# Final report
echo ""
echo "${GREEN}${BOLD}"
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                    🎉 MASS CENTRALIZATION COMPLETE! 🎉               ║"
echo "║                  The Mad Tinker's Empire Expands!                   ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo "${NC}"

echo "${CYAN}📊 Final Report:${NC}"
echo "${GREEN}  ✅ Successfully centralized: $success_count repositories${NC}"
if [ $failure_count -gt 0 ]; then
    echo "${RED}  ❌ Failed to centralize: $failure_count repositories${NC}"
    echo "${YELLOW}     Failed repositories:${NC}"
    for failed in "${failed_repos[@]}"; do
        echo "${RED}       • $failed${NC}"
    done
fi

total_centralized=$((centralized_count + success_count))
total_repos=${#repos_with_cursor[@]}

echo ""
echo "${PURPLE}${BOLD}👑 Mad Tinker's Domain Statistics:${NC}"
echo "${CYAN}  📈 Total repositories under central control: $total_centralized/$total_repos${NC}"

if [ $total_centralized -eq $total_repos ]; then
    echo ""
    echo "${GREEN}${BOLD}${BLINK}"
    echo "╔══════════════════════════════════════════════════════════════════════╗"
    echo "║                       🌟 TOTAL DOMINATION! 🌟                       ║"
    echo "║                All cursor rules are now centralized!                ║"
    echo "║               The Mad Tinker reigns supreme! 👑🔧⚡                  ║"
    echo "╚══════════════════════════════════════════════════════════════════════╝"
    echo "${NC}"
fi

echo ""
echo "${BLUE}💡 Pro Tip: Run this script periodically to catch new repositories!${NC}"
echo "${PURPLE}🔧 The Mad Tinker's tools grow stronger with each centralization! MWAHAHAHA!${NC}" 
