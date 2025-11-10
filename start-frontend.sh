#!/bin/bash

# StarHub Communications Generator - Frontend Startup Script

echo "================================================"
echo "StarHub Communications Generator - Frontend"
echo "================================================"

# Navigate to frontend directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "❌ node_modules not found!"
    echo "Installing dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ npm install failed"
        exit 1
    fi
    echo "✅ Dependencies installed"
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found"
    echo "Creating default .env..."
    echo "VITE_API_URL=http://localhost:8000" > .env
    echo "✅ .env file created with default API URL"
fi

# Start development server
echo "================================================"
echo "Starting Vite development server..."
echo "Frontend: http://localhost:5173"
echo "================================================"
echo ""

npm run dev
