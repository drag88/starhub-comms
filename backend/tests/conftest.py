"""
Pytest configuration and shared fixtures for all tests.
"""

import sys
from collections.abc import Generator
from pathlib import Path

# Add backend directory to Python path - must be before imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.models.campaign import Campaign
from app.models.communication import GeneratedCommunication  # noqa: F401
from app.models.creative import GeneratedCreative
from app.models.error_log import ErrorLog  # noqa: F401
from app.models.promotion import PromotionUpload  # noqa: F401
from database import Base, get_db
from main import app

# Test database setup
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def test_db() -> Generator[Session, None, None]:
    """
    Create test database and session for each test.

    Yields:
        Database session for testing

    Note:
        Creates fresh in-memory database for each test to ensure isolation
    """
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create session
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db: Session) -> Generator[TestClient, None, None]:
    """
    Create FastAPI test client with test database.

    Args:
        test_db: Test database session

    Yields:
        FastAPI test client

    Note:
        Overrides the get_db dependency to use test database
    """

    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_campaign(test_db: Session) -> Campaign:
    """
    Create sample campaign for testing.

    Args:
        test_db: Test database session

    Returns:
        Campaign instance saved to database

    Note:
        Creates campaign with realistic test data
    """
    import json

    campaign = Campaign(
        campaign_name="5G Launch Special",
        channel="email",
        objective="Acquisition - Drive 5G plan sign-ups",
        product_lines=json.dumps(["mobile"]),
        cohorts=json.dumps(["young_professionals", "tech_enthusiasts"]),
    )

    test_db.add(campaign)
    test_db.commit()
    test_db.refresh(campaign)

    return campaign


@pytest.fixture
def sample_creative(test_db: Session, sample_campaign: Campaign) -> GeneratedCreative:
    """
    Create sample generated creative for testing.

    Args:
        test_db: Test database session
        sample_campaign: Sample campaign fixture

    Returns:
        GeneratedCreative instance saved to database
    """
    import json

    creative = GeneratedCreative(
        campaign_id=sample_campaign.campaign_id,
        variant_number=1,
        channel_type="email_header",
        image_filename="test_email_header_1_20250110120000.jpg",
        image_url="/static/creatives/test_email_header_1_20250110120000.jpg",
        prompt_used="Test prompt for email header creative",
        generation_params=json.dumps({"width": 600, "height": 200, "content_type": "image/jpeg"}),
        model_used="seedream-4",
        recommendation_score=85,
        score_reasoning="Test scoring reasoning",
        is_selected=False,
    )

    test_db.add(creative)
    test_db.commit()
    test_db.refresh(creative)

    return creative


@pytest.fixture
def mock_fal_client():
    """
    Mock fal_client for testing creative generation without API calls.

    Yields:
        Mocked fal_client with subscribe method

    Note:
        Returns realistic test data matching fal.ai API response structure
    """
    mock_result = {
        "images": [
            {
                "url": "https://example.com/test_image.jpg",
                "width": 600,
                "height": 200,
                "content_type": "image/jpeg",
            }
        ]
    }

    with patch("app.services.creative_generator.fal_client") as mock_client:
        mock_client.subscribe = Mock(return_value=mock_result)
        yield mock_client


@pytest.fixture
def mock_image_download():
    """
    Mock httpx image download for testing without network calls.

    Yields:
        Patched httpx.AsyncClient context

    Note:
        Returns fake JPEG image data (1x1 pixel)
    """
    # Minimal valid JPEG data (1x1 red pixel)
    fake_jpeg_data = (
        b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
        b"\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n"
        b"\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d"
        b"\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342"
        b"\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x14"
        b"\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x03\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\xff\xda\x00\x08\x01\x01\x00\x00?\x00T\xdf"
        b"\xff\xd9"
    )

    mock_response = Mock()
    mock_response.content = fake_jpeg_data
    mock_response.raise_for_status = Mock()

    async def mock_get(url):
        return mock_response

    with patch("app.services.creative_generator.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = mock_get
        yield mock_client


@pytest.fixture
def mock_static_dir(tmp_path: Path):
    """
    Create temporary static directory for testing file operations.

    Args:
        tmp_path: pytest temporary directory fixture

    Returns:
        Path to temporary creatives directory

    Note:
        Automatically cleaned up after test by pytest
    """
    creatives_dir = tmp_path / "static" / "creatives"
    creatives_dir.mkdir(parents=True, exist_ok=True)
    return str(creatives_dir)


@pytest.fixture
def mock_env_fal_key(monkeypatch):
    """
    Mock FAL_KEY environment variable for testing.

    Args:
        monkeypatch: pytest monkeypatch fixture

    Note:
        Sets FAL_KEY to test value for duration of test
    """
    monkeypatch.setenv("FAL_KEY", "test_fal_key_12345")
