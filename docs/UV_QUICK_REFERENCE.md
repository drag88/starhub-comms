# UV Quick Reference Card

## Essential Commands

### Setup & Installation
```bash
# Install UV (first time only)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Setup project (first time or new machine)
./setup.sh

# Or manual setup
cd backend
uv sync --dev
```

### Running the Application
```bash
# Backend
./start-backend.sh
# OR
cd backend && uv run uvicorn main:app --reload

# Frontend
./start-frontend.sh
# OR
cd frontend && npm run dev
```

### Development Commands

#### Testing
```bash
cd backend
uv run pytest                           # Run all tests
uv run pytest tests/backend/unit/ -v   # Run unit tests
uv run pytest --cov=app                # Run with coverage
uv run pytest -k "test_campaign"       # Run specific test
```

#### Code Quality
```bash
cd backend
uv run ruff format .                   # Format code
uv run ruff check . --fix              # Lint and auto-fix
uv run mypy app/                       # Type checking
```

#### Database
```bash
cd backend
uv run alembic revision --autogenerate -m "description"  # Create migration
uv run alembic upgrade head                              # Apply migrations
uv run alembic downgrade -1                              # Rollback one
```

### Dependency Management

#### Adding Packages
```bash
cd backend
uv add requests                        # Add production dependency
uv add --dev pytest-mock              # Add dev dependency
```

#### Removing Packages
```bash
cd backend
uv remove package-name                 # Remove dependency
```

#### Updating Dependencies
```bash
cd backend
uv sync --upgrade                      # Update all dependencies
uv add package-name@latest             # Update specific package
```

#### Listing Packages
```bash
cd backend
uv pip list                            # List installed packages
```

### Python Version Management
```bash
uv python install 3.11                 # Install Python 3.11
uv python list                         # List available versions
uv run python --version                # Check current version
```

### Running Python Scripts
```bash
cd backend
uv run python script.py                # Run any Python script
uv run python -m module                # Run as module
```

### Troubleshooting

#### Clean Install
```bash
cd backend
rm -rf .venv
uv sync --dev
```

#### Clear Cache
```bash
uv cache clean
cd backend
uv sync --dev --refresh
```

#### Check Dependencies
```bash
cd backend
uv pip check                           # Verify no conflicts
uv pip list --outdated                 # Check for updates
```

## File Structure

```
project-root/
├── .python-version          # Python version (3.11)
├── setup.sh                 # Automated setup script
├── SETUP.md                 # Detailed setup guide
├── README.md                # Project documentation
└── backend/
    ├── pyproject.toml       # Dependencies & config
    ├── uv.lock              # Locked versions (commit this!)
    ├── .venv/               # Virtual env (gitignored)
    └── app/                 # Application code
```

## Key Differences from pip/venv

| Task | Old Way (pip) | New Way (UV) |
|------|---------------|--------------|
| Create venv | `python -m venv .venv` | `uv venv` (or skip, UV handles it) |
| Activate venv | `source .venv/bin/activate` | Not needed! Use `uv run` |
| Install deps | `pip install -r requirements.txt` | `uv sync` |
| Add package | `pip install pkg && pip freeze > requirements.txt` | `uv add pkg` |
| Run script | `python script.py` | `uv run python script.py` |
| Run tests | `pytest` | `uv run pytest` |

## Best Practices

1. **Never edit pyproject.toml manually for dependencies** - Use `uv add` / `uv remove`
2. **Always commit uv.lock** - This ensures reproducible builds
3. **Use `uv run` instead of activating venv** - Simpler and more reliable
4. **Keep dependencies minimal** - Only add what you need
5. **Update regularly** - Run `uv sync --upgrade` weekly
6. **Test before committing** - Run `uv run pytest` before pushing code

## Common Workflows

### Starting Work on New Machine
```bash
git clone <repo>
cd <project>
./setup.sh
cd backend && uv sync --dev
./start-backend.sh
```

### Adding a New Feature
```bash
cd backend
uv add new-package                     # Add dependency if needed
# Write code
uv run pytest                          # Test
uv run ruff format .                   # Format
uv run ruff check . --fix              # Lint
git add . && git commit -m "feat: ..."
```

### Daily Development
```bash
# Start backend
./start-backend.sh

# In another terminal, run tests on save
cd backend
uv run pytest --watch

# Make changes, tests run automatically
```

### Before Committing
```bash
cd backend
uv run ruff format .                   # Format
uv run ruff check . --fix              # Lint
uv run pytest                          # Test
uv run mypy app/                       # Type check
```

## Help & Resources

- **UV Docs**: https://docs.astral.sh/uv/
- **Detailed Setup**: See [SETUP.md](./SETUP.md)
- **Project README**: See [README.md](./README.md)
- **UV GitHub**: https://github.com/astral-sh/uv

## Emergency Recovery

If everything breaks:
```bash
cd backend
rm -rf .venv
rm uv.lock
uv sync --dev
```

This will recreate everything from scratch using pyproject.toml.
