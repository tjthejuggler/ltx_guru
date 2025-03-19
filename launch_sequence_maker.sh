#!/bin/bash

# Set environment variables to help with icon display
export QT_QPA_PLATFORMTHEME=gtk3
export RESOURCE_NAME=SequenceMaker
export XDG_CURRENT_DESKTOP=${XDG_CURRENT_DESKTOP:-GNOME}
export QT_STYLE_OVERRIDE=gtk3
export XDG_DATA_DIRS=${XDG_DATA_DIRS}:~/.local/share
export ICON_PATH=/home/twain/Projects/ltx_guru/sequence_maker/resources/icons/sm_app_icon_better.jpeg

# Change to the project directory
cd /home/twain/Projects/ltx_guru

# Make sure the icon installation script is executable
chmod +x install_icon.sh

# Install the icon (this will create properly sized icons in the system icon theme)
./install_icon.sh

# Clear icon cache more aggressively
rm -rf ~/.cache/icon-cache.kcache
gtk-update-icon-cache -f -t ~/.local/share/icons/hicolor

# Run the application
python run.py