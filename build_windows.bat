@echo off
REM Windows build script for Task Planner
REM Run this script on Windows to build the .exe file

echo ========================================
echo Building Task Planner for Windows
echo ========================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not available
    echo Please ensure pip is installed with Python
    pause
    exit /b 1
)

REM Install/upgrade required packages
echo Installing required packages...
pip install -r requirements.txt

REM Run the build script
echo Starting build process...
python build.py

REM Check if build was successful
if exist "dist\TaskPlanner*.exe" (
    echo.
    echo ========================================
    echo BUILD SUCCESSFUL!
    echo ========================================
    echo.
    echo Your executable is ready in the 'dist' folder
    echo You can now distribute this .exe file to other Windows computers
    echo.
    dir dist\TaskPlanner*.exe
    echo.
    echo Press any key to open the dist folder...
    pause >nul
    explorer dist
) else (
    echo.
    echo ========================================
    echo BUILD FAILED!
    echo ========================================
    echo.
    echo Please check the error messages above
    echo and ensure all dependencies are installed
    pause
)
