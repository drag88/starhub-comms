#!/bin/bash

# StarHub Communications Generator - Backend Startup Script

echo "================================================"
echo "StarHub Communications Generator - Backend"
echo "================================================"

# Navigate to backend directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/backend"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run setup first:"
    echo "  cd backend"
    echo "  uv venv"
    echo "  uv pip install -e \".[dev]\""
    exit 1
fi

# Activate virtual environment
echo "✅ Activating virtual environment..."
source .venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found"
    echo "Creating .env from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ .env file created"
        echo "⚠️  Please add your ANTHROPIC_API_KEY to backend/.env"
    else
        echo "❌ .env.example not found"
        echo "Please create backend/.env with:"
        echo "  ANTHROPIC_API_KEY=your_key_here"
        echo "  DATABASE_URL=sqlite:///./starhub_comms.db"
    fi
fi

# Check for ANTHROPIC_API_KEY
if ! grep -q "ANTHROPIC_API_KEY=" .env 2>/dev/null || grep -q "ANTHROPIC_API_KEY=$" .env 2>/dev/null || grep -q "ANTHROPIC_API_KEY=your_" .env 2>/dev/null; then
    echo "⚠️  Warning: ANTHROPIC_API_KEY not configured in .env"
    echo "Generation functionality will not work without a valid API key"
    echo "Get your key from: https://console.anthropic.com/"
fi

# Start server
echo "================================================"
echo "Starting FastAPI backend..."
echo "Server: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo "================================================"
echo ""

uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
