"""
Communication API endpoints for generation and management.
"""

import json
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.models.campaign import Campaign
from app.models.communication import GeneratedCommunication
from app.schemas.campaign import CustomizationOptions, PromotionDetails
from app.schemas.communication import (
    CommunicationResponse,
    CommunicationUpdate,
    GenerationResponse,
    RegenerateRequest,
)
from app.services.generation_service import GenerationService
from database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["communications"])


@router.post("/campaigns/{campaign_id}/generate", response_model=GenerationResponse)
def generate_communications(campaign_id: int, db: Session = Depends(get_db)):
    """
    Generate 5 communication variations for campaign.

    Process:
    1. Load campaign from database
    2. Call generation service (Claude API + starhub-comms skill)
    3. Score all 5 variations
    4. Save to database
    5. Return ranked variations

    Args:
        campaign_id: Campaign ID
        db: Database session

    Returns:
        Generation response with all 5 variations and scores

    Raises:
        HTTPException: If campaign not found or generation fails
    """
    # Load campaign
    campaign = db.query(Campaign).filter(Campaign.campaign_id == campaign_id).first()
    if not campaign:
        logger.warning(f"Campaign {campaign_id} not found for generation")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign with ID {campaign_id} not found",
        )

    # Parse and validate JSON fields with schema validation
    try:
        # Parse product_lines and cohorts (simple lists)
        product_lines = (
            json.loads(campaign.product_lines)
            if isinstance(campaign.product_lines, str)
            else campaign.product_lines
        )
        cohorts = (
            json.loads(campaign.cohorts) if isinstance(campaign.cohorts, str) else campaign.cohorts
        )

        # Parse and validate promotion_details with Pydantic schema
        if campaign.promotion_details:
            promo_dict = (
                json.loads(campaign.promotion_details)
                if isinstance(campaign.promotion_details, str)
                else campaign.promotion_details
            )
            validated_promo = PromotionDetails(**promo_dict)
            promotion_details = validated_promo.model_dump()
        else:
            promotion_details = None

        # Parse and validate customization with Pydantic schema
        custom_dict = (
            json.loads(campaign.customization)
            if isinstance(campaign.customization, str)
            else campaign.customization
        )
        validated_custom = CustomizationOptions(**custom_dict)
        customization = validated_custom.model_dump()

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse campaign JSON fields for campaign {campaign_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Campaign data is corrupted: Invalid JSON format",
        )
    except ValidationError as e:
        logger.error(f"Campaign data validation failed for campaign {campaign_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Campaign data validation failed: {str(e)}",
        )

    # Generate and score communications
    try:
        service = GenerationService()
        results = service.generate_and_score(
            channel=campaign.channel,
            cohorts=cohorts,
            objective=campaign.objective,
            product_lines=product_lines,
            promotion_details=promotion_details,
            customization=customization,
            is_promotional=(campaign.objective in ["promotion", "upsell", "cross_sell"]),
        )

        logger.info(f"Generated {len(results)} variations for campaign {campaign_id}")

    except Exception as e:
        error_msg = str(e)
        error_type = type(e).__name__
        logger.error(
            f"Generation failed for campaign {campaign_id}: {error_type}: {error_msg}",
            exc_info=True,
        )

        # Provide more helpful error messages
        if (
            "api_key" in error_msg.lower()
            or "authentication" in error_msg.lower()
            or "ANTHROPIC_API_KEY" in error_msg
        ):
            detail = "Generation failed: API key is missing or invalid. Please ensure ANTHROPIC_API_KEY is set in backend/.env file and restart the backend server."
        elif (
            "connection" in error_msg.lower()
            or "timeout" in error_msg.lower()
            or "ConnectionError" in error_type
        ):
            detail = f"Generation failed: Unable to connect to AI service. {error_msg}. Please check your network connection and ensure the backend has been restarted after setting ANTHROPIC_API_KEY."
        else:
            detail = f"Generation failed: {error_type}: {error_msg}"

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)

    # Save to database
    communications = []
    try:
        for result in results:
            # Create proper score breakdown structure for Pydantic model
            score_breakdown_dict = {
                "channel_best_practices": result["channel_score"],
                "cohort_alignment": result["cohort_score"],
                "objective_effectiveness": result["objective_score"],
                "compliance_safety": result["compliance_score"],
            }

            comm = GeneratedCommunication(
                campaign_id=campaign_id,
                variation_number=result["variation_number"],
                communication_text=result["text"],
                recommendation_score=result["total_score"],
                score_breakdown=json.dumps(score_breakdown_dict),
                recommendation_reasoning=result.get("reasoning", ""),
                compliance_notes=", ".join(result.get("compliance_notes", []))
                if isinstance(result.get("compliance_notes"), list)
                else str(result.get("compliance_notes", "")),
                is_selected=False,
                created_at=datetime.utcnow(),
            )
            db.add(comm)
            communications.append(comm)

        db.commit()

        # Refresh all to get IDs
        for comm in communications:
            db.refresh(comm)

        logger.info(f"Saved {len(communications)} communications for campaign {campaign_id}")

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to save communications for campaign {campaign_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save communications: {str(e)}",
        )

    # Convert to response schemas
    communication_responses = [CommunicationResponse.from_orm_model(c) for c in communications]

    return GenerationResponse.create(
        campaign_id=campaign_id, communications=communication_responses
    )


@router.post("/campaigns/{campaign_id}/regenerate", response_model=GenerationResponse)
def regenerate_communications(
    campaign_id: int, request: RegenerateRequest, db: Session = Depends(get_db)
):
    """
    Regenerate with parameter tweaks.

    Updates campaign with new parameters and generates new variations.
    Previous variations remain in database for history.

    Args:
        campaign_id: Campaign ID
        request: Updated parameters for regeneration
        db: Database session

    Returns:
        New generation response with fresh variations

    Raises:
        HTTPException: If campaign not found or regeneration fails
    """
    campaign = db.query(Campaign).filter(Campaign.campaign_id == campaign_id).first()
    if not campaign:
        logger.warning(f"Campaign {campaign_id} not found for regeneration")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign with ID {campaign_id} not found",
        )

    # Update campaign with new parameters
    try:
        updated_params = request.updated_params
        for field, value in updated_params.items():
            if field in ["product_lines", "cohorts"]:
                setattr(campaign, field, json.dumps(value))
            elif field in ["promotion_details", "customization"]:
                setattr(campaign, field, json.dumps(value))
            else:
                setattr(campaign, field, value)

        campaign.updated_at = datetime.utcnow()
        db.commit()

        logger.info(
            f"Updated campaign {campaign_id} for regeneration with params: {list(updated_params.keys())}"
        )

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update campaign {campaign_id} for regeneration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update campaign: {str(e)}",
        )

    # Generate new communications (reuse generate endpoint logic)
    return generate_communications(campaign_id, db)


@router.get("/campaigns/{campaign_id}/communications", response_model=list[CommunicationResponse])
def get_campaign_communications(campaign_id: int, db: Session = Depends(get_db)):
    """
    Get all generated communications for campaign (including history).

    Returns all variations ever generated for this campaign, ordered by
    creation date (newest first).

    Args:
        campaign_id: Campaign ID
        db: Database session

    Returns:
        List of all communications for campaign

    Raises:
        HTTPException: If campaign not found
    """
    campaign = db.query(Campaign).filter(Campaign.campaign_id == campaign_id).first()
    if not campaign:
        logger.warning(f"Campaign {campaign_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign with ID {campaign_id} not found",
        )

    communications = (
        db.query(GeneratedCommunication)
        .filter(GeneratedCommunication.campaign_id == campaign_id)
        .order_by(GeneratedCommunication.created_at.desc())
        .all()
    )

    logger.info(f"Retrieved {len(communications)} communications for campaign {campaign_id}")

    return [CommunicationResponse.from_orm_model(c) for c in communications]


@router.put("/communications/{communication_id}", response_model=CommunicationResponse)
def update_communication(
    communication_id: int, updates: CommunicationUpdate, db: Session = Depends(get_db)
):
    """
    Update communication (mark selected, save edited text).

    Allows users to:
    - Mark a variation as selected for use in the campaign
    - Save user-edited versions of the communication text

    Args:
        communication_id: Communication ID
        updates: Update data (is_selected, edited_text)
        db: Database session

    Returns:
        Updated communication

    Raises:
        HTTPException: If communication not found
    """
    comm = (
        db.query(GeneratedCommunication)
        .filter(GeneratedCommunication.communication_id == communication_id)
        .first()
    )

    if not comm:
        logger.warning(f"Communication {communication_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Communication with ID {communication_id} not found",
        )

    try:
        update_data = updates.dict(exclude_unset=True)

        # If marking as selected, unselect others in same campaign
        if update_data.get("is_selected", False):
            db.query(GeneratedCommunication).filter(
                GeneratedCommunication.campaign_id == comm.campaign_id,
                GeneratedCommunication.communication_id != communication_id,
            ).update({"is_selected": False})

        # Apply updates
        for field, value in update_data.items():
            setattr(comm, field, value)

        db.commit()
        db.refresh(comm)

        logger.info(f"Updated communication {communication_id}")

        return CommunicationResponse.from_orm_model(comm)

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update communication {communication_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update communication: {str(e)}",
        )


@router.get("/communications/{communication_id}", response_model=CommunicationResponse)
def get_communication(communication_id: int, db: Session = Depends(get_db)):
    """
    Get a specific communication by ID.

    Args:
        communication_id: Communication ID
        db: Database session

    Returns:
        Communication details

    Raises:
        HTTPException: If communication not found
    """
    comm = (
        db.query(GeneratedCommunication)
        .filter(GeneratedCommunication.communication_id == communication_id)
        .first()
    )

    if not comm:
        logger.warning(f"Communication {communication_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Communication with ID {communication_id} not found",
        )

    return CommunicationResponse.from_orm_model(comm)
