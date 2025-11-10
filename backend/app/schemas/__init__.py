"""
Pydantic schemas for API requests and responses.
"""
from app.schemas.campaign import (
    CustomizationOptions,
    PromotionDetails,
    CampaignCreate,
    CampaignUpdate,
    CampaignResponse,
)
from app.schemas.communication import (
    ScoreBreakdown,
    CommunicationResponse,
    GenerationResponse,
    CommunicationUpdate,
    RegenerateRequest,
)
from app.schemas.common import (
    HealthResponse,
    ErrorResponse,
    PaginatedResponse,
    MessageResponse,
)

__all__ = [
    # Campaign schemas
    "CustomizationOptions",
    "PromotionDetails",
    "CampaignCreate",
    "CampaignUpdate",
    "CampaignResponse",
    # Communication schemas
    "ScoreBreakdown",
    "CommunicationResponse",
    "GenerationResponse",
    "CommunicationUpdate",
    "RegenerateRequest",
    # Common schemas
    "HealthResponse",
    "ErrorResponse",
    "PaginatedResponse",
    "MessageResponse",
]
