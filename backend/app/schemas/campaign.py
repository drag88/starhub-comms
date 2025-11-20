"""
Pydantic schemas for campaign-related requests and responses.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


class CustomizationOptions(BaseModel):
    """Customization options for communication generation."""

    tone: str = Field(
        ...,
        description="Communication tone: friendly, urgent, premium, value-focused, professional",
    )
    custom_instructions: str | None = Field(
        None, description="Free-text custom instructions for generation"
    )
    required_phrases: list[str] = Field(
        default_factory=list, description="Phrases that must appear in all variations"
    )
    prohibited_words: list[str] = Field(
        default_factory=list, description="Words that must not appear in communications"
    )
    length_preference: str = Field(
        default="optimal", description="Length preference: shorter, optimal, or longer"
    )

    @field_validator("tone", mode="before")
    @classmethod
    def validate_tone(cls, v):
        """Validate tone is one of allowed values."""
        v = v.lower() if isinstance(v, str) else v
        allowed = ["friendly", "urgent", "premium", "value-focused", "professional"]
        if v not in allowed:
            raise ValueError(f"Tone must be one of: {', '.join(allowed)}")
        return v

    @field_validator("length_preference", mode="before")
    @classmethod
    def validate_length(cls, v):
        """Validate length preference is one of allowed values."""
        if isinstance(v, str):
            v = v.lower()
            # Map common incorrect values
            mapping = {
                "short": "shorter",
                "medium": "optimal",
                "long": "longer",
                "normal": "optimal",
                "default": "optimal",
            }
            v = mapping.get(v, v)

        allowed = ["shorter", "optimal", "longer"]
        if v not in allowed:
            raise ValueError(f"Length preference must be one of: {', '.join(allowed)}")
        return v


class PromotionDetails(BaseModel):
    """Details about a promotion or offer."""

    promotion_name: str = Field(..., description="Name of the promotion")
    pricing: dict[str, Any] | None = Field(
        None, description="Pricing info: monthly_price, contract_duration, discount, bonus"
    )
    features: list[str] = Field(
        default_factory=list, description="Key features and benefits of the promotion"
    )
    terms_conditions: str | None = Field(None, description="Terms and conditions text")
    validity_start: str | None = Field(None, description="Promotion start date (YYYY-MM-DD)")
    validity_end: str | None = Field(None, description="Promotion end date (YYYY-MM-DD)")


class CampaignCreate(BaseModel):
    """Schema for creating a new campaign."""

    campaign_name: str = Field(
        ..., min_length=1, max_length=200, description="Human-readable name for the campaign"
    )
    channel: str = Field(
        ..., pattern="^(email|sms|push)$", description="Communication channel: email, sms, or push"
    )
    objective: str = Field(
        ...,
        description="Campaign objective: promotion, retention, upsell, cross_sell, service_update, billing",
    )
    product_lines: list[str] = Field(
        ..., min_length=1, description="At least one product line required"
    )
    cohorts: list[str] = Field(..., min_length=1, description="At least one target cohort required")
    promotion_details: PromotionDetails | None = Field(
        None, description="Optional promotion details for promotional campaigns"
    )
    customization: CustomizationOptions = Field(
        ..., description="Customization options for communication generation"
    )

    @field_validator("objective", mode="before")
    @classmethod
    def validate_objective(cls, v):
        """Validate objective is one of allowed values."""
        v = v.lower() if isinstance(v, str) else v
        allowed = ["promotion", "retention", "upsell", "cross_sell", "service_update", "billing"]
        if v not in allowed:
            raise ValueError(f"Objective must be one of: {', '.join(allowed)}")
        return v

    @field_validator("channel", mode="before")
    @classmethod
    def validate_channel(cls, v):
        """Validate channel is one of allowed values."""
        v = v.lower() if isinstance(v, str) else v
        allowed = ["email", "sms", "push"]
        if v not in allowed:
            raise ValueError(f"Channel must be one of: {', '.join(allowed)}")
        return v


class CampaignUpdate(BaseModel):
    """Schema for updating an existing campaign."""

    campaign_name: str | None = Field(
        None, min_length=1, max_length=200, description="Updated campaign name"
    )
    channel: str | None = Field(
        None, pattern="^(email|sms|push)$", description="Updated channel"
    )
    objective: str | None = Field(None, description="Updated objective")
    product_lines: list[str] | None = Field(
        None, min_length=1, description="Updated product lines"
    )
    cohorts: list[str] | None = Field(None, min_length=1, description="Updated cohorts")
    promotion_details: PromotionDetails | None = Field(
        None, description="Updated promotion details"
    )
    customization: CustomizationOptions | None = Field(
        None, description="Updated customization options"
    )

    @field_validator("objective", mode="before")
    @classmethod
    def validate_objective(cls, v):
        """Validate objective if provided."""
        if v is not None:
            v = v.lower() if isinstance(v, str) else v
            allowed = [
                "promotion",
                "retention",
                "upsell",
                "cross_sell",
                "service_update",
                "billing",
            ]
            if v not in allowed:
                raise ValueError(f"Objective must be one of: {', '.join(allowed)}")
        return v

    @field_validator("channel", mode="before")
    @classmethod
    def validate_channel(cls, v):
        """Validate channel if provided."""
        if v is not None:
            v = v.lower() if isinstance(v, str) else v
            allowed = ["email", "sms", "push"]
            if v not in allowed:
                raise ValueError(f"Channel must be one of: {', '.join(allowed)}")
        return v


class CampaignResponse(BaseModel):
    """Schema for campaign response."""

    campaign_id: int
    campaign_name: str
    channel: str
    objective: str
    product_lines: list[str]
    cohorts: list[str]
    promotion_details: dict[str, Any] | None = None
    customization: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_model(cls, db_model):
        """
        Convert database model to response schema.

        This method handles JSON field parsing from database.
        """
        import json

        return cls(
            campaign_id=db_model.campaign_id,
            campaign_name=db_model.campaign_name,
            channel=db_model.channel,
            objective=db_model.objective,
            product_lines=json.loads(db_model.product_lines)
            if isinstance(db_model.product_lines, str)
            else db_model.product_lines,
            cohorts=json.loads(db_model.cohorts)
            if isinstance(db_model.cohorts, str)
            else db_model.cohorts,
            promotion_details=json.loads(db_model.promotion_details)
            if db_model.promotion_details and isinstance(db_model.promotion_details, str)
            else db_model.promotion_details,
            customization=json.loads(db_model.customization)
            if isinstance(db_model.customization, str)
            else db_model.customization,
            created_at=db_model.created_at,
            updated_at=db_model.updated_at,
        )
