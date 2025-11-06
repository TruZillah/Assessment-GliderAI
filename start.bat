@echo off
REM Quick Start Script for Assessment-GliderAI
REM This script helps you get started quickly

echo ========================================
echo   Assessment-GliderAI Setup
echo ========================================
echo.

REM Check if .env exists
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo.
    echo IMPORTANT: Edit .env file and add your OPENAI_API_KEY
    echo Default admin password is 'admin123' - CHANGE IT!
    echo.
    pause
)

REM Check if Flask is installed
python -c "import flask" 2>nul
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    echo.
)

echo Starting Flask development server...
echo.
echo Access the app at:
echo   - Main App: http://127.0.0.1:5000
echo   - Admin Panel: http://127.0.0.1:5000/admin.html
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py
