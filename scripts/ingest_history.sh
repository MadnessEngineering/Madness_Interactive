#!/bin/zsh

# Define the source and destination paths
SOURCE_DIR=".specstory/history"
DEST_DIR="/Users/d.edens/lab/madness_interactive/docs/cursor_chathistory/$(basename $PWD)"

# Move the history folder to the new location and create a symlink or skip if it already exists
if [ -d "$DEST_DIR" ]; then
    echo "Destination directory already exists. Skipping..."
else
    mv "$SOURCE_DIR" "$DEST_DIR"
    ln -s "$DEST_DIR" "$SOURCE_DIR"
fi

# Display the paths and ask for confirmation
echo "The history folder has been moved."
echo "Source Directory: $SOURCE_DIR"
echo "Destination Directory: $DEST_DIR"
echo $(realpath $SOURCE_DIR)
echo $(realpath $DEST_DIR)

input()

ln -s "$DEST_DIR" "$SOURCE_DIR"
