#!/bin/bash
# Quick Start Script for Assessment-GliderAI
# This script helps you get started quickly on Linux/Mac

echo "========================================"
echo "  Assessment-GliderAI Setup"
echo "========================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "IMPORTANT: Edit .env file and add your OPENAI_API_KEY"
    echo "Default admin password is 'admin123' - CHANGE IT!"
    echo ""
    read -p "Press enter to continue..."
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
echo ""

echo "Starting Flask development server..."
echo ""
echo "Access the app at:"
echo "  - Main App: http://127.0.0.1:5000"
echo "  - Admin Panel: http://127.0.0.1:5000/admin.html"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python app.py
