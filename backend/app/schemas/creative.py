"""
Pydantic schemas for creative-related requests and responses.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ChannelType(str, Enum):
    """Creative channel types."""

    EMAIL_HEADER = "email_header"
    PUSH_HEADER = "push_header"


class CreativeGenerationRequest(BaseModel):
    """Schema for creative generation request."""

    channel: ChannelType = Field(
        ..., description="Channel type for the creative (email_header or push_header)"
    )
    visual_concept: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Visual concept description for the creative",
    )
    headline: str | None = Field(
        None, max_length=100, description="Optional headline text to include in the creative"
    )
    offer_details: str | None = Field(
        None, max_length=200, description="Optional offer details to highlight"
    )
    partner_logos: list[str] | None = Field(
        default_factory=list, description="List of partner logo identifiers to include"
    )
    style_preference: str | None = Field(
        None, description="Style preference: modern, minimal, vibrant, elegant, bold"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "channel": "email_header",
                "visual_concept": "Young professionals using 5G on the go in Singapore's Marina Bay area",
                "headline": "Experience Ultra-Fast 5G",
                "offer_details": "From $35/month with 100GB data",
                "partner_logos": ["netflix", "spotify"],
                "style_preference": "modern",
            }
        }
    )


class GeneratedCreativeResponse(BaseModel):
    """Schema for generated creative response."""

    creative_id: int
    campaign_id: int
    variant_number: int = Field(..., ge=1, le=3, description="Variant number (1-3)")
    channel_type: ChannelType
    image_filename: str
    image_url: str
    prompt_used: str
    generation_params: dict[str, Any]
    model_used: str
    recommendation_score: int = Field(..., ge=0, le=100, description="Recommendation score (0-100)")
    score_reasoning: str | None = None
    is_selected: bool = False
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm_model(cls, db_model):
        """
        Convert database model to response schema.

        Args:
            db_model: GeneratedCreative database model instance

        Returns:
            GeneratedCreativeResponse instance

        This method handles JSON field parsing from database.
        """
        import json

        # Parse generation_params from JSON string
        generation_params_data = (
            json.loads(db_model.generation_params)
            if isinstance(db_model.generation_params, str)
            else db_model.generation_params
        )

        return cls(
            creative_id=db_model.creative_id,
            campaign_id=db_model.campaign_id,
            variant_number=db_model.variant_number,
            channel_type=ChannelType(db_model.channel_type),
            image_filename=db_model.image_filename,
            image_url=db_model.image_url,
            prompt_used=db_model.prompt_used,
            generation_params=generation_params_data,
            model_used=db_model.model_used,
            recommendation_score=db_model.recommendation_score,
            score_reasoning=db_model.score_reasoning,
            is_selected=db_model.is_selected,
            created_at=db_model.created_at,
        )


class CreativeListResponse(BaseModel):
    """Schema for list of creatives response."""

    campaign_id: int
    creatives: list[GeneratedCreativeResponse]
    total: int = Field(..., description="Total number of creatives")

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def create(cls, campaign_id: int, creatives: list[GeneratedCreativeResponse]):
        """
        Create a creative list response with computed fields.

        Args:
            campaign_id: Campaign ID
            creatives: List of generated creatives

        Returns:
            CreativeListResponse instance
        """
        return cls(campaign_id=campaign_id, creatives=creatives, total=len(creatives))


class CreativeSelectionRequest(BaseModel):
    """Schema for creative selection request."""

    is_selected: bool = Field(
        ..., description="Mark this creative as selected (true) or unselected (false)"
    )

    model_config = ConfigDict(json_schema_extra={"example": {"is_selected": True}})
