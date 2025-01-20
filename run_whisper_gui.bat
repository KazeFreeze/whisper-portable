@echo off
:: Check if virtual environment exists
if not exist "whisper-env\Scripts\activate.bat" (
    echo Virtual environment not found. Please run setup first.
    pause
    exit /b 1
)

:: Activate the virtual environment
call whisper-env\Scripts\activate.bat

:: Check if activation was successful
if errorlevel 1 (
    echo Failed to activate virtual environment
    pause
    exit /b 1
)

:: Run the GUI application
python whisper_gui\main.py

:: Keep the window open if there's an error
if errorlevel 1 (
    echo An error occurred while running the application
    pause
)