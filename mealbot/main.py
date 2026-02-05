"""FastAPI application entry point.

This module creates and configures the FastAPI application,
mirroring the Go server.go main() function structure.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from .config import get_settings
from .middleware.cors import add_cors_middleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context manager.

    Handles startup and shutdown events.
    """
    settings = get_settings()
    logger.info(f"Starting Mealbot API on port {settings.port}")
    yield
    logger.info("Shutting down Mealbot API")


# Create FastAPI application instance
app = FastAPI(
    title="Mealbot API",
    description="Meal pairing application API",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware (must be added first to handle preflight requests)
add_cors_middleware(app)

# Routers will be added in future tasks:
# from .routers import members, organizations, rounds, pairs
# app.include_router(members.router)
# app.include_router(organizations.router)
# app.include_router(rounds.router)
# app.include_router(pairs.router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint for verifying the application is running."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "mealbot.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=True,
    )
