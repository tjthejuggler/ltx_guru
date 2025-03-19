#!/bin/bash
# Sequence Maker - Icon Change Script
# This script automates the process of changing the application icon

# Display help message
show_help() {
    echo "Usage: $0 [options] <path_to_new_icon>"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -n, --name     Specify a name for the icon (default: uses filename)"
    echo ""
    echo "Example:"
    echo "  $0 ~/Pictures/my_new_icon.png"
    echo "  $0 -n custom_icon_name ~/Pictures/my_new_icon.png"
    echo ""
    exit 0
}

# Parse command line arguments
ICON_NAME=""
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            ;;
        -n|--name)
            ICON_NAME="$2"
            shift
            shift
            ;;
        *)
            ICON_PATH="$1"
            shift
            ;;
    esac
done

# Check if icon path is provided
if [ -z "$ICON_PATH" ]; then
    echo "Error: No icon path provided"
    show_help
fi

# Check if the icon file exists
if [ ! -f "$ICON_PATH" ]; then
    echo "Error: Icon file not found at $ICON_PATH"
    exit 1
fi

# Get the project root directory
PROJECT_ROOT="$(pwd)"

# Get the icon filename if no name is specified
if [ -z "$ICON_NAME" ]; then
    ICON_NAME=$(basename "$ICON_PATH")
fi

# Copy the icon to the resources directory
echo "Copying icon to resources directory..."
cp "$ICON_PATH" "$PROJECT_ROOT/sequence_maker/resources/icons/$ICON_NAME"

# Get the current icon name from application.py
CURRENT_ICON=$(grep -o 'get_icon_path("[^"]*")' "$PROJECT_ROOT/sequence_maker/app/application.py" | sed 's/get_icon_path("\(.*\)")/\1/')
echo "Current icon: $CURRENT_ICON"

# Update application.py
echo "Updating application.py..."
sed -i "s|get_icon_path(\"$CURRENT_ICON\")|get_icon_path(\"$ICON_NAME\")|g" "$PROJECT_ROOT/sequence_maker/app/application.py"

# Update main_window.py
echo "Updating main_window.py..."
sed -i "s|get_icon_path(\"$CURRENT_ICON\")|get_icon_path(\"$ICON_NAME\")|g" "$PROJECT_ROOT/sequence_maker/ui/main_window.py"

# Update run.py
echo "Updating run.py..."
sed -i "s|sequence_maker/resources/icons/$CURRENT_ICON|sequence_maker/resources/icons/$ICON_NAME|g" "$PROJECT_ROOT/run.py"

# Update desktop file
echo "Updating desktop file..."
CURRENT_DESKTOP_ICON=$(grep -o 'Icon=.*' "$PROJECT_ROOT/sequence_maker.desktop" | sed 's/Icon=//')
sed -i "s|Icon=$CURRENT_DESKTOP_ICON|Icon=$PROJECT_ROOT/sequence_maker/resources/icons/$ICON_NAME|g" "$PROJECT_ROOT/sequence_maker.desktop"

# Update install_icon.sh
echo "Updating install_icon.sh..."
CURRENT_INSTALL_ICON=$(grep -o 'ICON_PATH="$(pwd)/sequence_maker/resources/icons/[^"]*"' "$PROJECT_ROOT/install_icon.sh" | sed 's/ICON_PATH="$(pwd)\/sequence_maker\/resources\/icons\/\(.*\)"/\1/')
sed -i "s|ICON_PATH=\"\$(pwd)/sequence_maker/resources/icons/$CURRENT_INSTALL_ICON\"|ICON_PATH=\"\$(pwd)/sequence_maker/resources/icons/$ICON_NAME\"|g" "$PROJECT_ROOT/install_icon.sh"

# Make install_icon.sh executable
chmod +x "$PROJECT_ROOT/install_icon.sh"

# Run the icon installation script
echo "Installing the new icon..."
"$PROJECT_ROOT/install_icon.sh"

# Update the launch script environment variable
echo "Updating launch script..."
sed -i "s|export ICON_PATH=.*|export ICON_PATH=$PROJECT_ROOT/sequence_maker/resources/icons/$ICON_NAME|g" "$PROJECT_ROOT/launch_sequence_maker.sh"

echo ""
echo "Icon change complete! The new icon has been installed."
echo "Run ./launch_sequence_maker.sh to test the application with the new icon."
echo ""