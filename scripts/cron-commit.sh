#!/bin/bash

# Usage: 0/15 * * * * /path/to/this/script.sh [directory]
#
# Parameters:
#   directory (optional): Path to git repository to monitor
#                        If not provided, uses current directory
#
# Environment Variables:
#   CRON_COMMIT_AI: Set to enable AI-generated commit messages using ollama qwen2.5
#                   Example: export CRON_COMMIT_AI=1
#
# Examples:
#   ./cron-commit.sh /Users/d.edens/.hammerspoon/data
#   ./cron-commit.sh ~/projects/my-repo
#   ./cron-commit.sh   # uses current directory
#   CRON_COMMIT_AI=1 ./cron-commit.sh   # uses AI for commit messages

export AWSIP=${AWSIP:-"your.mqtt.server.ip"}
export AWSPORT=${AWSPORT:-"1883"}  # or your MQTT port

# Set PATH to ensure git and homebrew tools are available
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"

# Function to generate AI commit message using ollama qwen2.5
generate_ai_commit_message() {
    local changed_files="$1"
    local file_count="$2"

    # Check if ollama is available
    if ! command -v ollama >/dev/null 2>&1; then
        echo "Warning: ollama not found, falling back to standard commit message" >&2
        return 1
    fi

    # Create a prompt for the AI to generate a good commit message
    local prompt="You are a git commit message generator. Based on the following changed files, generate a concise, conventional commit message (50 chars or less for the title). Focus on the main purpose of the changes.

Changed files ($file_count):
$changed_files

Generate only the commit message title, no explanation needed. Use conventional commit format when appropriate (feat:, fix:, docs:, etc.)."

    # Call ollama with qwen2.5 model
    local ai_message
    ai_message=$(echo "$prompt" | ollama run qwen2.5 2>/dev/null | head -1 | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//')

    # Validate the AI response
    if [ -n "$ai_message" ] && [ ${#ai_message} -gt 5 ] && [ ${#ai_message} -lt 100 ]; then
        echo "AI-generated: $ai_message"
        return 0
    else
        echo "Warning: AI generated invalid commit message, falling back to standard" >&2
        return 1
    fi
}

# Get directory parameter or use current directory
TARGET_DIR="${1:-$(pwd)}"

# Validate and change to the repository directory
if [ ! -d "$TARGET_DIR" ]; then
    echo "Error: Directory '$TARGET_DIR' does not exist" >&2
    exit 1
fi

cd "$TARGET_DIR" || {
    echo "Error: Cannot change to directory '$TARGET_DIR'" >&2
    exit 1
}

# Get repository name for MQTT topic (basename of directory)
REPO_NAME=$(basename "$TARGET_DIR")

# Check if there are any changes (including untracked files)
if ! git diff --quiet HEAD || [ -n "$(git ls-files --others --exclude-standard)" ]; then
    # There are changes, so add and commit them
    git add .

    # Get list of files that will be committed (now that they're staged)
    ALL_CHANGED_FILES=$(git diff --cached --name-only)

    # Create commit message with file names
    FILE_COUNT=$(echo "$ALL_CHANGED_FILES" | wc -l)

    # Generate commit message (AI or standard)
    if [ -n "$CRON_COMMIT_AI" ]; then
        # Try to generate AI commit message
        export COMMIT_MSG=$(generate_ai_commit_message "$ALL_CHANGED_FILES" "$FILE_COUNT")

        # If AI generation failed, fall back to standard message
        if [ $? -ne 0 ] || [ -z "$COMMIT_MSG" ]; then
            if [ $FILE_COUNT -le 5 ]; then
                FILE_LIST=$(echo "$ALL_CHANGED_FILES" | tr '\n' ',' | sed 's/,$//')
                export COMMIT_MSG="Auto-commit: Updated $FILE_COUNT files ($FILE_LIST)"
            else
                FIRST_FILES=$(echo "$ALL_CHANGED_FILES" | head -3 | tr '\n' ',' | sed 's/,$//')
                export COMMIT_MSG="Auto-commit: Updated $FILE_COUNT files ($FIRST_FILES, and others)"
            fi
        fi
    else
        # Standard commit message generation
        if [ $FILE_COUNT -le 5 ]; then
            # If 5 or fewer files, list them all
            FILE_LIST=$(echo "$ALL_CHANGED_FILES" | tr '\n' ',' | sed 's/,$//')
            export COMMIT_MSG="Auto-commit: Updated $FILE_COUNT files ($FILE_LIST)"
        else
            # If more than 5 files, show count and first few
            FIRST_FILES=$(echo "$ALL_CHANGED_FILES" | head -3 | tr '\n' ',' | sed 's/,$//')
            export COMMIT_MSG="Auto-commit: Updated $FILE_COUNT files ($FIRST_FILES, and others)"
        fi
    fi

    # Create commit with timestamp
    TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

    if git commit -m "$COMMIT_MSG"; then
        # Get the commit hash
        COMMIT_HASH=$(git rev-parse --short HEAD)

        # Push to remote
        git push || echo "Push failed"

        # Notification/status update
        # Log to a status file
        echo "$(date): Updated chats repository - commit $COMMIT_HASH" >> /tmp/chat_updates.log

        # Send enhanced MQTT status with commit hash
        if command -v mosquitto_pub >/dev/null 2>&1; then
            MQTT_TIMESTAMP=$(date +%Y-%m-%d.%H:%M)
            mosquitto_pub -h "$AWSIP" -p "$AWSPORT" -t "status/git/${REPO_NAME}/commit" -m "${MQTT_TIMESTAMP}=:=${COMMIT_MSG} ${COMMIT_HASH} =:= Updated ${FILE_COUNT} files"
        fi

    else
        echo "$(date): Git commit failed in $TARGET_DIR" >> /tmp/chat_updates.log
        exit 1
    fi
else
    # No changes to commit


    # Send MQTT status for no changes case if HAMMER_DEBUG is set
    if [ -n "$HAMMER_DEBUG" ]; then
        echo "$(date): No changes to commit in $TARGET_DIR" >> /tmp/chat_updates.log
        if command -v mosquitto_pub >/dev/null 2>&1; then
            MQTT_TIMESTAMP=$(date +%Y-%m-%d.%H:%M)
            mosquitto_pub -h "$AWSIP" -p "$AWSPORT" -t "status/git/${REPO_NAME}/commit" -m "${MQTT_TIMESTAMP}=:=No changes to commit"
        fi
    fi
fi
