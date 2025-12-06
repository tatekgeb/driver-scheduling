#!/bin/bash
# Start script for Railway deployment
# Ensures dependencies are installed before starting

echo "Installing Python dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

echo "Starting Flask application from project root..."
# Change to script directory (project root) to ensure relative paths work correctly
cd "$(dirname "$0")"
python3 api/app.py
