#!/bin/zsh

# Define the source and destination paths
SOURCE_DIR=".specstory/history"
DEST_DIR="/Users/d.edens/lab/madness_interactive/docs/cursor_chathistory/$(basename $PWD)"

# Move the history folder to the new location
mv "$SOURCE_DIR" "$DEST_DIR"

# Display the paths and ask for confirmation
echo "The history folder has been moved."
echo "Source Directory: $SOURCE_DIR"
echo "Destination Directory: $DEST_DIR/$(basename $SOURCE_DIR)"
read -q "CONFIRM?Do you want to create a symbolic link back to the original location? (y/n) "

if [[ $CONFIRM == "y" ]]; then
    # Create a symbolic link back to the original location
    ln -s "$DEST_DIR/$(basename $SOURCE_DIR)" "$SOURCE_DIR"
    echo "Symbolic link created."
else
    echo "Symbolic link not created. Please create it manually if needed."
fi
