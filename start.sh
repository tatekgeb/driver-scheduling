#!/bin/bash
# Start script for Railway deployment
# Ensures dependencies are installed before starting

echo "Installing Python dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

echo "Current directory: $(pwd)"
echo "Starting Flask application..."
# Railway mounts code in /app, so we should be there already
# But ensure we're in the right place
if [ -f "api/app.py" ]; then
    echo "Found api/app.py, running from current directory"
    python3 api/app.py
elif [ -f "/app/api/app.py" ]; then
    echo "Found /app/api/app.py, changing to /app"
    cd /app
    python3 api/app.py
else
    echo "ERROR: Cannot find api/app.py"
    echo "Current directory contents:"
    ls -la
    exit 1
fi
