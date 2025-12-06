#!/bin/bash
# Start script for Railway deployment
# Ensures dependencies are installed before starting

echo "Installing Python dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

echo "Starting Flask application..."
cd api
python3 app.py

