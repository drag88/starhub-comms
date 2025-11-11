"""Unit tests for creative generation service."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.creative_generator import (
    CreativeGenerator,
    save_image,
    score_creative,
    CreativeGenerationService,
)


@pytest.fixture
def mock_fal_client():
    """Mock fal_client for testing."""
    with patch("app.services.creative_generator.fal_client") as mock:
        mock.subscribe.return_value = {
            "images": [
                {
                    "url": "https://example.com/image.jpg",
                    "width": 600,
                    "height": 400,
                    "content_type": "image/jpeg",
                }
            ]
        }
        yield mock


def test_creative_generator_init():
    """Test CreativeGenerator initialization."""
    with patch.dict("os.environ", {"FAL_KEY": "test_key"}):
        generator = CreativeGenerator()
        assert generator.api_key == "test_key"


def test_build_prompt_email_header():
    """Test prompt building for email header."""
    with patch.dict("os.environ", {"FAL_KEY": "test_key"}):
        generator = CreativeGenerator()
        prompt = generator.build_prompt(
            channel="email_header",
            visual_concept="happy family watching TV",
            campaign_data={},
            headline="Stream Everything",
            offer_details="$99/mth",
        )

        assert "email header" in prompt.lower()
        assert "happy family watching TV" in prompt
        assert "Stream Everything" in prompt
        assert "$99/mth" in prompt
        assert "#00D964" in prompt  # Brand green


def test_generate_image_success(mock_fal_client):
    """Test successful image generation."""
    with patch.dict("os.environ", {"FAL_KEY": "test_key"}):
        generator = CreativeGenerator()
        result = generator.generate_image("test prompt", "email_header")

        assert "url" in result
        assert "metadata" in result
        assert result["url"] == "https://example.com/image.jpg"


@pytest.mark.asyncio
async def test_save_image():
    """Test image saving to filesystem."""
    with patch("httpx.AsyncClient") as mock_client, \
         patch("aiofiles.open") as mock_file, \
         patch("PIL.Image.open") as mock_image, \
         patch("os.makedirs"):

        # Mock HTTP response
        mock_response = Mock()
        mock_response.content = b"fake_image_data"
        mock_response.raise_for_status = Mock()

        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=mock_response
        )

        # Mock image validation
        mock_img = Mock()
        mock_img.width = 600
        mock_img.height = 400
        mock_image.return_value = mock_img

        # Mock aiofiles.open properly
        mock_async_file = AsyncMock()
        mock_async_file.__aenter__.return_value.write = AsyncMock()
        mock_file.return_value = mock_async_file

        result = await save_image(
            image_url="https://example.com/test.jpg",
            campaign_id=1,
            channel="email_header",
            variant=1,
        )

        assert "filename" in result
        assert "url" in result
        assert result["url"].startswith("/static/creatives/")


def test_score_creative():
    """Test creative scoring algorithm."""
    result = score_creative(
        image_path="test.jpg",
        channel="email_header",
        prompt_used="test prompt",
    )

    assert "score" in result
    assert "reasoning" in result
    assert "score_breakdown" in result
    assert 0 <= result["score"] <= 100
    assert result["score"] == 92  # 35 + 30 + 18 + 9


@pytest.mark.asyncio
async def test_generate_and_score_success(mock_fal_client):
    """Test complete generation workflow."""
    with patch.dict("os.environ", {"FAL_KEY": "test_key"}), \
         patch("app.services.creative_generator.save_image", new=AsyncMock()) as mock_save, \
         patch("app.services.creative_generator.score_creative") as mock_score:

        # Setup mocks
        mock_save.return_value = {"filename": "test.jpg", "url": "/static/creatives/test.jpg"}
        mock_score.return_value = {
            "score": 92,
            "reasoning": "Test reasoning",
            "score_breakdown": {},
        }

        # Mock database session
        mock_db = Mock()
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()

        service = CreativeGenerationService()
        results = await service.generate_and_score(
            campaign_id=1,
            channel="email_header",
            visual_concept="happy family",
            campaign_data={},
            db=mock_db,
        )

        assert len(results) == 3
        assert all("rank" in r for r in results)
        assert results[0]["rank"] == 1  # Highest score first
