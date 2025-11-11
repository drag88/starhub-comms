"""
Pydantic schemas for API requests and responses.
"""

from app.schemas.campaign import (
    CampaignCreate,
    CampaignResponse,
    CampaignUpdate,
    CustomizationOptions,
    PromotionDetails,
)
from app.schemas.common import (
    ErrorResponse,
    HealthResponse,
    MessageResponse,
    PaginatedResponse,
)
from app.schemas.communication import (
    CommunicationResponse,
    CommunicationUpdate,
    GenerationResponse,
    RegenerateRequest,
    ScoreBreakdown,
)
from app.schemas.creative import (
    ChannelType,
    CreativeGenerationRequest,
    CreativeListResponse,
    CreativeSelectionRequest,
    GeneratedCreativeResponse,
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
    # Creative schemas
    "ChannelType",
    "CreativeGenerationRequest",
    "GeneratedCreativeResponse",
    "CreativeListResponse",
    "CreativeSelectionRequest",
    # Common schemas
    "HealthResponse",
    "ErrorResponse",
    "PaginatedResponse",
    "MessageResponse",
]
