"""
Common schemas used across the API.
"""
from pydantic import BaseModel, Field
from typing import List, Any, Generic, TypeVar
from datetime import datetime


class HealthResponse(BaseModel):
    """Health check response schema."""

    status: str = Field(..., description="Overall health status: healthy, degraded, unhealthy")
    version: str = Field(..., description="API version")
    database: str = Field(..., description="Database connection status")
    services: dict = Field(
        default_factory=dict,
        description="Status of individual services"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "database": "connected",
                "services": {
                    "generation": "ready",
                    "scoring": "ready",
                    "config": "loaded"
                }
            }
        }


class ErrorResponse(BaseModel):
    """Error response schema."""

    detail: str = Field(..., description="Error message")
    error_type: str = Field(..., description="Type of error")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="Error timestamp in ISO format"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Campaign not found",
                "error_type": "NotFoundError",
                "timestamp": "2025-11-09T10:30:00.000Z"
            }
        }


T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response schema."""

    items: List[T] = Field(..., description="List of items for current page")
    total: int = Field(..., description="Total number of items across all pages")
    page: int = Field(..., description="Current page number (1-indexed)")
    limit: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")

    class Config:
        json_schema_extra = {
            "example": {
                "items": [],
                "total": 100,
                "page": 1,
                "limit": 20,
                "pages": 5
            }
        }

    @classmethod
    def create(cls, items: List[T], total: int, page: int, limit: int):
        """Create a paginated response with computed fields."""
        pages = (total + limit - 1) // limit if limit > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            limit=limit,
            pages=pages
        )


class MessageResponse(BaseModel):
    """Simple message response schema."""

    message: str = Field(..., description="Response message")
    success: bool = Field(default=True, description="Operation success status")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Operation completed successfully",
                "success": True
            }
        }
