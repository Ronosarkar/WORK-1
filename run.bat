@echo off
title Media Variant & Metadata Studio
echo ========================================================
echo   Media Variant ^& Metadata Studio - Launcher
echo ========================================================
echo.

cd /d "%~dp0"

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not found on PATH!
    echo Please install Python 3.10+ from https://www.python.org
    pause
    exit /b 1
)

:: Verify dependencies
python -c "import PySide6, PIL, flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Installing missing Python libraries...
    python -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install packages.
        pause
        exit /b 1
    )
)

:: Verify FFmpeg binaries
if not exist "bin\ffmpeg.exe" (
    echo [INFO] Setting up FFmpeg...
    python setup_ffmpeg.py
)

:: Launch the Studio directly
echo [OK] Starting Media Variant & Metadata Studio...
python main.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] The application closed unexpectedly.
    pause
)
