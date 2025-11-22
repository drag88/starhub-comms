#!/bin/bash

# StarHub Communications Generator - Complete Setup Script
# This script sets up the entire project using UV for Python dependency management

set -e  # Exit on error

echo "================================================"
echo "StarHub Communications Generator - Setup"
echo "================================================"
echo ""

# Get project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if UV is installed
echo "Checking dependencies..."
if ! command -v uv &> /dev/null; then
    print_error "UV is not installed!"
    echo ""
    echo "Please install UV first:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo ""
    echo "Or visit: https://github.com/astral-sh/uv"
    exit 1
fi
print_status "UV found: $(uv --version)"

# Check if Node.js is installed (for frontend)
if ! command -v node &> /dev/null; then
    print_warning "Node.js not found - frontend setup will be skipped"
    SETUP_FRONTEND=false
else
    print_status "Node.js found: $(node --version)"
    SETUP_FRONTEND=true
fi

echo ""
echo "================================================"
echo "Setting up Backend (Python)"
echo "================================================"
echo ""

cd "$PROJECT_ROOT/backend"

# Check Python version
print_status "Checking Python version..."
PYTHON_VERSION=$(uv run python --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    print_error "Python $REQUIRED_VERSION or higher required, found $PYTHON_VERSION"
    echo ""
    echo "Install Python 3.11 with:"
    echo "  uv python install 3.11"
    exit 1
fi
print_status "Python version OK: $PYTHON_VERSION"

# Sync dependencies
echo ""
print_status "Syncing Python dependencies..."
uv sync --dev
print_status "Dependencies installed"

# Setup environment file
echo ""
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_status ".env file created from template"
        print_warning "Please add your ANTHROPIC_API_KEY to backend/.env"
    else
        print_warning ".env.example not found"
        echo "Creating basic .env file..."
        cat > .env << EOF
# Anthropic API Configuration
ANTHROPIC_API_KEY=your_key_here

# Database Configuration
DATABASE_URL=sqlite:///./starhub_comms.db

# FAL AI Configuration (for creative generation)
FAL_KEY=your_fal_key_here

# Environment
ENVIRONMENT=development
EOF
        print_status ".env file created"
        print_warning "Please add your API keys to backend/.env"
    fi
else
    print_status ".env file already exists"
fi

# Initialize database
echo ""
print_status "Initializing database..."
if [ -f "alembic.ini" ]; then
    uv run alembic upgrade head
    print_status "Database migrations applied"
else
    print_warning "Alembic not configured - skipping migrations"
fi

# Setup frontend
if [ "$SETUP_FRONTEND" = true ]; then
    echo ""
    echo "================================================"
    echo "Setting up Frontend (Node.js)"
    echo "================================================"
    echo ""

    cd "$PROJECT_ROOT/frontend"

    if [ -f "package.json" ]; then
        print_status "Installing Node.js dependencies..."
        npm install
        print_status "Frontend dependencies installed"
    else
        print_warning "No package.json found in frontend/"
    fi
fi

# Final instructions
echo ""
echo "================================================"
echo "Setup Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Configure API keys in backend/.env:"
echo "   - ANTHROPIC_API_KEY (required for AI generation)"
echo "   - FAL_KEY (required for creative image generation)"
echo ""
echo "2. Start the backend:"
echo "   ./start-backend.sh"
echo "   or"
echo "   cd backend && uv run uvicorn main:app --reload"
echo ""
if [ "$SETUP_FRONTEND" = true ]; then
    echo "3. Start the frontend (in another terminal):"
    echo "   ./start-frontend.sh"
    echo ""
fi
echo "4. Run tests:"
echo "   cd backend && uv run pytest"
echo ""
echo "5. Access the application:"
echo "   - Backend API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
if [ "$SETUP_FRONTEND" = true ]; then
    echo "   - Frontend: http://localhost:3000"
fi
echo ""
print_status "Happy coding!"
echo ""
