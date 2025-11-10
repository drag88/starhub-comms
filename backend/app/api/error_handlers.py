"""
Error handling middleware and exception handlers for the API.
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle Pydantic validation errors.

    Provides detailed error information for invalid request data.

    Args:
        request: The incoming request
        exc: The validation exception

    Returns:
        JSON response with validation error details
    """
    errors = exc.errors()
    logger.warning(f"Validation error on {request.url.path}: {errors}")

    # Convert errors to serializable format
    serializable_errors = []
    for error in errors:
        error_dict = {
            "type": error.get("type"),
            "loc": error.get("loc"),
            "msg": error.get("msg"),
            "input": error.get("input")
        }
        serializable_errors.append(error_dict)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "error_type": "ValidationError",
            "errors": serializable_errors,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Handle HTTP exceptions.

    Provides consistent error response format for all HTTP errors.

    Args:
        request: The incoming request
        exc: The HTTP exception

    Returns:
        JSON response with error details
    """
    logger.warning(f"HTTP {exc.status_code} on {request.url.path}: {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_type": f"HTTP{exc.status_code}Error",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle general exceptions.

    Catches all unhandled exceptions and returns a 500 error.

    Args:
        request: The incoming request
        exc: The exception

    Returns:
        JSON response with error details
    """
    logger.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "error_type": type(exc).__name__,
            "message": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


async def database_exception_handler(request: Request, exc: Exception):
    """
    Handle database-related exceptions.

    Provides specific handling for database connectivity and integrity errors.

    Args:
        request: The incoming request
        exc: The database exception

    Returns:
        JSON response with error details
    """
    logger.error(f"Database error on {request.url.path}: {exc}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "detail": "Database service unavailable",
            "error_type": "DatabaseError",
            "message": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )
