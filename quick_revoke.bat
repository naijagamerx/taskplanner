@echo off
title Task Planner - Quick License Revoke
color 0E

echo.
echo ========================================
echo    Quick License Revocation
echo ========================================
echo.

REM Get the current directory
set "APP_DIR=%~dp0"

echo Revoking license on this computer...
echo.

REM Run Python script to quickly revoke license
py "%APP_DIR%revoke_license.py" --quick

if errorlevel 1 (
    echo ❌ License revocation failed.
) else (
    echo.
    echo ✅ License revocation completed!
    echo    Restart Task Planner to see the license activation window.
)

echo.
timeout /t 3 /nobreak >nul
