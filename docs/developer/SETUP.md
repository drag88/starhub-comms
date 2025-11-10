# Setup Guide

Complete installation and setup instructions for the StarHub Customer Communications Generator.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Backend Setup](#backend-setup)
3. [Frontend Setup](#frontend-setup)
4. [Environment Configuration](#environment-configuration)
5. [Database Initialization](#database-initialization)
6. [Running the Application](#running-the-application)
7. [Running Tests](#running-tests)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software

| Software | Minimum Version | Recommended | Purpose |
|----------|----------------|-------------|---------|
| Python | 3.13+ | 3.13 | Backend runtime |
| Node.js | 18.x | 20.x | Frontend runtime |
| npm | 9.x | 10.x | Frontend package manager |
| Git | 2.x | Latest | Version control |

### Optional Tools

| Tool | Purpose |
|------|---------|
| UV | Modern Python package manager (highly recommended) |
| SQLite Browser | Database inspection |
| Postman/Insomnia | API testing |
| VS Code | Recommended IDE |

### System Requirements

- **Operating System**: macOS, Linux, or Windows WSL2
- **RAM**: Minimum 4GB, recommended 8GB+
- **Disk Space**: 500MB for dependencies
- **Network**: Internet connection for Claude API and package downloads

## Backend Setup

### Option 1: Using UV (Recommended)

UV is a modern, fast Python package manager that's 10-100x faster than pip.

#### 1. Install UV

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation
uv --version
```

#### 2. Navigate to Backend Directory

```bash
cd backend
```

#### 3. Create Virtual Environment

```bash
# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# OR
.venv\Scripts\activate  # Windows
```

#### 4. Install Dependencies

```bash
# Production dependencies
uv pip install -e .

# With development dependencies (testing, linting)
uv pip install -e ".[dev]"
```

### Option 2: Using pip (Traditional)

If you prefer traditional Python tools:

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Backend Dependencies

**Production Dependencies:**
- FastAPI >=0.109.0 - Web framework
- Uvicorn >=0.27.0 - ASGI server
- SQLAlchemy >=2.0.25 - ORM
- Anthropic >=0.8.1 - Claude API client
- Pydantic >=2.5.3 - Data validation
- PyYAML >=6.0.1 - Configuration parsing
- Python-dotenv >=1.0.0 - Environment variables

**Development Dependencies (Optional):**
- Pytest >=7.4.4 - Testing framework
- HTTPX >=0.26.0 - Test HTTP client
- Black >=23.12.0 - Code formatter
- Ruff >=0.1.9 - Linter
- MyPy >=1.8.0 - Type checker

### Verify Backend Installation

```bash
# Check Python version
python --version  # Should be 3.13+

# Check installed packages
uv pip list  # or: pip list

# Test import
python -c "import fastapi, anthropic, sqlalchemy; print('✅ All imports successful')"
```

## Frontend Setup

### 1. Navigate to Frontend Directory

```bash
cd frontend
```

### 2. Install Dependencies

```bash
# Install all npm packages
npm install

# This installs:
# - React 19
# - TypeScript
# - Vite
# - Tailwind CSS
# - React Hook Form
# - Axios
# - And all dev dependencies
```

### Frontend Dependencies

**Production Dependencies:**
- react: ^19.0.0 - UI framework
- react-dom: ^19.0.0 - React DOM rendering
- axios: ^1.6.5 - HTTP client
- react-hook-form: ^7.49.3 - Form state management

**Development Dependencies:**
- typescript: ^5.3.3 - Type checking
- vite: ^5.0.11 - Build tool
- tailwindcss: ^3.4.1 - CSS framework
- @types/react: ^19.0.0 - React type definitions

### Verify Frontend Installation

```bash
# Check Node.js version
node --version  # Should be 18+

# Check npm version
npm --version  # Should be 9+

# Verify package installation
npm list --depth=0
```

## Environment Configuration

### Backend Environment Variables

#### 1. Create Environment File

```bash
# In backend directory
cp .env.example .env
```

#### 2. Edit .env File

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-your-api-key-here

# Optional (defaults shown)
DATABASE_URL=sqlite:///./starhub_comms.db
PORT=8000
ENVIRONMENT=development
ALLOWED_ORIGINS=*
```

#### 3. Obtain Anthropic API Key

1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Sign up or log in
3. Navigate to API Keys
4. Create new API key
5. Copy key to `.env` file

**Security Note**: Never commit `.env` file to version control. It's already in `.gitignore`.

### Frontend Environment Variables

#### 1. Create Environment File

```bash
# In frontend directory
cp .env.example .env
# OR create manually
```

#### 2. Configure API URL

```bash
# frontend/.env
VITE_API_URL=http://localhost:8000
```

**Note**: For production, change this to your production backend URL.

## Database Initialization

The database is automatically initialized when the backend starts for the first time.

### Automatic Initialization

```bash
# Database is created automatically on first run
cd backend
uv run uvicorn main:app --reload
```

This creates:
- `backend/starhub_comms.db` (SQLite database file)
- All 4 tables: campaigns, generated_communications, error_logs, promotion_uploads
- Indexes and foreign key constraints

### Manual Database Initialization

If you need to manually initialize or reset the database:

```bash
cd backend

# Using UV
uv run python -c "from database import init_db; init_db()"

# Or with activated venv
python -c "from database import init_db; init_db()"
```

### Reset Database

```bash
cd backend

# Using UV
uv run python -c "from database import reset_db; reset_db()"

# This drops all tables and recreates them
# WARNING: All data will be lost!
```

### Inspect Database

Using SQLite command-line:

```bash
sqlite3 backend/starhub_comms.db

# SQLite commands:
.tables              # List all tables
.schema campaigns    # Show table schema
SELECT * FROM campaigns;  # Query data
.quit                # Exit
```

Using SQLite Browser (GUI):

1. Download [DB Browser for SQLite](https://sqlitebrowser.org/)
2. Open `backend/starhub_comms.db`
3. Browse tables, data, and schema

## Running the Application

### Quick Start (All Services)

Use the provided startup script:

```bash
# From project root
./start-all.sh
```

This starts:
- Backend server at http://localhost:8000
- Frontend dev server at http://localhost:5173

### Start Backend Only

#### Option 1: Using Startup Script

```bash
./start-backend.sh
```

#### Option 2: Manual Start with UV

```bash
cd backend
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Option 3: Manual Start with Activated Venv

```bash
cd backend
source .venv/bin/activate  # or venv/bin/activate

# Option A: Using main.py
python main.py

# Option B: Using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Start Frontend Only

#### Option 1: Using Startup Script

```bash
./start-frontend.sh
```

#### Option 2: Manual Start

```bash
cd frontend
npm run dev
```

### Access Points

Once running:

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:5173 | Main application UI |
| Backend API | http://localhost:8000 | API base URL |
| Swagger Docs | http://localhost:8000/docs | Interactive API documentation |
| ReDoc | http://localhost:8000/redoc | Alternative API documentation |
| Health Check | http://localhost:8000/api/v1/health | Service health status |

### Verify Services Are Running

```bash
# Check backend health
curl http://localhost:8000/api/v1/health

# Expected response:
# {
#   "status": "healthy",
#   "database": "connected",
#   "timestamp": "2025-11-09T..."
# }

# Check frontend
curl http://localhost:5173
# Should return HTML page

# Check API documentation
open http://localhost:8000/docs  # macOS
# OR
xdg-open http://localhost:8000/docs  # Linux
# OR visit in browser
```

## Running Tests

### Backend Tests

All backend tests are organized in `tests/backend/`:

```
tests/backend/
├── unit/           # Unit tests for services
├── integration/    # API endpoint tests
└── performance/    # Performance benchmarks
```

#### Run All Backend Tests

```bash
cd backend
uv run pytest ../tests/backend/ -v
```

#### Run Specific Test Categories

```bash
# Unit tests only
uv run pytest ../tests/backend/unit/ -v

# Integration tests only
uv run pytest ../tests/backend/integration/ -v

# Performance tests
uv run python ../tests/backend/performance/test_performance.py
```

#### Run Specific Test File

```bash
# Test config loader
uv run pytest ../tests/backend/unit/test_config_loader.py -v

# Test API campaigns
uv run pytest ../tests/backend/integration/test_api_campaigns.py -v
```

#### Test Options

```bash
# Verbose output
uv run pytest ../tests/backend/ -v

# Show print statements
uv run pytest ../tests/backend/ -s

# Run specific test
uv run pytest ../tests/backend/unit/test_config_loader.py::test_get_cohorts -v

# Stop on first failure
uv run pytest ../tests/backend/ -x

# Run last failed tests
uv run pytest ../tests/backend/ --lf
```

### Frontend Tests

Frontend automated tests are planned for future implementation.

Currently available:
- Manual E2E testing (see `tests/e2e/test_scenarios.md`)

### End-to-End Tests

E2E tests are manual and documented in `tests/e2e/test_scenarios.md`.

To execute E2E tests:

1. Start both backend and frontend:
   ```bash
   ./start-all.sh
   ```

2. Follow test scenarios in `tests/e2e/test_scenarios.md`

3. Document results in the test scenario file

## Troubleshooting

### Common Issues

#### 1. Backend Won't Start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
```bash
cd backend
uv pip install -e ".[dev]"
# Ensure virtual environment is activated
```

**Error**: `anthropic.APIConnectionError`

**Solution**:
```bash
# Check .env file exists and has valid API key
cat backend/.env | grep ANTHROPIC_API_KEY

# Verify API key is valid at https://console.anthropic.com/
```

**Error**: `sqlite3.OperationalError: unable to open database file`

**Solution**:
```bash
# Ensure backend directory is writable
ls -la backend/

# Manually create database
cd backend
uv run python -c "from database import init_db; init_db()"
```

#### 2. Frontend Won't Start

**Error**: `Error: Cannot find module 'react'`

**Solution**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Error**: `EADDRINUSE: address already in use :::5173`

**Solution**:
```bash
# Kill process using port 5173
lsof -ti:5173 | xargs kill -9

# Or use different port
npm run dev -- --port 5174
```

#### 3. Frontend Can't Connect to Backend

**Error**: `Network Error` or `CORS Error`

**Solution**:
```bash
# Verify backend is running
curl http://localhost:8000/api/v1/health

# Check frontend .env
cat frontend/.env
# Should have: VITE_API_URL=http://localhost:8000

# Check backend CORS settings in backend/.env
# Should have: ALLOWED_ORIGINS=*
```

#### 4. Tests Failing

**Error**: `ModuleNotFoundError` in tests

**Solution**:
```bash
# Install test dependencies
cd backend
uv pip install -e ".[dev]"

# Verify pytest is installed
uv run pytest --version
```

**Error**: `FAILED tests/backend/unit/test_config_loader.py`

**Solution**:
```bash
# Verify YAML config files exist
ls -la backend/app/config/

# Should show:
# - cohorts.yaml
# - objectives.yaml
# - products.yaml
```

#### 5. Database Issues

**Error**: `sqlalchemy.exc.OperationalError: no such table`

**Solution**:
```bash
# Reinitialize database
cd backend
uv run python -c "from database import init_db; init_db()"
```

**Error**: Database locked

**Solution**:
```bash
# Stop all backend processes
pkill -f uvicorn

# Delete database and reinitialize
rm backend/starhub_comms.db
cd backend
uv run python -c "from database import init_db; init_db()"
```

### Environment Issues

#### PATH Issues with UV

**Issue**: `uv: command not found`

**Solution**:
```bash
# Add UV to PATH (macOS/Linux)
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Verify
uv --version
```

#### Virtual Environment Not Activating

**Solution**:
```bash
# macOS/Linux
source backend/.venv/bin/activate

# Verify activation
which python  # Should point to .venv/bin/python

# If still issues, recreate venv
cd backend
rm -rf .venv
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

### Performance Issues

#### Slow Startup

**Possible Causes**:
- First-time database initialization
- YAML config file loading
- Package imports

**Normal**: Backend should start in 2-5 seconds

**Check**:
```bash
time uv run uvicorn main:app --reload
```

#### Slow Generation

**Possible Causes**:
- Claude API latency (5-10 seconds normal)
- Network issues
- API key rate limiting

**Check**:
```bash
# Test API directly
curl -X POST http://localhost:8000/api/v1/campaigns/1/generate
```

### Getting Help

If you encounter issues not covered here:

1. **Check Logs**:
   ```bash
   # Backend logs (console output)
   tail -f backend/app.log  # if logging to file

   # Frontend logs (browser console)
   # Open browser DevTools → Console tab
   ```

2. **Check API Documentation**:
   - Visit http://localhost:8000/docs
   - Test endpoints interactively

3. **Verify Configuration**:
   ```bash
   # Backend
   cat backend/.env

   # Frontend
   cat frontend/.env

   # Config files
   ls -la backend/app/config/
   ```

4. **Clean Reinstall**:
   ```bash
   # Backend
   cd backend
   rm -rf .venv
   uv venv
   source .venv/bin/activate
   uv pip install -e ".[dev]"

   # Frontend
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

## Development Workflow

### Recommended IDE Setup

**VS Code Extensions**:
- Python (Microsoft)
- Pylance
- Python Test Explorer
- ESLint
- Tailwind CSS IntelliSense
- REST Client

**VS Code Settings** (`.vscode/settings.json`):
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/backend/.venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

### Code Quality Tools

#### Backend

```bash
cd backend

# Format code
uv run black .

# Lint code
uv run ruff check .

# Type check
uv run mypy .

# All quality checks
uv run black . && uv run ruff check . && uv run mypy .
```

#### Frontend

```bash
cd frontend

# Lint
npm run lint

# Type check
npm run type-check

# Build (verifies no errors)
npm run build
```

### Hot Reload

Both backend and frontend support hot reload during development:

**Backend**:
- Automatic reload on file changes with `--reload` flag
- Works with Python files in `app/` directory

**Frontend**:
- Instant HMR (Hot Module Replacement) with Vite
- Updates without full page reload

## Production Considerations

For production deployment (future phases):

1. **Backend**:
   - Use production ASGI server (Gunicorn + Uvicorn workers)
   - Migrate to PostgreSQL
   - Configure proper CORS origins
   - Set up proper logging
   - Use environment-specific configs

2. **Frontend**:
   - Build for production: `npm run build`
   - Serve static files from CDN
   - Configure production API URL
   - Enable production optimizations

3. **Security**:
   - Use HTTPS/TLS
   - Implement authentication
   - Add rate limiting
   - Secure API keys with secrets manager
   - Set restrictive CORS policy

See [DEPLOYMENT.md](../operations/DEPLOYMENT.md) for detailed production deployment guide.

## Next Steps

After successful setup:

1. **Explore the Application**:
   - Open http://localhost:5173
   - Create a test campaign
   - Generate communications
   - Try different channels and cohorts

2. **Review Documentation**:
   - [User Guide](../user/USER_GUIDE.md) - How to use the application
   - [API Reference](API_REFERENCE.md) - API documentation
   - [Architecture](ARCHITECTURE.md) - System architecture

3. **Run Tests**:
   - Execute all backend tests
   - Try E2E test scenarios
   - Review test coverage

4. **Development**:
   - Make code changes
   - Run tests
   - Use API documentation
   - Follow code quality guidelines

## Appendix: Quick Reference

### Backend Commands

```bash
# Start server
uv run uvicorn main:app --reload

# Run tests
uv run pytest ../tests/backend/ -v

# Reset database
uv run python -c "from database import reset_db; reset_db()"

# Format code
uv run black .
```

### Frontend Commands

```bash
# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint
npm run lint
```

### Database Commands

```bash
# Initialize
python -c "from database import init_db; init_db()"

# Reset
python -c "from database import reset_db; reset_db()"

# Inspect
sqlite3 backend/starhub_comms.db
```

### Health Checks

```bash
# Backend
curl http://localhost:8000/api/v1/health

# Frontend
curl http://localhost:5173

# API docs
open http://localhost:8000/docs
```
