#!/bin/bash

# World AI Agent System - Startup Script
# This script starts the World AI Agent System

echo "🌍 Starting World AI Agent System..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Please run this script from the World directory."
    exit 1
fi

# Check for Gemini API key
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  Warning: GEMINI_API_KEY environment variable not set"
    echo "   Some features may not work properly"
    echo "   Set it with: export GEMINI_API_KEY='your-api-key'"
    echo ""
    read -p "Do you want to continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "📦 Installing dependencies..."
    pip3 install -r requirements.txt
fi

# Install Node.js dependencies if package.json exists
if [ -f "scrapers/webScraper/backend/package.json" ]; then
    echo "📦 Installing Node.js dependencies..."
    cd scrapers/webScraper/backend
    npm install
    cd ../../..
fi

# Make main.py executable
chmod +x main.py

# Start the system
echo "🚀 Starting World AI Agent System..."
echo "   Use Ctrl+C to stop the system"
echo ""

# Check command line arguments
if [ "$1" = "--interactive" ]; then
    python3 main.py --interactive
elif [ "$1" = "--api" ]; then
    python3 main.py --start-api
elif [ "$1" = "--all" ]; then
    python3 main.py --start-all
else
    # Default to interactive mode
    python3 main.py --interactive
fi
