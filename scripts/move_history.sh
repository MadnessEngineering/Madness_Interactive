#!/bin/zsh

SOURCE_DIR=".specstory/history"
DEST_DIR="/Users/d.edens/lab/madness_interactive/docs/cursor_chathistory/$(basename $PWD)"

# Move the history folder to the new location
mv "$SOURCE_DIR" "$DEST_DIR"

# Display the paths and ask for confirmation
echo "The history folder has been moved."
echo "Source Directory: $SOURCE_DIR"
echo "Destination Directory: $DEST_DIR/$(basename $SOURCE_DIR)"

# Create a symbolic link
ln -s "$DEST_DIR" "$SOURCE_DIR"

# Change to the destination directory and commit
cd "/Users/d.edens/lab/madness_interactive/docs/cursor_chathistory"
git add .
git commit -m "Move .specstory/history to cursor_chathistory: SOURCE_DIR=$SOURCE_DIR, DEST_DIR=$DEST_DIR" 
