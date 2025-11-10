"""
Pydantic schemas for campaign-related requests and responses.
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime


class CustomizationOptions(BaseModel):
    """Customization options for communication generation."""

    tone: str = Field(
        ...,
        description="Communication tone: friendly, urgent, premium, value-focused, professional"
    )
    custom_instructions: Optional[str] = Field(
        None,
        description="Free-text custom instructions for generation"
    )
    required_phrases: List[str] = Field(
        default_factory=list,
        description="Phrases that must appear in all variations"
    )
    prohibited_words: List[str] = Field(
        default_factory=list,
        description="Words that must not appear in communications"
    )
    length_preference: str = Field(
        default="optimal",
        description="Length preference: shorter, optimal, or longer"
    )

    @field_validator('tone')
    @classmethod
    def validate_tone(cls, v):
        """Validate tone is one of allowed values."""
        allowed = ["friendly", "urgent", "premium", "value-focused", "professional"]
        if v not in allowed:
            raise ValueError(f"Tone must be one of: {', '.join(allowed)}")
        return v

    @field_validator('length_preference')
    @classmethod
    def validate_length(cls, v):
        """Validate length preference is one of allowed values."""
        allowed = ["shorter", "optimal", "longer"]
        if v not in allowed:
            raise ValueError(f"Length preference must be one of: {', '.join(allowed)}")
        return v


class PromotionDetails(BaseModel):
    """Details about a promotion or offer."""

    promotion_name: str = Field(..., description="Name of the promotion")
    pricing: Optional[Dict[str, Any]] = Field(
        None,
        description="Pricing info: monthly_price, contract_duration, discount, bonus"
    )
    features: List[str] = Field(
        default_factory=list,
        description="Key features and benefits of the promotion"
    )
    terms_conditions: Optional[str] = Field(
        None,
        description="Terms and conditions text"
    )
    validity_start: Optional[str] = Field(
        None,
        description="Promotion start date (YYYY-MM-DD)"
    )
    validity_end: Optional[str] = Field(
        None,
        description="Promotion end date (YYYY-MM-DD)"
    )


class CampaignCreate(BaseModel):
    """Schema for creating a new campaign."""

    campaign_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Human-readable name for the campaign"
    )
    channel: str = Field(
        ...,
        pattern="^(email|sms|push)$",
        description="Communication channel: email, sms, or push"
    )
    objective: str = Field(
        ...,
        description="Campaign objective: promotion, retention, upsell, cross_sell, service_update, billing"
    )
    product_lines: List[str] = Field(
        ...,
        min_length=1,
        description="At least one product line required"
    )
    cohorts: List[str] = Field(
        ...,
        min_length=1,
        description="At least one target cohort required"
    )
    promotion_details: Optional[PromotionDetails] = Field(
        None,
        description="Optional promotion details for promotional campaigns"
    )
    customization: CustomizationOptions = Field(
        ...,
        description="Customization options for communication generation"
    )

    @field_validator('objective')
    @classmethod
    def validate_objective(cls, v):
        """Validate objective is one of allowed values."""
        allowed = ["promotion", "retention", "upsell", "cross_sell", "service_update", "billing"]
        if v not in allowed:
            raise ValueError(f"Objective must be one of: {', '.join(allowed)}")
        return v

    @field_validator('channel')
    @classmethod
    def validate_channel(cls, v):
        """Validate channel is one of allowed values."""
        allowed = ["email", "sms", "push"]
        if v not in allowed:
            raise ValueError(f"Channel must be one of: {', '.join(allowed)}")
        return v


class CampaignUpdate(BaseModel):
    """Schema for updating an existing campaign."""

    campaign_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200,
        description="Updated campaign name"
    )
    channel: Optional[str] = Field(
        None,
        pattern="^(email|sms|push)$",
        description="Updated channel"
    )
    objective: Optional[str] = Field(
        None,
        description="Updated objective"
    )
    product_lines: Optional[List[str]] = Field(
        None,
        min_length=1,
        description="Updated product lines"
    )
    cohorts: Optional[List[str]] = Field(
        None,
        min_length=1,
        description="Updated cohorts"
    )
    promotion_details: Optional[PromotionDetails] = Field(
        None,
        description="Updated promotion details"
    )
    customization: Optional[CustomizationOptions] = Field(
        None,
        description="Updated customization options"
    )

    @field_validator('objective')
    @classmethod
    def validate_objective(cls, v):
        """Validate objective if provided."""
        if v is not None:
            allowed = ["promotion", "retention", "upsell", "cross_sell", "service_update", "billing"]
            if v not in allowed:
                raise ValueError(f"Objective must be one of: {', '.join(allowed)}")
        return v

    @field_validator('channel')
    @classmethod
    def validate_channel(cls, v):
        """Validate channel if provided."""
        if v is not None:
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
    product_lines: List[str]
    cohorts: List[str]
    promotion_details: Optional[Dict[str, Any]] = None
    customization: Dict[str, Any]
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
            product_lines=json.loads(db_model.product_lines) if isinstance(db_model.product_lines, str) else db_model.product_lines,
            cohorts=json.loads(db_model.cohorts) if isinstance(db_model.cohorts, str) else db_model.cohorts,
            promotion_details=json.loads(db_model.promotion_details) if db_model.promotion_details and isinstance(db_model.promotion_details, str) else db_model.promotion_details,
            customization=json.loads(db_model.customization) if isinstance(db_model.customization, str) else db_model.customization,
            created_at=db_model.created_at,
            updated_at=db_model.updated_at
        )
