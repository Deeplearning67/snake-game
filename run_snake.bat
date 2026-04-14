@echo off
chcp 65001 >nul 2>&1
echo Starting Snake Game...
python snake_game.py
if errorlevel 1 (
    echo.
    echo Game error! Press any key to exit...
    pause >nul
)
