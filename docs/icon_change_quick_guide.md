# Quick Guide: Changing the Sequence Maker Icon

This is a concise, step-by-step guide for changing the Sequence Maker application icon. For more detailed explanations, see `changing_app_icon.md`.

## Automated Method (Recommended)

We've created a script that automates the entire icon change process:

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

## Manual Method

If you prefer to change the icon manually, follow these steps:

1. **Add your new icon file**
   ```bash
   # Copy your new icon to the icons directory
   cp /path/to/your/new_icon.png sequence_maker/resources/icons/
   ```

2. **Update the application code**
   ```bash
   # Edit application.py to use the new icon
   sed -i 's/sm_app_icon_better-removebg-preview.png/your_new_icon.png/g' sequence_maker/app/application.py
   
   # Edit main_window.py to use the new icon
   sed -i 's/sm_app_icon_better-removebg-preview.png/your_new_icon.png/g' sequence_maker/ui/main_window.py
   
   # Edit run.py to use the new icon
   sed -i 's/sm_app_icon_better-removebg-preview.png/your_new_icon.png/g' run.py
   ```

3. **Update the desktop file**
   ```bash
   # Edit the desktop file to use the absolute path to the new icon
   sed -i 's|/home/twain/Projects/ltx_guru/sequence_maker/resources/icons/sm_app_icon_better-removebg-preview.png|/home/twain/Projects/ltx_guru/sequence_maker/resources/icons/your_new_icon.png|g' sequence_maker.desktop
   ```

4. **Update the icon installation script**
   ```bash
   # Edit the icon installation script to use the new icon
   sed -i 's|sm_app_icon_better-removebg-preview.png|your_new_icon.png|g' install_icon.sh
   ```

5. **Install the new icon**
   ```bash
   # Make the script executable
   chmod +x install_icon.sh
   
   # Run the icon installation script
   ./install_icon.sh
   ```

6. **Test the application**
   ```bash
   # Run the application
   ./launch_sequence_maker.sh
   ```

## Verification

After following these steps, verify that:

1. The splash screen shows the new icon
2. The window title bar shows the new icon
3. The taskbar/dock shows the new icon
4. The application switcher shows the new icon

## Troubleshooting

If the icon doesn't appear correctly:

1. Check that all file paths are correct
2. Ensure the icon file exists and is readable
3. Try logging out and logging back in
4. Check the application logs for any errors

For more detailed troubleshooting, refer to the full documentation in `changing_app_icon.md`.