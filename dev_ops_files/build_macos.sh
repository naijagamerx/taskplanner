#!/bin/bash
# macOS build script for Task Planner
# Run this script on macOS to build the .app file

echo "========================================"
echo "Building Task Planner for macOS"
echo "========================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ from https://python.org"
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "ERROR: pip3 is not available"
    echo "Please ensure pip is installed with Python"
    exit 1
fi

# Install/upgrade required packages
echo "Installing required packages..."
pip3 install -r requirements.txt

# Run the build script
echo "Starting build process..."
python3 build.py

# Check if build was successful
if ls dist/TaskPlanner*.app 1> /dev/null 2>&1; then
    echo ""
    echo "========================================"
    echo "BUILD SUCCESSFUL!"
    echo "========================================"
    echo ""
    echo "Your application is ready in the 'dist' folder"
    echo "You can now distribute this .app file to other Mac computers"
    echo ""
    ls -la dist/TaskPlanner*.app
    echo ""
    echo "To install: Drag the .app file to your Applications folder"
    echo "To distribute: Create a .dmg file or zip the .app"
    echo ""
    read -p "Press Enter to open the dist folder..."
    open dist
else
    echo ""
    echo "========================================"
    echo "BUILD FAILED!"
    echo "========================================"
    echo ""
    echo "Please check the error messages above"
    echo "and ensure all dependencies are installed"
    read -p "Press Enter to continue..."
fi
