#!/bin/bash

# Shell script to set up the Victoria application in the macOS VM

echo "Looking for Victoria app zip in /Users/Shared/..."

# The shared directory in UTM is typically /Users/Shared
# We are looking for a file like Victoria-2023.10.27.app.zip
zip_path=$(find /Users/Shared -name "Victoria-*.app.zip" -print -quit)

if [ -n "$zip_path" ]; then
    filename=$(basename "$zip_path")
    echo "Found application archive: $filename"

    # Define the destination path in the Applications folder
    apps_dir="/Applications"

    echo "Unzipping '$filename' to '$apps_dir'..."
    unzip -o "$zip_path" -d "$apps_dir"

    # The app name is always Victoria.app
    app_name="Victoria.app"
    app_path="$apps_dir/$app_name"

    if [ -d "$app_path" ]; then
        echo "Successfully installed Victoria.app to /Applications"
        echo "------------------------------------------------------------------"
        echo "Setup complete!"
        echo "You can now find 'Victoria' in your Applications folder."
        echo "------------------------------------------------------------------"
    else
        echo "------------------------------------------------------------------"
        echo "Error: Failed to unzip the application to the Applications folder."
        echo "Please check permissions and try again."
        echo "------------------------------------------------------------------"
    fi

else
    echo "------------------------------------------------------------------"
    echo "Victoria application zip not found in the /Users/Shared directory."
    echo "Please download the 'Victoria-*.app.zip' from GitHub Releases"
    echo "and place it in the shared directory configured in your UTM VM."
    echo "Then, run this script again."
    echo "------------------------------------------------------------------"
fi
