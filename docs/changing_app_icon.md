# Changing the Sequence Maker Application Icon

This document provides comprehensive instructions for changing the application icon for the Sequence Maker application.

## Automated Icon Change (Recommended)

We've created a script that automates the entire icon change process. This is the recommended method for changing the icon:

```bash
# Make the script executable
chmod +x change_icon.sh

# Run the script with the path to your new icon
./change_icon.sh /path/to/your/new_icon.png

# Optionally specify a custom name for the icon
./change_icon.sh -n custom_name.png /path/to/your/new_icon.png
```

The script will:
1. Copy your icon to the resources directory
2. Update all necessary files to reference the new icon
3. Install the icon to the system icon theme
4. Update the desktop file

After running the script, you can test the application with:
```bash
./launch_sequence_maker.sh
```

For those who prefer to understand the process in detail or need to make manual changes, the rest of this document explains the complete process step by step.

## Overview of Manual Icon Change

Changing an application icon in Linux desktop environments can be complex due to the multiple mechanisms involved in icon display:

1. **System Icon Theme**: Icons installed in the system icon theme directories
2. **Application Window Icon**: Set via PyQt6 in the application code
3. **Desktop Entry Icon**: Referenced in the .desktop file
4. **Window Manager Class**: Used to associate the window with the correct icon
5. **Icon Caches**: Various caches that need to be cleared for changes to take effect

To properly change the application icon, you need to update all of these components. The following steps provide a thorough approach that has been tested to work reliably.

## Step 1: Prepare Your New Icon

1. Create your new icon in PNG format with a recommended size of at least 256x256 pixels
2. The icon should have a transparent background for best results
3. Place the icon file in the `sequence_maker/resources/icons/` directory
4. Choose a descriptive filename (e.g., `my_new_icon.png`)

## Step 2: Update the Icon References in Application Code

### 2.1 Update the Main Application Code

Edit `sequence_maker/app/application.py` and update the icon path:

```python
# Get icon path - use absolute path for better compatibility
icon_path = get_icon_path("my_new_icon.png")
self.logger.info(f"Setting application icon from: {icon_path}")
```

Also ensure the icon is set in multiple ways for maximum compatibility:

```python
# Set the application icon in multiple ways to ensure it's used
self.qt_app.setWindowIcon(self.app_icon)

# Set the icon as a property
self.qt_app.setProperty("windowIcon", self.app_icon)

# Set the icon for all windows
QIcon.setThemeName("hicolor")
QIcon.setThemeSearchPaths([os.path.expanduser("~/.local/share/icons"), os.path.expanduser("~/.icons")])
```

### 2.2 Update the Main Window Code

Edit `sequence_maker/ui/main_window.py` and update the icon path:

```python
# Set window icon - use the PNG version
icon_path = get_icon_path("my_new_icon.png")
self.logger.info(f"Setting window icon from: {icon_path}")
```

### 2.3 Update the Run Script

Edit `run.py` and update the icon path:

```python
# Set icon path
icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "sequence_maker/resources/icons/my_new_icon.png")
```

## Step 3: Update the Desktop Entry File

Edit `sequence_maker.desktop` and update the icon reference to use the absolute path to the icon:

```
[Desktop Entry]
Type=Application
Name=Sequence Maker
Comment=A tool for creating color sequences for LTX juggling balls
Exec=/home/twain/Projects/ltx_guru/launch_sequence_maker.sh
Icon=/home/twain/Projects/ltx_guru/sequence_maker/resources/icons/my_new_icon.png
Terminal=false
Categories=Utility;Development;
StartupWMClass=SequenceMaker
StartupNotify=true
```

Using an absolute path ensures the icon is found regardless of how the application is launched.

## Step 4: Update the Icon Installation Script

Edit `install_icon.sh` and update the source icon path:

```bash
# Get the source icon path
ICON_PATH="$(pwd)/sequence_maker/resources/icons/my_new_icon.png"
```

The script will:
1. Create properly sized versions of your icon (16x16 to 256x256)
2. Install them to the system icon theme directories
3. Create symbolic links in additional locations for maximum compatibility
4. Clear icon caches to ensure the new icon is used

## Step 5: Update the Launch Script

The `launch_sequence_maker.sh` script sets environment variables and runs the icon installation script. No changes are needed unless you want to add additional environment variables for specific desktop environments.

## Step 6: Install the New Icon

Run the icon installation script to install the new icon to all necessary locations:

```bash
chmod +x install_icon.sh
./install_icon.sh
```

This script will:
1. Install the icon to the system icon theme directories in multiple sizes
2. Create a symbolic link in the ~/.icons directory
3. Copy the icon to the ~/.local/share/pixmaps directory
4. Clear the icon cache
5. Update the desktop file database
6. Copy the desktop file to the applications directory

## Step 7: Test the Application

Run the application to verify that the new icon is displayed correctly:

```bash
./launch_sequence_maker.sh
```

The application should now display your new icon in:
- The taskbar/dock
- The window title bar
- The application switcher
- The splash screen
- Any desktop shortcuts

## Troubleshooting

If the icon is not displaying correctly after following all steps:

1. **Check Icon Paths**: Ensure all paths to the icon file are correct and the file exists
2. **Verify Icon Installation**: Check that the icon files were created in:
   - `~/.local/share/icons/hicolor/*/apps/SequenceMaker.png`
   - `~/.icons/SequenceMaker.png`
   - `~/.local/share/pixmaps/SequenceMaker.png`
3. **Clear All Icon Caches**:
   ```bash
   rm -rf ~/.cache/icon-cache.kcache
   gtk-update-icon-cache -f -t ~/.local/share/icons/hicolor
   ```
4. **Verify Desktop File**: Check that the desktop file was copied to:
   - `~/.local/share/applications/sequence_maker.desktop`
5. **Check Window Class**: Ensure the StartupWMClass in the .desktop file matches the application name set in the code
6. **Try Different Icon Formats**: Some desktop environments work better with SVG or ICO formats
7. **Log Out and Log Back In**: Some icon cache changes require a session restart

## Additional Notes

- The icon installation script uses Python with PIL (Pillow) to resize the icon to different sizes. Make sure PIL is installed (`pip install pillow`).
- Different desktop environments (GNOME, KDE, XFCE, etc.) may have different requirements for icon display. The approach in this document aims to be compatible with all major desktop environments.
- The application uses a custom style (`CustomIconStyle`) to force the icon to be used in various contexts within the application.
- Using absolute paths for icons in the .desktop file is generally more reliable than using icon theme names.
- The StartupWMClass in the .desktop file must match the application name set in the code for proper window-icon association.