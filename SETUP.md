# Setup Guide - UV Package Manager

This project uses **UV** for Python dependency management, ensuring consistent, reproducible environments across all machines.

## Prerequisites

### 1. Install UV

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Verify installation
uv --version
```

### 2. Install Python 3.11+ (if needed)

```bash
# UV can install Python for you
uv python install 3.11

# Verify Python version
uv run python --version
```

### 3. Install Node.js (for frontend)

- Download from: https://nodejs.org/ (LTS version recommended)
- Or use a version manager like `nvm`

## Quick Start

### Automated Setup (Recommended)

Run the automated setup script from the project root:

```bash
./setup.sh
```

This will:
- Install all Python dependencies via UV
- Set up the database
- Create environment files
- Install frontend dependencies (if Node.js is available)

### Manual Setup

If you prefer manual setup or need more control:

#### 1. Backend Setup

```bash
cd backend

# Sync all dependencies (production + development)
uv sync --dev

# Or for production only
uv sync
```

#### 2. Environment Configuration

```bash
cd backend

# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
# Required: ANTHROPIC_API_KEY, FAL_KEY
```

#### 3. Database Setup

```bash
cd backend

# Run migrations
uv run alembic upgrade head
```

#### 4. Frontend Setup (optional)

```bash
cd frontend

# Install Node.js dependencies
npm install
```

## Running the Application

### Backend

```bash
# From project root
./start-backend.sh

# Or manually
cd backend
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Access at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

### Frontend

```bash
# From project root
./start-frontend.sh

# Or manually
cd frontend
npm run dev
```

## Development Workflow

### Adding Dependencies

```bash
cd backend

# Add a production dependency
uv add package-name

# Add a development dependency
uv add --dev package-name

# Remove a dependency
uv remove package-name
```

**IMPORTANT**: Never edit `pyproject.toml` directly for dependencies. Always use `uv add` or `uv remove`.

### Running Tests

```bash
cd backend

# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=html

# Run specific test file
uv run pytest tests/backend/unit/test_campaign.py -v
```

### Code Quality

```bash
cd backend

# Format code
uv run ruff format .

# Lint and auto-fix
uv run ruff check . --fix

# Type checking
uv run mypy app/
```

### Database Migrations

```bash
cd backend

# Create a new migration
uv run alembic revision --autogenerate -m "Description of changes"

# Apply migrations
uv run alembic upgrade head

# Rollback one migration
uv run alembic downgrade -1
```

## UV Benefits

### Why UV?

1. **Fast**: 10-100x faster than pip
2. **Reliable**: Deterministic dependency resolution with lockfile
3. **Cross-platform**: Works identically on Mac, Linux, Windows
4. **Simple**: Single tool for virtualenvs, dependencies, and Python versions
5. **Reproducible**: `uv.lock` ensures everyone has exact same versions

### Key Files

- **`pyproject.toml`**: Declares dependencies and project metadata
- **`uv.lock`**: Pins exact versions for reproducibility (commit this!)
- **`.python-version`**: Specifies Python version for the project

### UV Commands Cheat Sheet

```bash
# Environment management
uv venv                    # Create virtual environment
uv sync                    # Install dependencies from lockfile
uv sync --dev              # Install with dev dependencies
uv sync --upgrade          # Update dependencies

# Dependency management
uv add <package>           # Add dependency
uv add --dev <package>     # Add dev dependency
uv remove <package>        # Remove dependency
uv pip list                # List installed packages

# Python version management
uv python install 3.11     # Install Python 3.11
uv python list             # List available Python versions

# Running commands
uv run <command>           # Run command in virtual environment
uv run python script.py    # Run Python script
uv run pytest              # Run tests
```

## Troubleshooting

### Issue: "uv: command not found"

**Solution**: UV not in PATH. Restart terminal or add UV to PATH manually:

```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="$HOME/.cargo/bin:$PATH"
```

### Issue: "Python version too old"

**Solution**: Install Python 3.11+:

```bash
uv python install 3.11
```

### Issue: "Module not found" errors

**Solution**: Resync dependencies:

```bash
cd backend
rm -rf .venv
uv sync --dev
```

### Issue: Dependency conflicts

**Solution**: Clear cache and resync:

```bash
uv cache clean
cd backend
uv sync --dev --refresh
```

### Issue: "Failed to build" errors

**Solution**: Ensure build tools are installed:

```bash
# macOS
xcode-select --install

# Ubuntu/Debian
sudo apt-get install build-essential python3-dev

# Windows
# Install Visual Studio Build Tools
```

## Moving to a New Machine

To set up this project on a new machine:

1. **Clone the repository**

```bash
git clone <repository-url>
cd <project-directory>
```

2. **Install UV** (if not already installed)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. **Run setup script**

```bash
./setup.sh
```

4. **Configure environment**

```bash
cd backend
# Edit .env with your API keys
```

5. **Start the application**

```bash
./start-backend.sh
```

That's it! The `uv.lock` file ensures you get the exact same dependencies as every other developer.

## CI/CD Integration

For GitHub Actions or other CI/CD:

```yaml
# .github/workflows/test.yml
- name: Install UV
  run: curl -LsSf https://astral.sh/uv/install.sh | sh

- name: Install dependencies
  run: |
    cd backend
    uv sync --dev

- name: Run tests
  run: |
    cd backend
    uv run pytest
```

## FAQ

**Q: Should I commit `uv.lock`?**
A: Yes! This ensures reproducible builds across all environments.

**Q: Should I commit `.venv`?**
A: No! This is already in `.gitignore`. Virtual environments should be created on each machine.

**Q: Can I use pip instead of UV?**
A: Not recommended. This project is configured for UV. Using pip may cause dependency conflicts.

**Q: How do I update all dependencies?**
A: Run `uv sync --upgrade` to update within the version constraints specified in `pyproject.toml`.

**Q: What if a dependency is yanked (like fal-client 0.9.0)?**
A: UV will warn you. Update the version in `pyproject.toml` or accept the warning if it's not critical.

## Additional Resources

- [UV Documentation](https://github.com/astral-sh/uv)
- [UV Guide](https://docs.astral.sh/uv/)
- [Python Packaging Guide](https://packaging.python.org/)
