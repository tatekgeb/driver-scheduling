#!/bin/bash
# Build script for Railway deployment

echo "Building React frontend..."
cd desktop
npm install
npm run build:react
cd ..

echo "Installing Python dependencies..."
pip install -r api/requirements.txt

echo "Build complete!"

