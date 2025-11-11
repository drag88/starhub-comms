"""
Campaign API endpoints for CRUD operations.
"""

import json
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.models.campaign import Campaign
from app.schemas.campaign import CampaignCreate, CampaignResponse, CampaignUpdate
from app.services.config_loader import get_cohort_by_id
from database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/campaigns", tags=["campaigns"])


def infer_product_lines_from_cohorts(cohort_ids: list[str]) -> list[str]:
    """
    Infer product lines from selected cohorts based on cohort characteristics.

    Args:
        cohort_ids: List of cohort IDs

    Returns:
        List of inferred product line IDs
    """
    product_lines = set()

    for cohort_id in cohort_ids:
        cohort = get_cohort_by_id(cohort_id)
        if not cohort:
            logger.warning(f"Cohort not found for ID: {cohort_id}")
            continue

        # Check if cohort has explicit target_products field
        if "target_products" in cohort and cohort["target_products"]:
            product_lines.update(cohort["target_products"])
            continue

        # Fallback: infer from cohort ID or name
        cohort_id_lower = cohort_id.lower()
        cohort_name_lower = cohort.get("name", "").lower()

        # Broadband-related cohorts
        if any(
            keyword in cohort_id_lower or keyword in cohort_name_lower
            for keyword in ["broadband", "fiber", "10gbps", "premium_segment"]
        ):
            product_lines.add("broadband_fiber")
            if "10gbps" in cohort_id_lower or "10gbps" in cohort_name_lower:
                product_lines.add("broadband_10gbps")

        # Bundle-related cohorts
        elif any(
            keyword in cohort_id_lower or keyword in cohort_name_lower
            for keyword in ["bundle", "triple", "homehub"]
        ):
            product_lines.add("bundle_homehub")

        # Entertainment-related cohorts
        elif any(
            keyword in cohort_id_lower or keyword in cohort_name_lower
            for keyword in ["entertainment", "sports", "streaming", "tv"]
        ):
            product_lines.add("entertainment_tv")

        # Mobile-related cohorts (default)
        else:
            product_lines.add("mobile_postpaid")

    # Return list or default to mobile_postpaid if no matches
    return list(product_lines) if product_lines else ["mobile_postpaid"]


@router.post("/", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
def create_campaign(campaign_data: CampaignCreate, db: Session = Depends(get_db)):
    """
    Create a new campaign.

    Validates all inputs and stores campaign configuration in database.

    Args:
        campaign_data: Campaign creation data
        db: Database session

    Returns:
        Created campaign with all details

    Raises:
        HTTPException: If validation fails or database error occurs
    """
    try:
        # Infer product_lines from cohorts if not provided or if default value
        product_lines = campaign_data.product_lines
        if not product_lines or product_lines == ["mobile_postpaid"]:
            inferred_lines = infer_product_lines_from_cohorts(campaign_data.cohorts)
            logger.info(
                f"Inferred product_lines {inferred_lines} from cohorts {campaign_data.cohorts}"
            )
            product_lines = inferred_lines

        # Convert Pydantic models to dict/JSON for storage
        campaign = Campaign(
            campaign_name=campaign_data.campaign_name,
            channel=campaign_data.channel,
            objective=campaign_data.objective,
            product_lines=json.dumps(product_lines),
            cohorts=json.dumps(campaign_data.cohorts),
            promotion_details=json.dumps(campaign_data.promotion_details.model_dump())
            if campaign_data.promotion_details
            else None,
            customization=json.dumps(campaign_data.customization.model_dump()),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        db.add(campaign)
        db.commit()
        db.refresh(campaign)

        logger.info(f"Created campaign {campaign.campaign_id}: {campaign.campaign_name}")

        # Convert to response schema
        return CampaignResponse.from_orm_model(campaign)

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create campaign: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create campaign: {str(e)}",
        )


@router.get("/{campaign_id}", response_model=CampaignResponse)
def get_campaign(campaign_id: int, db: Session = Depends(get_db)):
    """
    Get campaign by ID.

    Args:
        campaign_id: Campaign ID
        db: Database session

    Returns:
        Campaign details

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

    return CampaignResponse.from_orm_model(campaign)


@router.put("/{campaign_id}", response_model=CampaignResponse)
def update_campaign(campaign_id: int, campaign_data: CampaignUpdate, db: Session = Depends(get_db)):
    """
    Update campaign parameters.

    Only provided fields will be updated. Omitted fields remain unchanged.

    Args:
        campaign_id: Campaign ID
        campaign_data: Updated campaign data
        db: Database session

    Returns:
        Updated campaign details

    Raises:
        HTTPException: If campaign not found or validation fails
    """
    campaign = db.query(Campaign).filter(Campaign.campaign_id == campaign_id).first()

    if not campaign:
        logger.warning(f"Campaign {campaign_id} not found for update")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign with ID {campaign_id} not found",
        )

    try:
        # Update only provided fields
        update_data = campaign_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if field in ["product_lines", "cohorts"]:
                setattr(campaign, field, json.dumps(value))
            elif field == "promotion_details" and value:
                # value is already a dict from model_dump
                setattr(campaign, field, json.dumps(value))
            elif field == "customization" and value:
                # value is already a dict from model_dump
                setattr(campaign, field, json.dumps(value))
            else:
                setattr(campaign, field, value)

        campaign.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(campaign)

        logger.info(f"Updated campaign {campaign_id}")

        return CampaignResponse.from_orm_model(campaign)

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update campaign {campaign_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update campaign: {str(e)}",
        )


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_campaign(campaign_id: int, db: Session = Depends(get_db)):
    """
    Delete campaign and all generated communications (cascade).

    This operation cannot be undone. All communications and related data
    will be permanently deleted.

    Args:
        campaign_id: Campaign ID
        db: Database session

    Returns:
        No content (204)

    Raises:
        HTTPException: If campaign not found
    """
    campaign = db.query(Campaign).filter(Campaign.campaign_id == campaign_id).first()

    if not campaign:
        logger.warning(f"Campaign {campaign_id} not found for deletion")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign with ID {campaign_id} not found",
        )

    try:
        db.delete(campaign)
        db.commit()

        logger.info(f"Deleted campaign {campaign_id}: {campaign.campaign_name}")

        return None

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete campaign {campaign_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete campaign: {str(e)}",
        )


@router.get("/", response_model=list[CampaignResponse])
def list_campaigns(
    skip: int = Query(0, ge=0, description="Number of records to skip (pagination)"),
    limit: int = Query(20, ge=1, le=100, description="Maximum records to return (1-100)"),
    channel: str | None = Query(
        None, pattern="^(email|sms|push)$", description="Filter by channel"
    ),
    objective: str | None = Query(None, description="Filter by objective"),
    db: Session = Depends(get_db),
):
    """
    List campaigns with pagination and filtering.

    Query parameters:
    - skip: Number of records to skip (for pagination)
    - limit: Maximum records to return (1-100)
    - channel: Filter by channel (email, sms, push)
    - objective: Filter by objective

    Args:
        skip: Offset for pagination
        limit: Max results per page
        channel: Optional channel filter
        objective: Optional objective filter
        db: Database session

    Returns:
        List of campaigns (sorted by creation date, newest first)
    """
    try:
        query = db.query(Campaign)

        # Apply filters
        if channel:
            query = query.filter(Campaign.channel == channel)
        if objective:
            query = query.filter(Campaign.objective == objective)

        # Get total count for metadata (optional)
        total = query.count()

        # Apply pagination and ordering
        campaigns = query.order_by(Campaign.created_at.desc()).offset(skip).limit(limit).all()

        logger.info(
            f"Listed {len(campaigns)} campaigns (total: {total}, skip: {skip}, limit: {limit})"
        )

        # Convert to response schemas
        return [CampaignResponse.from_orm_model(c) for c in campaigns]

    except Exception as e:
        logger.error(f"Failed to list campaigns: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list campaigns: {str(e)}",
        )
