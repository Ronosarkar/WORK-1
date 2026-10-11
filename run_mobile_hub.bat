@echo off
title Media Variant Studio - Phone Hub
echo ========================================================
echo   Starting Media Variant Studio Phone Access Server...
echo ========================================================
echo.
cd /d "%~dp0"

python server.py
pause
