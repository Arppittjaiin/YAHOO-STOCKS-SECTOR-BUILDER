@echo off
TITLE Yahoo Stocks Sector Builder
SETLOCAL

:: 1. Navigate to the project directory
CD /D "%~dp0"

:: 2. Check if Python is installed
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    ECHO.
    ECHO ERROR: Python is not installed.
    PAUSE
    EXIT /B 1
)

:: 3. Install missing dependencies (Quietly)
ECHO Verifying dependencies...
python -m pip install -r requirements.txt --quiet --no-warn-script-location

:: 4. Launch the script
ECHO.
ECHO Starting Yahoo Stocks Sector Builder...
ECHO.
python build_symbol_map.py

:: 5. Success/Failure feedback
IF %ERRORLEVEL% NEQ 0 (
    ECHO.
    ECHO [!] The process stopped unexpectedly.
    PAUSE
) ELSE (
    ECHO.
    ECHO ✅ Process completed successfully!
    TIMEOUT /T 10
)

ENDLOCAL
