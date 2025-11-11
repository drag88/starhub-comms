"""
Pydantic schemas for communication-related requests and responses.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ScoreBreakdown(BaseModel):
    """Breakdown of recommendation score components."""

    channel_best_practices: int = Field(..., description="Score for channel best practices (0-100)")
    cohort_alignment: int = Field(..., description="Score for cohort alignment (0-100)")
    objective_effectiveness: int = Field(
        ..., description="Score for objective effectiveness (0-100)"
    )
    compliance_safety: int = Field(..., description="Score for compliance and safety (0-100)")


class CommunicationResponse(BaseModel):
    """Schema for generated communication response."""

    communication_id: int
    campaign_id: int
    variation_number: int = Field(..., ge=1, le=5, description="Variation number (1-5)")
    communication_text: str
    recommendation_score: int = Field(
        ..., ge=0, le=100, description="Overall recommendation score (0-100)"
    )
    score_breakdown: ScoreBreakdown
    recommendation_reasoning: str
    compliance_notes: str
    is_selected: bool
    edited_text: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_model(cls, db_model):
        """
        Convert database model to response schema.

        This method handles JSON field parsing from database.
        """
        import json

        # Parse score_breakdown from JSON string
        score_breakdown_data = (
            json.loads(db_model.score_breakdown)
            if isinstance(db_model.score_breakdown, str)
            else db_model.score_breakdown
        )

        return cls(
            communication_id=db_model.communication_id,
            campaign_id=db_model.campaign_id,
            variation_number=db_model.variation_number,
            communication_text=db_model.communication_text,
            recommendation_score=db_model.recommendation_score,
            score_breakdown=ScoreBreakdown(**score_breakdown_data),
            recommendation_reasoning=db_model.recommendation_reasoning or "",
            compliance_notes=db_model.compliance_notes or "",
            is_selected=db_model.is_selected,
            edited_text=db_model.edited_text,
            created_at=db_model.created_at,
        )


class GenerationResponse(BaseModel):
    """Schema for communication generation response."""

    campaign_id: int
    communications: list[CommunicationResponse]
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    total_generated: int = Field(..., description="Total number of variations generated")

    class Config:
        from_attributes = True

    @classmethod
    def create(cls, campaign_id: int, communications: list[CommunicationResponse]):
        """Create a generation response with computed fields."""
        return cls(
            campaign_id=campaign_id,
            communications=communications,
            generated_at=datetime.utcnow(),
            total_generated=len(communications),
        )


class CommunicationUpdate(BaseModel):
    """Schema for updating a communication."""

    is_selected: bool | None = Field(
        None, description="Mark this variation as selected for the campaign"
    )
    edited_text: str | None = Field(
        None, description="User-edited version of the communication text"
    )


class RegenerateRequest(BaseModel):
    """Schema for regeneration request with parameter updates."""

    updated_params: dict[str, Any] = Field(
        default_factory=dict, description="Updated campaign parameters for regeneration"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "updated_params": {
                    "customization": {
                        "tone": "friendly",
                        "custom_instructions": "Make it more conversational",
                        "length_preference": "shorter",
                    }
                }
            }
        }
