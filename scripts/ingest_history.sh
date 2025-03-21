#!/bin/zsh

# Define the source and destination paths
SOURCE_DIR=".specstory/history"
DEST_DIR="/Users/d.edens/lab/madness_interactive/docs/cursor_chathistory/$(basename $PWD)"

# Move the history folder to the new location
mv "$SOURCE_DIR" "$DEST_DIR"

# Display the paths and ask for confirmation
echo "The history folder has been moved."
echo "Source Directory: $SOURCE_DIR"
echo "Destination Directory: $DEST_DIR"

input()

ln -s "$DEST_DIR" "$SOURCE_DIR"
