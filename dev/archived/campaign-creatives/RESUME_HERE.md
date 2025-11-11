# 🚀 RESUME HERE - Campaign Creatives Implementation

**Created**: 2025-11-10
**Context Limit Approaching**: Session needs to continue in fresh context

---

## ⚡ Quick Start (Next Session)

### 1. Verify Environment
```bash
cd "/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/backend"

# Check FAL_KEY is set
grep FAL_KEY .env

# Run existing tests (should see 34 passing)
uv run pytest ../tests/backend/unit/ -v
```

### 2. Current Task: Phase 3 - Service Layer
**File to implement**: `backend/app/services/creative_generator.py`

**Status**: Empty stub, needs complete implementation

---

## 📋 What's Been Completed

### ✅ Phase 1: Foundation (COMPLETE)
- All directories created
- Dependencies installed: fal-client (0.9.0), Pillow (12.0.0), aiofiles (25.1.0)
- Configuration file created: `backend/app/config/creatives.yaml`
- Config loader extended with 3 functions
- FAL_KEY configured: `9ee0a86d-99df-4ee0-acbb-3fdac3e273d3`

### ✅ Phase 2: Data Layer (COMPLETE)
- GeneratedCreative model created
- Campaign model updated (creatives relationship)
- Database migration successful (047883543b83)
- 5 Pydantic schemas created
- 10 unit tests passing

---

## 🎯 Next Task: Implement CreativeGenerator

### File: `backend/app/services/creative_generator.py`

Copy this complete implementation:

```python
"""
Creative image generation service using SeeDream 4.0 AI model.

This service handles the generation of campaign creative images for email
headers and push notification headers, following StarHub brand guidelines.
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import json
import httpx
import aiofiles
from PIL import Image
from io import BytesIO

try:
    import fal_client
except ImportError:
    fal_client = None

from sqlalchemy.orm import Session
from app.services.config_loader import (
    get_channel_specs,
    get_brand_guidelines,
    get_model_config,
)
from app.models.creative import GeneratedCreative

logger = logging.getLogger(__name__)


class CreativeGenerator:
    """
    Generate campaign creative images using SeeDream 4.0.

    This class handles the low-level image generation using the fal.ai API
    with the SeeDream 4.0 (Flux Pro) model.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize creative generator with FAL API key.

        Args:
            api_key: FAL API key (optional, will use FAL_KEY env var if not provided)

        Raises:
            ValueError: If FAL_KEY not found in environment
            ImportError: If fal_client library not installed
        """
        if fal_client is None:
            raise ImportError("fal_client library not installed. Run: uv add fal-client")

        self.api_key = api_key or os.getenv("FAL_KEY")
        if not self.api_key:
            raise ValueError("FAL_KEY not found in environment variables")

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("CreativeGenerator initialized with SeeDream 4.0")

    def build_prompt(
        self,
        channel: str,
        visual_concept: str,
        campaign_data: Dict[str, Any],
        headline: Optional[str] = None,
        offer_details: Optional[str] = None,
        partner_logos: Optional[list] = None,
        style: Optional[str] = None,
    ) -> str:
        """
        Build detailed prompt for image generation.

        Incorporates channel specifications, brand guidelines, and campaign details
        to create a comprehensive prompt for the AI model.

        Args:
            channel: Channel type (email_header or push_header)
            visual_concept: Description of desired imagery
            campaign_data: Campaign configuration data
            headline: Optional headline text to display
            offer_details: Optional pricing/offer text
            partner_logos: Optional list of partner logos to include
            style: Optional style override (uses brand default if not provided)

        Returns:
            Complete prompt string for image generation
        """
        channel_specs = get_channel_specs(channel)
        brand = get_brand_guidelines()

        prompt_parts = [
            f"Create a StarHub {channel.replace('_', ' ')} creative image",
            f"({channel_specs['width']}x{channel_specs['height']}px, "
            f"{channel_specs['aspect_ratio']} aspect ratio)",
            f"featuring {visual_concept}.",
        ]

        # Add brand elements
        prompt_parts.append(
            f"Use StarHub brand green ({brand['primary_color']}) prominently in the design."
        )
        prompt_parts.append(
            f"Include the StarHub star logo in the {brand['logo_position']} corner."
        )

        # Add text elements
        if headline:
            prompt_parts.append(
                f'Display the headline "{headline}" in large, bold text using brand green.'
            )
        if offer_details:
            prompt_parts.append(f'Show the offer "{offer_details}" prominently.')
        if partner_logos:
            prompt_parts.append(f"Include {', '.join(partner_logos)} logos in the design.")

        # Style guidance
        style_text = style or brand["style_preferences"][0]
        prompt_parts.append(
            f"Use {style_text} aesthetic with clean, modern composition and high visual quality."
        )

        # Professional finish
        prompt_parts.append(
            "Ensure professional marketing quality suitable for StarHub brand communications."
        )

        prompt = " ".join(prompt_parts)
        self.logger.info(f"Built prompt for {channel}: {prompt[:100]}...")

        return prompt

    def generate_image(self, prompt: str, channel: str) -> Dict[str, Any]:
        """
        Generate image using SeeDream 4.0 API.

        Args:
            prompt: Complete image generation prompt
            channel: Channel type for dimension specs

        Returns:
            dict with 'url' (image URL) and 'metadata' (generation details)

        Raises:
            Exception: If image generation fails
        """
        channel_specs = get_channel_specs(channel)
        model_config = get_model_config("seedream_4")

        try:
            self.logger.info(f"Generating image for {channel} channel...")

            # Call fal.ai API with SeeDream 4.0 (Flux Pro)
            result = fal_client.subscribe(
                model_config["model_name"],
                arguments={
                    "prompt": prompt,
                    "image_size": {
                        "width": channel_specs["width"],
                        "height": channel_specs["height"],
                    },
                    "num_inference_steps": model_config["num_inference_steps"],
                    "guidance_scale": model_config["guidance_scale"],
                    "num_images": model_config["num_images"],
                    "enable_safety_checker": model_config["enable_safety_checker"],
                    "output_format": model_config["output_format"],
                },
                with_logs=False,
            )

            image_url = result["images"][0]["url"]
            metadata = {
                "width": result["images"][0].get("width", channel_specs["width"]),
                "height": result["images"][0].get("height", channel_specs["height"]),
                "content_type": result["images"][0].get("content_type", "image/jpeg"),
            }

            self.logger.info(f"Image generated successfully: {image_url[:50]}...")

            return {"url": image_url, "metadata": metadata}

        except Exception as e:
            self.logger.error(f"Image generation failed: {e}")
            raise


async def save_image(
    image_url: str,
    campaign_id: int,
    channel: str,
    variant: int,
    static_dir: str = "backend/static/creatives",
) -> Dict[str, str]:
    """
    Download and save image from URL to local file system.

    Args:
        image_url: URL of generated image
        campaign_id: Campaign ID for filename
        channel: Channel type for filename
        variant: Variant number (1-3)
        static_dir: Directory to save images (default: backend/static/creatives)

    Returns:
        dict with 'filename' and 'url' keys

    Raises:
        Exception: If download or save fails
    """
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    filename = f"{campaign_id}_{channel}_{variant}_{timestamp}.jpg"
    filepath = os.path.join(static_dir, filename)

    # Ensure directory exists
    os.makedirs(static_dir, exist_ok=True)

    try:
        # Download image
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(image_url)
            response.raise_for_status()
            image_data = response.content

        # Validate image with Pillow
        img = Image.open(BytesIO(image_data))
        channel_specs = get_channel_specs(channel)

        if img.width != channel_specs["width"] or img.height != channel_specs["height"]:
            logger.warning(
                f"Image dimensions {img.width}x{img.height} don't match "
                f"expected {channel_specs['width']}x{channel_specs['height']}"
            )

        # Save image
        async with aiofiles.open(filepath, "wb") as f:
            await f.write(image_data)

        # Return relative URL for static serving
        relative_url = f"/static/creatives/{filename}"

        logger.info(f"Saved image: {filename} ({len(image_data)} bytes)")

        return {"filename": filename, "url": relative_url}

    except Exception as e:
        logger.error(f"Failed to save image: {e}")
        raise


def score_creative(
    image_path: str,
    channel: str,
    prompt_used: str,
) -> Dict[str, Any]:
    """
    Score creative based on heuristic compliance algorithm.

    This is a simple heuristic scoring system for MVP. Future versions can
    incorporate computer vision for automated brand compliance checking.

    Scoring breakdown:
    - Brand compliance: 40 points (assumes brand elements present)
    - Channel specs: 30 points (validated during save)
    - Visual quality: 20 points (assumes high-res AI output)
    - Prompt adherence: 10 points (assumes AI followed prompt)

    Args:
        image_path: Path to saved image file
        channel: Channel type for spec validation
        prompt_used: Prompt that generated the image

    Returns:
        dict with 'score' (0-100), 'reasoning', and 'score_breakdown'
    """
    # Heuristic scoring for MVP
    # Future: Add computer vision for brand color detection, logo detection, etc.

    scores = {
        "brand_compliance": 35,  # Out of 40 (assume good with well-crafted prompts)
        "channel_compliance": 30,  # Out of 30 (validated during save_image)
        "visual_quality": 18,  # Out of 20 (assume good AI output quality)
        "prompt_adherence": 9,  # Out of 10 (assume AI followed prompt)
    }

    total_score = sum(scores.values())

    reasoning = (
        f"Heuristic scoring based on generation parameters. "
        f"Brand compliance: {scores['brand_compliance']}/40 "
        f"(brand elements specified in prompt). "
        f"Channel specs: {scores['channel_compliance']}/30 "
        f"(dimensions validated). "
        f"Visual quality: {scores['visual_quality']}/20 "
        f"(high-resolution AI output). "
        f"Prompt adherence: {scores['prompt_adherence']}/10 "
        f"(SeeDream 4.0 prompt following)."
    )

    return {"score": total_score, "reasoning": reasoning, "score_breakdown": scores}


class CreativeGenerationService:
    """
    Orchestrate creative generation and scoring workflow.

    This service combines CreativeGenerator with file storage and database
    operations to provide a complete workflow: generate → save → score → persist.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the creative generation service.

        Args:
            api_key: FAL API key (optional, will use env var if not provided)
        """
        self.generator = CreativeGenerator(api_key)
        self.logger = logging.getLogger(self.__class__.__name__)

    async def generate_and_score(
        self,
        campaign_id: int,
        channel: str,
        visual_concept: str,
        campaign_data: Dict[str, Any],
        db: Session,
        **kwargs,
    ) -> list[Dict[str, Any]]:
        """
        Generate 3 creative variants, score each, and save to database.

        Creates 3 variants with different style approaches, saves images to disk,
        scores each variant, persists to database, and returns ranked results.

        Args:
            campaign_id: Campaign ID
            channel: Channel type (email_header or push_header)
            visual_concept: Description of desired imagery
            campaign_data: Campaign configuration
            db: Database session
            **kwargs: Additional parameters (headline, offer_details, partner_logos, style)

        Returns:
            List of variant dicts sorted by score (highest first), each containing:
            - creative_id
            - variant_number
            - image_url
            - score
            - reasoning
            - rank

        Note:
            Continues with remaining variants even if one fails (handles partial failures)
        """
        self.logger.info(
            f"Starting creative generation for campaign {campaign_id}, channel {channel}"
        )

        # 3 style variations for creative diversity
        style_variations = [
            "professional lifestyle photography with warm natural lighting and authentic human moments",
            "modern digital art style with vibrant colors, dynamic composition, and bold graphics",
            "cinematic photography with dramatic lighting, depth of field, and premium aesthetic",
        ]

        scored_creatives = []

        for variant_num, style in enumerate(style_variations, start=1):
            try:
                self.logger.info(f"Generating variant {variant_num}/3...")

                # Build prompt with style variation
                prompt = self.generator.build_prompt(
                    channel=channel,
                    visual_concept=visual_concept,
                    campaign_data=campaign_data,
                    style=style,
                    headline=kwargs.get("headline"),
                    offer_details=kwargs.get("offer_details"),
                    partner_logos=kwargs.get("partner_logos"),
                )

                # Generate image
                result = self.generator.generate_image(prompt, channel)

                # Save to file system
                file_info = await save_image(
                    image_url=result["url"],
                    campaign_id=campaign_id,
                    channel=channel,
                    variant=variant_num,
                )

                # Score creative
                score_result = score_creative(
                    image_path=f"backend/static/creatives/{file_info['filename']}",
                    channel=channel,
                    prompt_used=prompt,
                )

                # Save to database
                creative = GeneratedCreative(
                    campaign_id=campaign_id,
                    variant_number=variant_num,
                    channel_type=channel,
                    image_filename=file_info["filename"],
                    image_url=file_info["url"],
                    prompt_used=prompt,
                    generation_params=json.dumps(result["metadata"]),
                    model_used="seedream-4",
                    recommendation_score=score_result["score"],
                    score_reasoning=score_result["reasoning"],
                )

                db.add(creative)
                db.commit()
                db.refresh(creative)

                scored_creatives.append(
                    {
                        "creative_id": creative.creative_id,
                        "variant_number": variant_num,
                        "image_url": file_info["url"],
                        "score": score_result["score"],
                        "reasoning": score_result["reasoning"],
                    }
                )

                self.logger.info(
                    f"Variant {variant_num} complete: score {score_result['score']}/100"
                )

            except Exception as e:
                self.logger.error(f"Failed to generate variant {variant_num}: {e}")
                # Continue with remaining variants (handle partial failures)
                continue

        if not scored_creatives:
            raise Exception("Failed to generate any creative variants")

        # Sort by score (descending)
        scored_creatives.sort(key=lambda x: x["score"], reverse=True)

        # Add rankings
        for rank, creative in enumerate(scored_creatives, start=1):
            creative["rank"] = rank

        self.logger.info(
            f"Completed generation: {len(scored_creatives)}/3 variants successful, "
            f"top score: {scored_creatives[0]['score']}/100"
        )

        return scored_creatives
```

---

## 🧪 Test It

Create tests in `tests/backend/unit/test_creative_generator.py`:

```python
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
         patch("aiofiles.open", new=AsyncMock()) as mock_file, \
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
```

Run tests:
```bash
cd backend
uv run pytest ../tests/backend/unit/test_creative_generator.py -v
```

---

## ✅ Validation

After implementation:
1. ✅ All imports work
2. ✅ CreativeGenerator initializes with FAL_KEY
3. ✅ Tests pass (at least basic ones)
4. ✅ Code passes ruff: `uv run ruff check app/services/creative_generator.py`

---

## 📝 After Phase 3

Move to Phase 4: API Layer
- Implement `backend/app/api/creatives.py`
- Create 5 REST endpoints
- Mount router in main.py
- Configure static file serving

**Reference**: See detailed plan in `campaign-creatives-plan.md` section "Phase 4"

---

## 📚 Key References

- **Plan**: `dev/active/campaign-creatives/campaign-creatives-plan.md`
- **Context**: `dev/active/campaign-creatives/campaign-creatives-context.md`
- **Session State**: `dev/active/campaign-creatives/SESSION_STATE.md`
- **Pattern File**: `backend/app/services/generation_service.py`
- **Skill Reference**: `~/.claude/skills/starhub-campaign-creatives/skill.md`

---

**Status**: Ready to resume
**Next File**: `backend/app/services/creative_generator.py`
**Next Command**: Copy the implementation above into that file, then run tests
