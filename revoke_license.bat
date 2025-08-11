@echo off
title Task Planner - License Revocation Tool
color 0E

echo.
echo ========================================
echo    Task Planner License Revocation
echo ========================================
echo.

REM Get the current directory
set "APP_DIR=%~dp0"

REM Check if Python is available
py --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again.
    pause
    exit /b 1
)

REM Run Python script to revoke license
py "%APP_DIR%revoke_license.py"

if errorlevel 1 (
    echo.
    echo ❌ License revocation failed.
    pause
    exit /b 1
)

echo.
echo ✅ License revocation completed successfully!
echo.
echo NOTE: If Task Planner is currently running, you may need to
echo       restart it for the changes to take effect.
echo.
pause
