#!/bin/bash

# This script installs the Sequence Maker icon to the system icon theme directories

# Create icon directories if they don't exist
mkdir -p ~/.local/share/icons/hicolor/16x16/apps
mkdir -p ~/.local/share/icons/hicolor/24x24/apps
mkdir -p ~/.local/share/icons/hicolor/32x32/apps
mkdir -p ~/.local/share/icons/hicolor/48x48/apps
mkdir -p ~/.local/share/icons/hicolor/64x64/apps
mkdir -p ~/.local/share/icons/hicolor/128x128/apps
mkdir -p ~/.local/share/icons/hicolor/256x256/apps

# Get the source icon path
ICON_PATH="$(pwd)/sequence_maker/resources/icons/sm_app_icon_better.jpeg"

# Check if the icon exists
if [ ! -f "$ICON_PATH" ]; then
    echo "Error: Icon file not found at $ICON_PATH"
    exit 1
fi

# Create a Python script to resize the icon
cat > resize_icon.py << 'EOF'
from PIL import Image
import sys
import os

def resize_icon(input_path, output_path, size):
    try:
        img = Image.open(input_path)
        img = img.resize((size, size), Image.LANCZOS)
        img.save(output_path)
        return True
    except Exception as e:
        print(f"Error resizing icon: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python resize_icon.py input_path output_path size")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    size = int(sys.argv[3])
    
    if resize_icon(input_path, output_path, size):
        print(f"Successfully resized icon to {size}x{size}")
    else:
        sys.exit(1)
EOF

# Convert and install the icon at different sizes
for size in 16 24 32 48 64 128 256; do
    output_path=~/.local/share/icons/hicolor/${size}x${size}/apps/SequenceMaker.png
    python resize_icon.py "$ICON_PATH" "$output_path" $size
    
    # If Python script fails, just copy the original icon
    if [ $? -ne 0 ]; then
        echo "Python resize failed, copying original icon to $output_path"
        cp "$ICON_PATH" "$output_path"
    fi
    
    echo "Installed icon at size ${size}x${size}"
done

# Clean up the temporary Python script
rm resize_icon.py

# Create ~/.icons directory if it doesn't exist
mkdir -p ~/.icons

# Create a symbolic link to the icon in ~/.icons
ln -sf "$ICON_PATH" ~/.icons/SequenceMaker.png

# Create ~/.local/share/pixmaps directory if it doesn't exist
mkdir -p ~/.local/share/pixmaps

# Copy the icon to the pixmaps directory
cp "$ICON_PATH" ~/.local/share/pixmaps/SequenceMaker.png

# Update icon cache
gtk-update-icon-cache -f -t ~/.local/share/icons/hicolor

# Force desktop file cache update
update-desktop-database ~/.local/share/applications 2>/dev/null || true

# Copy the desktop file to the applications directory
cp "$(pwd)/sequence_maker.desktop" ~/.local/share/applications/

echo "Icon installation complete. The icon should now be available to the desktop environment."