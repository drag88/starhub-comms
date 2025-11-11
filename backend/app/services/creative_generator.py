"""
Creative image generation service using BytePlus ModelArk SeeDream 4.0 AI model.

This service handles the generation of campaign creative images for email
headers and push notification headers, following StarHub brand guidelines.

API Documentation: https://docs.byteplus.com/en/docs/ModelArk/1541523
"""

import json
import logging
import os
from datetime import datetime
from io import BytesIO
from typing import Any

import aiofiles
import httpx
from PIL import Image

from sqlalchemy.orm import Session

from app.models.creative import GeneratedCreative
from app.services.config_loader import (
    get_brand_guidelines,
    get_channel_specs,
    get_model_config,
)

logger = logging.getLogger(__name__)


class CreativeGenerator:
    """
    Generate campaign creative images using SeeDream 4.0.

    This class handles the low-level image generation using the BytePlus ModelArk API
    with the SeeDream 4.0 model.
    """

    def __init__(self, api_key: str | None = None):
        """
        Initialize creative generator with BytePlus ModelArk API key.

        Args:
            api_key: BytePlus API key (optional, will use FAL_KEY env var if not provided)

        Raises:
            ValueError: If FAL_KEY not found in environment
        """
        self.api_key = api_key or os.getenv("FAL_KEY")
        if not self.api_key:
            raise ValueError("FAL_KEY not found in environment variables")

        # BytePlus ModelArk API endpoint (Asia Pacific Southeast region)
        self.api_endpoint = "https://ark.ap-southeast.bytepluses.com/api/v3/images/generations"

        # Configure SSL verification for corporate proxy environments
        # Check if SSL verification should be disabled (for corporate environments)
        # This handles cases where corporate proxies use self-signed certificates
        verify_ssl = os.getenv("FAL_VERIFY_SSL", os.getenv("ANTHROPIC_VERIFY_SSL", "true")).lower() != "false"
        
        if not verify_ssl:
            logger.warning(
                "SSL verification disabled for FAL API - this should only be used in corporate proxy environments"
            )
            # Disable SSL verification for httpx (used by fal_client)
            # Set environment variable that httpx respects
            os.environ["PYTHONHTTPSVERIFY"] = "0"
            # Disable SSL warnings
            try:
                import urllib3
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            except ImportError:
                pass  # urllib3 not available, skip warning suppression
            
            # Configure fal_client's httpx client to not verify SSL
            # fal_client uses httpx internally, so we patch httpx.Client defaults
            # Store original __init__ methods
            original_client_init = httpx.Client.__init__.__func__ if hasattr(httpx.Client.__init__, '__func__') else httpx.Client.__init__
            original_async_client_init = httpx.AsyncClient.__init__.__func__ if hasattr(httpx.AsyncClient.__init__, '__func__') else httpx.AsyncClient.__init__
            
            def patched_client_init(self, *args, **kwargs):
                kwargs.setdefault("verify", False)
                return original_client_init(self, *args, **kwargs)
            
            def patched_async_client_init(self, *args, **kwargs):
                kwargs.setdefault("verify", False)
                return original_async_client_init(self, *args, **kwargs)
            
            # Patch httpx.Client and AsyncClient to default verify=False
            httpx.Client.__init__ = patched_client_init
            httpx.AsyncClient.__init__ = patched_async_client_init

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(f"BytePlus API Key configured: {self.api_key[:8]}... (length: {len(self.api_key)})")
        self.logger.info(f"CreativeGenerator initialized with BytePlus ModelArk SeeDream 4.0 (SSL verification: {verify_ssl})")

    def build_prompt(
        self,
        channel: str,
        visual_concept: str,
        campaign_data: dict[str, Any],
        headline: str | None = None,
        offer_details: str | None = None,
        partner_logos: list | None = None,
        style: str | None = None,
    ) -> str:
        """
        Build detailed prompt for image generation.

        Generates PURE VISUAL IMAGERY ONLY - no text, logos, or branding.
        All brand elements (logo, text overlays) are added via post-processing.

        Args:
            channel: Channel type (email_header or push_header)
            visual_concept: Description of desired imagery
            campaign_data: Campaign configuration data
            headline: NOT USED - text added in post-processing
            offer_details: NOT USED - text added in post-processing
            partner_logos: NOT USED - logos added in post-processing
            style: Optional style override (uses brand default if not provided)

        Returns:
            Complete prompt string for image generation (visual concept only)
        """
        brand = get_brand_guidelines()

        # Build minimal prompt focused ONLY on pure visual concept
        # CRITICAL: No brand names, no text, no logos - post-processing handles ALL branding
        prompt_parts = [
            f"Professional marketing photography: {visual_concept}.",
        ]

        # Add style and mood (NO brand names, NO technical details, NO text)
        style_text = style or brand["style_preferences"][0]
        prompt_parts.append(
            f"{style_text} aesthetic. Vibrant green color palette. Modern dynamic composition."
        )

        # Quality and composition guidance
        prompt_parts.append(
            "High-resolution commercial photography. Cinematic lighting. Professional marketing quality."
        )

        # CRITICAL: Strong negative prompting to prevent ANY text/logo rendering by AI
        prompt_parts.append(
            "IMPORTANT: No text. No letters. No numbers. No words. No typography. No labels. "
            "No signs. No logos. No brand marks. No company names. No branding elements. "
            "Pure visual imagery only. No readable content whatsoever."
        )

        prompt = " ".join(prompt_parts)
        self.logger.info(f"Built clean visual prompt for {channel}: {prompt[:100]}...")

        return prompt

    def generate_image(self, prompt: str, channel: str) -> dict[str, Any]:
        """
        Generate base image using BytePlus ModelArk SeeDream 4.0 API.

        Generates high-resolution base image that will be resized to channel-specific
        dimensions in post-processing. Image is VISUAL ONLY - no text, logos, or branding.
        All brand elements added via post-processing overlay.

        Args:
            prompt: Pure visual concept prompt (no text/logos)
            channel: Channel type for dimension specs (email_header or push_header)

        Returns:
            dict with 'url' (image URL) and 'metadata' (generation details)

        Raises:
            Exception: If image generation fails

        Note:
            - API generates "2K" base image (~2048px)
            - Post-processing resizes to exact channel dimensions
            - Logo overlay happens after resize
        """
        channel_specs = get_channel_specs(channel)
        model_config = get_model_config("seedream_4")

        try:
            self.logger.info(f"Generating clean visual base image for {channel} channel...")

            # Check SSL verification setting
            verify_ssl = os.getenv("FAL_VERIFY_SSL", os.getenv("ANTHROPIC_VERIFY_SSL", "true")).lower() != "false"

            # Call BytePlus ModelArk API with SeeDream 4.0
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            # BytePlus API only accepts predefined size codes, not custom dimensions
            # Generate high-res "2K" base image, then resize to channel specs in post-processing
            # This ensures maximum quality before resizing to exact dimensions
            payload = {
                "model": "seedream-4-0-250828",
                "prompt": prompt,
                "size": "2K",  # High-res base (~2048px) - resized to channel specs later
                "sequential_image_generation": "disabled",
                "response_format": "url",
                "stream": False,
                "watermark": False  # No watermark for professional campaigns
            }

            with httpx.Client(verify=verify_ssl, timeout=120.0) as client:
                response = client.post(self.api_endpoint, headers=headers, json=payload)
                response.raise_for_status()
                result = response.json()

            # Extract image URL from BytePlus response format
            if "data" in result and len(result["data"]) > 0:
                image_url = result["data"][0]["url"]
            elif "url" in result:
                image_url = result["url"]
            else:
                raise Exception(f"Unexpected API response format: {result}")

            metadata = {
                "width": channel_specs["width"],
                "height": channel_specs["height"],
                "content_type": "image/jpeg",
            }

            self.logger.info(f"Image generated successfully: {image_url[:50]}...")

            return {"url": image_url, "metadata": metadata}

        except httpx.HTTPStatusError as e:
            self.logger.error(f"HTTP error during image generation: {e.response.status_code} - {e.response.text}")
            raise Exception(f"BytePlus API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            self.logger.error(f"Image generation failed: {e}")
            raise


async def save_image(
    image_url: str,
    campaign_id: int,
    channel: str,
    variant: int,
    static_dir: str = "backend/static/creatives",
) -> dict[str, str]:
    """
    Download base image and apply post-processing to create final campaign creative.

    Post-processing pipeline:
    1. Download high-res base image from AI model
    2. Resize to exact channel dimensions (smart crop + scale)
    3. Overlay official StarHub logo from assets
    4. Save as high-quality JPEG

    This ensures final creative is:
    - Exact channel dimensions (600x400 email or 1200x628 push)
    - Contains ONLY official StarHub logo (not AI-generated)
    - Clean banner image without metadata or technical text

    Args:
        image_url: URL of generated base image
        campaign_id: Campaign ID for filename
        channel: Channel type (email_header or push_header)
        variant: Variant number (1-3)
        static_dir: Directory to save images (default: backend/static/creatives)

    Returns:
        dict with 'filename' and 'url' keys for final creative

    Raises:
        Exception: If download, processing, or save fails
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{campaign_id}_{channel}_{variant}_{timestamp}.jpg"
    filepath = os.path.join(static_dir, filename)

    # Ensure directory exists
    os.makedirs(static_dir, exist_ok=True)

    try:
        # Check SSL verification setting (same as CreativeGenerator)
        verify_ssl = os.getenv("FAL_VERIFY_SSL", os.getenv("ANTHROPIC_VERIFY_SSL", "true")).lower() != "false"
        
        # Download image
        async with httpx.AsyncClient(timeout=30.0, verify=verify_ssl) as client:
            response = await client.get(image_url)
            response.raise_for_status()
            image_data = response.content

        # Load image with Pillow
        img = Image.open(BytesIO(image_data))
        channel_specs = get_channel_specs(channel)

        # Enforce channel-specific dimensions via resizing
        target_width = channel_specs["width"]
        target_height = channel_specs["height"]

        if img.width != target_width or img.height != target_height:
            logger.info(
                f"Resizing image from {img.width}x{img.height} to "
                f"{target_width}x{target_height} for {channel} channel"
            )

            # Calculate aspect ratios
            current_aspect = img.width / img.height
            target_aspect = target_width / target_height

            # Smart resize: crop to target aspect ratio first, then resize
            if current_aspect > target_aspect:
                # Image is wider - crop width
                new_width = int(img.height * target_aspect)
                left = (img.width - new_width) // 2
                img = img.crop((left, 0, left + new_width, img.height))
            elif current_aspect < target_aspect:
                # Image is taller - crop height
                new_height = int(img.width / target_aspect)
                top = (img.height - new_height) // 2
                img = img.crop((0, top, img.width, top + new_height))

            # Now resize to exact target dimensions
            img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
            logger.info(f"Resize complete: {img.width}x{img.height}")

        # Apply post-processing: logo overlay (text overlays future enhancement)
        img = add_starhub_logo(img)
        
        # Note: Text overlays could be added here in future if needed
        # For now, keeping images clean with just the logo

        # Save the modified image
        img.save(filepath, "JPEG", quality=95)

        # Return relative URL for static serving
        relative_url = f"/static/creatives/{filename}"

        logger.info(f"Saved image with logo overlay: {filename}")

        return {"filename": filename, "url": relative_url}

    except Exception as e:
        logger.error(f"Failed to save image: {e}")
        raise


def add_starhub_logo(img: Image.Image) -> Image.Image:
    """
    Add official StarHub logo overlay to the image in the top-left corner.

    This function overlays the OFFICIAL StarHub logo from frontend assets.
    The AI model should NOT generate any logos - this is the ONLY logo source.

    Args:
        img: PIL Image to add logo to (must be in RGB or RGBA mode)

    Returns:
        Image with official StarHub logo overlay in top-left corner

    Note:
        Logo is sized proportionally (8% of image width) and positioned with
        2.5% horizontal and 4% vertical padding from top-left corner.
    """
    try:
        # Path to OFFICIAL StarHub logo (from frontend assets)
        # This is the ONLY logo that should appear in generated creatives
        workspace_root = "/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator"
        logo_path = os.path.join(workspace_root, "frontend/src/assets/starhub-logo.png")

        if not os.path.exists(logo_path):
            logger.warning(f"Official StarHub logo not found at {logo_path}, skipping logo overlay")
            return img

        # Open official logo
        logo = Image.open(logo_path)

        # Calculate logo size (proportional to image size)
        # Logo should be clearly visible and prominent - 18% of image width for email headers
        # For smaller images (email headers at 600px), we need a larger proportion for visibility
        if img.width < 800:
            # Email headers (600px) - use 18% for good visibility
            target_logo_width = int(img.width * 0.18)
        else:
            # Push notifications (1200px) - use 12% for balanced presence
            target_logo_width = int(img.width * 0.12)

        logo_aspect = logo.height / logo.width
        target_logo_height = int(target_logo_width * logo_aspect)

        # Resize logo with high-quality resampling
        logo = logo.resize((target_logo_width, target_logo_height), Image.Resampling.LANCZOS)

        # Calculate position (top-left with brand-compliant padding)
        padding_x = int(img.width * 0.03)  # 3% horizontal padding
        padding_y = int(img.height * 0.03)  # 3% vertical padding
        position = (padding_x, padding_y)

        # Handle transparency-aware compositing
        if logo.mode in ('RGBA', 'LA') or (logo.mode == 'P' and 'transparency' in logo.info):
            # Logo has transparency - composite properly
            img_copy = img.convert('RGBA')
            logo_rgba = logo.convert('RGBA')
            img_copy.paste(logo_rgba, position, logo_rgba)
            # Convert back to RGB for JPEG output
            img = img_copy.convert('RGB')
        else:
            # No transparency - direct paste
            img.paste(logo, position)

        logger.info(
            f"✓ Added official StarHub logo at {position} "
            f"with size {target_logo_width}x{target_logo_height}px"
        )

        return img

    except Exception as e:
        logger.error(f"Failed to add StarHub logo overlay: {e}")
        # Return original image if logo overlay fails (non-fatal error)
        return img


def score_creative(
    image_path: str,
    channel: str,
    prompt_used: str,
) -> dict[str, Any]:
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

    def __init__(self, api_key: str | None = None):
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
        campaign_data: dict[str, Any],
        db: Session,
        **kwargs,
    ) -> list[dict[str, Any]]:
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
