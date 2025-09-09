#!/bin/bash

# Shell script to set up the Victoria AppImage in the Ubuntu VM

echo "Looking for Victoria AppImage in /vagrant/installers..."

# Find the AppImage file in the installers directory.
appimage_path=$(find /vagrant/installers -name "Victoria-*.AppImage" -print -quit)

if [ -n "$appimage_path" ]; then
    filename=$(basename "$appimage_path")
    echo "Found AppImage: $filename"

    # Define the destination path on the user's desktop
    desktop_path="/home/vagrant/Desktop/$filename"

    echo "Copying AppImage to the Desktop at $desktop_path"
    cp "$appimage_path" "$desktop_path"

    echo "Making the AppImage executable..."
    chmod +x "$desktop_path"

    # Set the owner to the vagrant user so they can run it without issues
    chown vagrant:vagrant "$desktop_path"

    echo "------------------------------------------------------------------"
    echo "Setup complete!"
    echo "You can now log in to the Ubuntu desktop and double-click the"
    echo "'$filename' icon on the Desktop to run the application."
    echo "------------------------------------------------------------------"

else
    echo "------------------------------------------------------------------"
    echo "Victoria AppImage not found in the /vagrant/installers directory."
    echo "Please download the 'Victoria-*.AppImage' from GitHub Releases"
    echo "and place it in the 'installers/' directory of this project on your host machine."
    echo "Then, run 'vagrant provision' or 'vagrant reload --provision'."
    echo "------------------------------------------------------------------"
fi
