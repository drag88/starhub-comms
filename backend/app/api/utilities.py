"""
Utility API endpoints for configuration data and health checks.
"""
from fastapi import APIRouter, HTTPException, status
from typing import Dict, List, Any
import logging

from app.services.config_loader import (
    get_cohorts,
    get_products,
    get_objectives,
    get_channel_constraints,
)
from app.schemas.common import HealthResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["utilities"])


@router.get("/cohorts", response_model=Dict[str, Any])
def list_cohorts():
    """
    List all available customer cohorts with characteristics.

    Returns cohorts organized by category with full metadata including:
    - Cohort ID
    - Display name
    - Description
    - Characteristics
    - Recommended communication approaches

    Returns:
        Dictionary with flattened cohort list and category information
    """
    try:
        cohorts_config = get_cohorts()

        # Flatten structure for easy frontend consumption
        all_cohorts = []
        for category, cohorts in cohorts_config.items():
            for cohort in cohorts:
                all_cohorts.append({
                    **cohort,
                    "category": category
                })

        logger.info(f"Retrieved {len(all_cohorts)} cohorts across {len(cohorts_config)} categories")

        return {
            "cohorts": all_cohorts,
            "total": len(all_cohorts),
            "categories": list(cohorts_config.keys())
        }

    except Exception as e:
        logger.error(f"Failed to retrieve cohorts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve cohorts: {str(e)}"
        )


@router.get("/products", response_model=Dict[str, Any])
def list_products():
    """
    List all product lines from configuration.

    Returns products organized by category with metadata including:
    - Product ID
    - Display name
    - Description
    - Category
    - Key features
    - Target segments

    Returns:
        Dictionary with flattened product list and category information
    """
    try:
        products_config = get_products()

        # Flatten structure
        all_products = []
        for category, products in products_config.items():
            for product in products:
                all_products.append({
                    **product,
                    "category": category
                })

        logger.info(f"Retrieved {len(all_products)} products across {len(products_config)} categories")

        return {
            "products": all_products,
            "total": len(all_products),
            "categories": list(products_config.keys())
        }

    except Exception as e:
        logger.error(f"Failed to retrieve products: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve products: {str(e)}"
        )


@router.get("/objectives", response_model=Dict[str, Any])
def list_objectives():
    """
    List supported communication objectives.

    Returns all available objectives with:
    - Objective ID
    - Display name
    - Description
    - Typical channels
    - Key messaging guidance

    Returns:
        Dictionary with objectives list and total count
    """
    try:
        objectives = get_objectives()

        logger.info(f"Retrieved {len(objectives)} objectives")

        return {
            "objectives": objectives,
            "total": len(objectives)
        }

    except Exception as e:
        logger.error(f"Failed to retrieve objectives: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve objectives: {str(e)}"
        )


@router.get("/channels", response_model=Dict[str, Any])
def list_channels():
    """
    List supported communication channels with constraints.

    Returns detailed information about each channel including:
    - Channel name
    - Length constraints
    - Format requirements
    - Compliance requirements (opt-out, unsubscribe)
    - Best practices

    Returns:
        Dictionary with channel configurations
    """
    try:
        channels = {
            "email": get_channel_constraints("email"),
            "sms": get_channel_constraints("sms"),
            "push": get_channel_constraints("push")
        }

        logger.info("Retrieved channel constraints for all channels")

        return {
            "channels": channels,
            "total": len(channels),
            "supported_channels": list(channels.keys())
        }

    except Exception as e:
        logger.error(f"Failed to retrieve channel constraints: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve channel constraints: {str(e)}"
        )


@router.get("/health", response_model=HealthResponse)
def health_check():
    """
    System health check endpoint.

    Checks the status of:
    - API service
    - Database connectivity
    - Configuration loading
    - Generation service
    - Scoring service

    Returns:
        Health status with service details
    """
    try:
        # Test database connectivity
        from database import SessionLocal
        db = SessionLocal()
        try:
            db.execute("SELECT 1")
            database_status = "connected"
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            database_status = "disconnected"
        finally:
            db.close()

        # Test configuration loading
        try:
            get_cohorts()
            get_products()
            get_objectives()
            config_status = "loaded"
        except Exception as e:
            logger.error(f"Configuration health check failed: {e}")
            config_status = "error"

        # Test generation service
        try:
            from app.services.generation_service import GenerationService
            service = GenerationService()
            generation_status = "ready"
        except Exception as e:
            logger.error(f"Generation service health check failed: {e}")
            generation_status = "error"

        # Determine overall status
        if database_status == "connected" and config_status == "loaded":
            overall_status = "healthy"
        elif database_status == "disconnected":
            overall_status = "unhealthy"
        else:
            overall_status = "degraded"

        return HealthResponse(
            status=overall_status,
            version="1.0.0",
            database=database_status,
            services={
                "generation": generation_status,
                "scoring": "ready",  # Always ready (no external dependencies)
                "config": config_status
            }
        )

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            version="1.0.0",
            database="unknown",
            services={
                "generation": "unknown",
                "scoring": "unknown",
                "config": "unknown"
            }
        )


@router.get("/info", response_model=Dict[str, Any])
def get_api_info():
    """
    Get API information and capabilities.

    Returns:
        Dictionary with API metadata, version, and capabilities
    """
    return {
        "name": "StarHub Customer Communications Generator API",
        "version": "1.0.0",
        "description": "AI-powered multi-channel customer communications with recommendation scoring",
        "capabilities": {
            "channels": ["email", "sms", "push"],
            "objectives": ["promotion", "retention", "upsell", "cross_sell", "service_update", "billing"],
            "variations_per_campaign": 5,
            "scoring_pillars": ["channel_best_practices", "cohort_alignment", "objective_effectiveness", "compliance_safety"]
        },
        "endpoints": {
            "campaigns": "/api/v1/campaigns",
            "communications": "/api/v1/campaigns/{id}/communications",
            "generation": "/api/v1/campaigns/{id}/generate",
            "cohorts": "/api/v1/cohorts",
            "products": "/api/v1/products",
            "objectives": "/api/v1/objectives",
            "channels": "/api/v1/channels",
            "health": "/api/v1/health",
            "documentation": "/docs"
        }
    }
