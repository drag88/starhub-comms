"""
Creative API endpoints for campaign creative image generation and management.
"""

import json
import logging
import os
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.campaign import Campaign
from app.models.creative import GeneratedCreative
from app.schemas.creative import (
    CreativeListResponse,
    CreativeRegenerateRequest,
    CreativeSelectionRequest,
    GeneratedCreativeResponse,
)
from app.services.creative_generator import CreativeGenerationService
from database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["creatives"])


@router.post(
    "/campaigns/{campaign_id}/generate-creatives",
    response_model=CreativeListResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_campaign_creatives(campaign_id: int, db: Session = Depends(get_db)):
    """
    Generate 3 creative image variations for campaign.

    This endpoint generates creative images (email headers or push notification headers)
    based on the campaign configuration. It produces 3 variants with different style
    approaches, scores each variant, and returns them ranked by recommendation score.

    Process:
    1. Load campaign from database (404 if not found)
    2. Parse campaign JSON fields (channel, objective, product_lines, etc.)
    3. Determine channel type for creative (email_header or push_header)
    4. Call CreativeGenerationService to generate 3 variants
    5. Score each variant using heuristic algorithm
    6. Save images to disk and database
    7. Return ranked variations (highest score first)

    Args:
        campaign_id: Campaign ID to generate creatives for
        db: Database session

    Returns:
        CreativeListResponse with 3 generated creatives sorted by score

    Raises:
        HTTPException 404: Campaign not found
        HTTPException 500: Generation failed (API key missing, network error, etc.)

    Example:
        POST /api/v1/campaigns/123/generate-creatives
        Response: {
            "campaign_id": 123,
            "creatives": [...3 variants...],
            "total": 3
        }
    """
    # Load campaign
    campaign = db.query(Campaign).filter(Campaign.campaign_id == campaign_id).first()
    if not campaign:
        logger.warning(f"Campaign {campaign_id} not found for creative generation")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign with ID {campaign_id} not found",
        )

    # Parse campaign JSON fields
    try:
        product_lines = (
            json.loads(campaign.product_lines)
            if isinstance(campaign.product_lines, str)
            else campaign.product_lines
        )
        cohorts = (
            json.loads(campaign.cohorts) if isinstance(campaign.cohorts, str) else campaign.cohorts
        )

        # Determine channel type for creative
        # email campaigns get email_header, push campaigns get push_header
        channel_type = f"{campaign.channel}_header"

        # Build campaign data for prompt generation
        campaign_data = {
            "campaign_id": campaign_id,
            "campaign_name": campaign.campaign_name,
            "channel": campaign.channel,
            "objective": campaign.objective,
            "product_lines": product_lines,
            "cohorts": cohorts,
        }

        # Extract visual concept from campaign name or objective
        visual_concept = f"{campaign.campaign_name} - {campaign.objective}"

        logger.info(
            f"Starting creative generation for campaign {campaign_id}, channel {channel_type}"
        )

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse campaign JSON fields for campaign {campaign_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Campaign data is corrupted: Invalid JSON format",
        )

    # Generate and score creatives
    try:
        service = CreativeGenerationService()
        results = await service.generate_and_score(
            campaign_id=campaign_id,
            channel=channel_type,
            visual_concept=visual_concept,
            campaign_data=campaign_data,
            db=db,
        )

        logger.info(f"Generated {len(results)} creative variations for campaign {campaign_id}")

    except ValueError as e:
        # API key missing
        error_msg = str(e)
        logger.error(f"Creative generation failed for campaign {campaign_id}: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Creative generation failed: {error_msg}. Please ensure FAL_KEY is set in backend/.env file.",
        )
    except Exception as e:
        error_msg = str(e)
        error_type = type(e).__name__
        logger.error(
            f"Creative generation failed for campaign {campaign_id}: {error_type}: {error_msg}",
            exc_info=True,
        )

        # Provide helpful error messages
        if (
            "api_key" in error_msg.lower()
            or "authentication" in error_msg.lower()
            or "FAL_KEY" in error_msg
        ):
            detail = "Creative generation failed: API key is missing or invalid. Please ensure FAL_KEY is set in backend/.env file and restart the backend server."
        elif (
            "connection" in error_msg.lower()
            or "timeout" in error_msg.lower()
            or "ConnectionError" in error_type
        ):
            detail = f"Creative generation failed: Unable to connect to AI service. {error_msg}. Please check your network connection."
        else:
            detail = f"Creative generation failed: {error_type}: {error_msg}"

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)

    # Load generated creatives from database (generate_and_score saves them)
    creatives = (
        db.query(GeneratedCreative)
        .filter(GeneratedCreative.campaign_id == campaign_id)
        .order_by(GeneratedCreative.recommendation_score.desc())
        .all()
    )

    # Convert to response schemas
    creative_responses = [GeneratedCreativeResponse.from_orm_model(c) for c in creatives]

    return CreativeListResponse.create(campaign_id=campaign_id, creatives=creative_responses)


@router.post(
    "/campaigns/{campaign_id}/regenerate-creatives",
    response_model=CreativeListResponse,
    status_code=status.HTTP_201_CREATED,
)
async def regenerate_campaign_creatives(
    campaign_id: int,
    request: CreativeRegenerateRequest,
    db: Session = Depends(get_db),
):
    """
    Regenerate creative images with user feedback.

    This endpoint deletes existing creatives and generates new ones incorporating
    user feedback. The feedback is used to refine the visual concept and style.

    Process:
    1. Load campaign from database (404 if not found)
    2. Delete existing creatives for this campaign
    3. Incorporate user feedback into visual concept
    4. Generate 3 new creative variants
    5. Score and save new creatives
    6. Return ranked variations

    Args:
        campaign_id: Campaign ID to regenerate creatives for
        request: Regeneration request with optional feedback
        db: Database session

    Returns:
        CreativeListResponse with 3 new creatives sorted by score

    Raises:
        HTTPException 404: Campaign not found
        HTTPException 500: Generation failed

    Example:
        POST /api/v1/campaigns/123/regenerate-creatives
        Body: {"feedback": "Make images more vibrant with dynamic poses"}
    """
    # Load campaign
    campaign = db.query(Campaign).filter(Campaign.campaign_id == campaign_id).first()
    if not campaign:
        logger.warning(f"Campaign {campaign_id} not found for creative regeneration")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign with ID {campaign_id} not found",
        )

    # Delete existing creatives
    existing_creatives = (
        db.query(GeneratedCreative)
        .filter(GeneratedCreative.campaign_id == campaign_id)
        .all()
    )

    for creative in existing_creatives:
        # Delete image file from disk
        image_path = Path("backend") / "static" / "creatives" / creative.image_filename
        if image_path.exists():
            os.remove(image_path)
            logger.info(f"Deleted image file: {creative.image_filename}")

        # Delete database record
        db.delete(creative)

    db.commit()
    logger.info(f"Deleted {len(existing_creatives)} existing creatives for campaign {campaign_id}")

    # Parse campaign JSON fields
    try:
        product_lines = (
            json.loads(campaign.product_lines)
            if isinstance(campaign.product_lines, str)
            else campaign.product_lines
        )
        cohorts = (
            json.loads(campaign.cohorts) if isinstance(campaign.cohorts, str) else campaign.cohorts
        )

        channel_type = f"{campaign.channel}_header"

        campaign_data = {
            "campaign_id": campaign_id,
            "campaign_name": campaign.campaign_name,
            "channel": campaign.channel,
            "objective": campaign.objective,
            "product_lines": product_lines,
            "cohorts": cohorts,
        }

        # Build visual concept with feedback
        visual_concept = f"{campaign.campaign_name} - {campaign.objective}"
        if request.feedback:
            visual_concept += f". User feedback: {request.feedback}"
            logger.info(f"Regenerating with feedback: {request.feedback}")

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse campaign JSON fields: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Campaign data corrupted",
        )

    # Generate new creatives
    try:
        service = CreativeGenerationService()
        results = await service.generate_and_score(
            campaign_id=campaign_id,
            channel=channel_type,
            visual_concept=visual_concept,
            campaign_data=campaign_data,
            db=db,
        )

        logger.info(f"Regenerated {len(results)} creative variations for campaign {campaign_id}")

    except Exception as e:
        logger.error(f"Creative regeneration failed: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Creative regeneration failed: {str(e)}",
        )

    # Load new creatives
    creatives = (
        db.query(GeneratedCreative)
        .filter(GeneratedCreative.campaign_id == campaign_id)
        .order_by(GeneratedCreative.recommendation_score.desc())
        .all()
    )

    creative_responses = [GeneratedCreativeResponse.from_orm_model(c) for c in creatives]

    return CreativeListResponse.create(campaign_id=campaign_id, creatives=creative_responses)


@router.get("/campaigns/{campaign_id}/creatives", response_model=CreativeListResponse)
def get_campaign_creatives(campaign_id: int, db: Session = Depends(get_db)):
    """
    Get all generated creatives for campaign.

    Retrieves all creative images generated for this campaign, sorted by
    recommendation score (highest first). Includes all variants from all
    generation attempts (history preserved).

    Args:
        campaign_id: Campaign ID
        db: Database session

    Returns:
        List of creatives sorted by recommendation score

    Raises:
        HTTPException 404: Campaign not found

    Example:
        GET /api/v1/campaigns/123/creatives
        Response: {
            "campaign_id": 123,
            "creatives": [...all creatives...],
            "total": 6
        }
    """
    # Validate campaign exists
    campaign = db.query(Campaign).filter(Campaign.campaign_id == campaign_id).first()
    if not campaign:
        logger.warning(f"Campaign {campaign_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign with ID {campaign_id} not found",
        )

    # Query all creatives for campaign, sorted by score descending
    creatives = (
        db.query(GeneratedCreative)
        .filter(GeneratedCreative.campaign_id == campaign_id)
        .order_by(GeneratedCreative.recommendation_score.desc())
        .all()
    )

    logger.info(f"Retrieved {len(creatives)} creatives for campaign {campaign_id}")

    # Convert to response schemas
    creative_responses = [GeneratedCreativeResponse.from_orm_model(c) for c in creatives]

    return CreativeListResponse.create(campaign_id=campaign_id, creatives=creative_responses)


@router.get("/creatives/{creative_id}", response_model=GeneratedCreativeResponse)
def get_creative(creative_id: int, db: Session = Depends(get_db)):
    """
    Get a specific creative by ID.

    Retrieves detailed information about a single creative image, including
    generation parameters, prompt used, score, and image URL.

    Args:
        creative_id: Creative ID
        db: Database session

    Returns:
        Creative details

    Raises:
        HTTPException 404: Creative not found

    Example:
        GET /api/v1/creatives/456
        Response: {
            "creative_id": 456,
            "campaign_id": 123,
            "variant_number": 1,
            "image_url": "/static/creatives/123_email_header_1_20250110120000.jpg",
            "recommendation_score": 92,
            ...
        }
    """
    creative = (
        db.query(GeneratedCreative).filter(GeneratedCreative.creative_id == creative_id).first()
    )

    if not creative:
        logger.warning(f"Creative {creative_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Creative with ID {creative_id} not found",
        )

    return GeneratedCreativeResponse.from_orm_model(creative)


@router.put("/creatives/{creative_id}/select", response_model=GeneratedCreativeResponse)
def select_creative(
    creative_id: int, selection: CreativeSelectionRequest, db: Session = Depends(get_db)
):
    """
    Mark creative as selected or unselected.

    Allows users to mark a creative as selected for use in the campaign.
    When selecting a creative, all other creatives for the same campaign
    are automatically unselected (only one creative can be selected per campaign).

    Args:
        creative_id: Creative ID
        selection: Selection request with is_selected boolean
        db: Database session

    Returns:
        Updated creative

    Raises:
        HTTPException 404: Creative not found

    Example:
        PUT /api/v1/creatives/456/select
        Body: {"is_selected": true}
        Response: {...updated creative with is_selected=true...}
    """
    creative = (
        db.query(GeneratedCreative).filter(GeneratedCreative.creative_id == creative_id).first()
    )

    if not creative:
        logger.warning(f"Creative {creative_id} not found for selection")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Creative with ID {creative_id} not found",
        )

    try:
        # If marking as selected, unselect others in same campaign
        if selection.is_selected:
            db.query(GeneratedCreative).filter(
                GeneratedCreative.campaign_id == creative.campaign_id,
                GeneratedCreative.creative_id != creative_id,
            ).update({"is_selected": False})

        # Update this creative's selection status
        creative.is_selected = selection.is_selected

        db.commit()
        db.refresh(creative)

        logger.info(f"Updated creative {creative_id} selection to {selection.is_selected}")

        return GeneratedCreativeResponse.from_orm_model(creative)

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update creative {creative_id} selection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update creative selection: {str(e)}",
        )


@router.delete("/creatives/{creative_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_creative(creative_id: int, db: Session = Depends(get_db)):
    """
    Delete creative image and database record.

    Permanently deletes the creative image file from disk and removes the
    database record. This operation cannot be undone.

    Process:
    1. Load creative from database (404 if not found)
    2. Delete image file from static/creatives/ directory
    3. Delete database record
    4. Return 204 No Content

    Args:
        creative_id: Creative ID
        db: Database session

    Returns:
        No content (204)

    Raises:
        HTTPException 404: Creative not found

    Example:
        DELETE /api/v1/creatives/456
        Response: 204 No Content
    """
    creative = (
        db.query(GeneratedCreative).filter(GeneratedCreative.creative_id == creative_id).first()
    )

    if not creative:
        logger.warning(f"Creative {creative_id} not found for deletion")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Creative with ID {creative_id} not found",
        )

    try:
        # Delete image file from disk
        # Image is stored in backend/static/creatives/
        image_path = Path("backend") / "static" / "creatives" / creative.image_filename

        if image_path.exists():
            os.remove(image_path)
            logger.info(f"Deleted image file: {creative.image_filename}")
        else:
            logger.warning(f"Image file not found for deletion: {creative.image_filename}")

        # Delete database record
        db.delete(creative)
        db.commit()

        logger.info(f"Deleted creative {creative_id} and associated image")

        return None

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete creative {creative_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete creative: {str(e)}",
        )
