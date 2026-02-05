"""FastAPI application entry point."""

from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles

from mealbot.middleware.cors import CORSMiddleware
from mealbot.routers.organizations import router as organizations_router

# Create FastAPI application instance
app = FastAPI(
    title="Mealbot",
    description="A meal pairing and scheduling service",
    version="1.0.0",
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> PlainTextResponse:
    """Handle validation errors with plain text responses for backward compatibility."""
    # Return plain text error messages as the Go code does
    return PlainTextResponse(
        content="Request body is malformed",
        status_code=status.HTTP_400_BAD_REQUEST,
    )


# Register CORS middleware
app.add_middleware(CORSMiddleware)

# Include organization routes
app.include_router(organizations_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


# Mount static files directory
# This must come AFTER all route definitions as it catches remaining paths
# Use relative path from where the app runs (project root)
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
