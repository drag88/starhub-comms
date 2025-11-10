#!/bin/bash

# StarHub Communications Generator - Full Application Startup Script
# Starts both backend and frontend servers

echo "========================================================"
echo "  StarHub Customer Communications Generator"
echo "========================================================"
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "========================================================"
    echo "Shutting down servers..."
    echo "========================================================"
    if [ ! -z "$BACKEND_PID" ]; then
        echo "Stopping backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID 2>/dev/null
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        echo "Stopping frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID 2>/dev/null
    fi
    echo "Cleanup complete. Goodbye!"
    exit 0
}

# Set trap to cleanup on Ctrl+C
trap cleanup SIGINT SIGTERM

# Check if backend setup exists
if [ ! -d "$SCRIPT_DIR/backend/.venv" ]; then
    echo "❌ Backend not set up!"
    echo ""
    echo "Please run setup first:"
    echo "  cd backend"
    echo "  uv venv"
    echo "  uv pip install -e \".[dev]\""
    echo ""
    exit 1
fi

# Check if frontend setup exists
if [ ! -d "$SCRIPT_DIR/frontend/node_modules" ]; then
    echo "❌ Frontend not set up!"
    echo ""
    echo "Please run setup first:"
    echo "  cd frontend"
    echo "  npm install"
    echo ""
    exit 1
fi

# Start backend
echo "========================================================"
echo "1. Starting Backend Server..."
echo "========================================================"
cd "$SCRIPT_DIR/backend"
source .venv/bin/activate
nohup uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"
echo "   Logs: logs/backend.log"

# Wait for backend to start
echo "   Waiting for backend to initialize..."
sleep 5

# Check if backend is running
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "❌ Backend failed to start"
    echo "   Check logs/backend.log for details"
    exit 1
fi

# Test backend health
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy"
else
    echo "⚠️  Backend may not be fully ready yet"
fi

echo ""

# Start frontend
echo "========================================================"
echo "2. Starting Frontend Server..."
echo "========================================================"
cd "$SCRIPT_DIR/frontend"
nohup npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "✅ Frontend started (PID: $FRONTEND_PID)"
echo "   Logs: logs/frontend.log"

# Wait for frontend to start
echo "   Waiting for frontend to initialize..."
sleep 3

echo ""
echo "========================================================"
echo "✅ Application Started Successfully!"
echo "========================================================"
echo ""
echo "Access the application:"
echo "  🌐 Frontend:  http://localhost:5173"
echo "  🔧 Backend:   http://localhost:8000"
echo "  📚 API Docs:  http://localhost:8000/docs"
echo ""
echo "Process IDs:"
echo "  Backend:  $BACKEND_PID"
echo "  Frontend: $FRONTEND_PID"
echo ""
echo "Logs:"
echo "  Backend:  logs/backend.log"
echo "  Frontend: logs/frontend.log"
echo ""
echo "Press Ctrl+C to stop all servers"
echo "========================================================"
echo ""

# Create logs directory if it doesn't exist
mkdir -p "$SCRIPT_DIR/logs"

# Wait for processes
wait
