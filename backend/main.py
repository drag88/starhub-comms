"""
Main FastAPI application for StarHub Customer Communications Generator.
"""

import logging
import os

# Load environment variables from backend/.env
import pathlib
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

# Import routers
from app.api import campaigns, communications, creatives, utilities

# Import error handlers
from app.api.error_handlers import (
    general_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)

# Import database
from database import init_db

env_path = pathlib.Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.

    Handles startup and shutdown events.
    """
    # Startup: Initialize database
    logger.info("Initializing database...")
    init_db()

    # Validate environment variables
    if not os.getenv("FAL_KEY"):
        logger.warning("FAL_KEY not set - creative generation will fail")

    logger.info("Application startup complete")

    yield

    # Shutdown: Cleanup (if needed)
    logger.info("Application shutdown")


# Create FastAPI application
app = FastAPI(
    title="StarHub Customer Communications Generator API",
    description="AI-powered multi-channel customer communications with recommendation scoring",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for MVP - restrict in production
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Register error handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include API routers
app.include_router(campaigns.router)
app.include_router(communications.router)
app.include_router(utilities.router)
app.include_router(creatives.router)

logger.info("API routers registered successfully")

# Configure static file serving for creative images
from fastapi.staticfiles import StaticFiles

# Ensure static directory exists
static_dir = "backend/static"
os.makedirs(os.path.join(static_dir, "creatives"), exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")
logger.info("Static file serving configured for creative images")


@app.get("/")
async def root():
    """
    Root endpoint providing API information.

    Returns:
        dict: API information and navigation links
    """
    return {
        "message": "StarHub Customer Communications Generator API",
        "version": "1.0.0",
        "status": "active",
        "documentation": "/docs",
        "health_check": "/api/v1/health",
        "api_info": "/api/v1/info",
        "endpoints": {
            "campaigns": "/api/v1/campaigns",
            "cohorts": "/api/v1/cohorts",
            "products": "/api/v1/products",
            "objectives": "/api/v1/objectives",
            "channels": "/api/v1/channels",
        },
    }


if __name__ == "__main__":
    import uvicorn

    # Get port from environment or default to 8000
    port = int(os.getenv("PORT", 8000))

    # Run the application
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,  # Enable auto-reload for development
    )
