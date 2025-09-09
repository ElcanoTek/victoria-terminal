#!/bin/bash

# Script to manage testing Victoria on a temporary UTM virtual machine

BASE_VM_NAME="macOS Base"
TEST_VM_NAME="macOS Test"

# Check if utmctl is installed
if ! command -v utmctl &> /dev/null; then
    echo "Error: utmctl is not installed or not in your PATH."
    echo "Please install UTM and ensure utmctl is available."
    echo "You can create a symbolic link:"
    echo "sudo ln -sf /Applications/UTM.app/Contents/MacOS/utmctl /usr/local/bin/utmctl"
    exit 1
fi

# Check if the base VM exists
if ! utmctl status "$BASE_VM_NAME" &> /dev/null; then
    echo "Error: Base VM '$BASE_VM_NAME' not found."
    echo "Please create a macOS VM in UTM named '$BASE_VM_NAME'."
    echo "This VM should be configured with a shared directory."
    exit 1
fi

# Clean up any previous test VM
if utmctl status "$TEST_VM_NAME" &> /dev/null; then
    echo "Found an existing test VM. Stopping and deleting it..."
    utmctl stop "$TEST_VM_NAME" --force &> /dev/null
    utmctl delete "$TEST_VM_NAME"
fi

echo "Cloning '$BASE_VM_NAME' to '$TEST_VM_NAME'..."
utmctl clone "$BASE_VM_NAME" --name "$TEST_VM_NAME"

echo "Please manually start '$TEST_VM_NAME'..."
# utmctl start "$TEST_VM_NAME"

echo "------------------------------------------------------------------"
echo "The test VM '$TEST_VM_NAME' is starting up."
echo "Once the VM has booted, please do the following:"
echo "1. Copy the Victoria.app.zip to the test vm"
echo "2. Install Victoria.app by copying it to the Applications folder"
echo "3. Test the Victoria application."
echo "------------------------------------------------------------------"

read -p "Press [Enter] after you have finished testing to clean up the VM..."

echo "Stopping '$TEST_VM_NAME'..."
utmctl stop "$TEST_VM_NAME" --force

echo "Deleting '$TEST_VM_NAME'..."
utmctl delete "$TEST_VM_NAME"

echo "Cleanup complete."
