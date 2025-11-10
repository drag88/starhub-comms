"""
Pytest configuration and fixtures for backend tests.

This conftest.py sets up the Python path so tests can import from the backend
directory regardless of where they're run from.
"""

import sys
from pathlib import Path

# Add backend directory to Python path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# This allows tests to import like:
# from app.services.config_loader import get_cohorts
# from app.models.campaign import Campaign
# etc.
