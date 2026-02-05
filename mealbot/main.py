"""FastAPI application entry point."""

from fastapi import FastAPI

from mealbot.middleware.cors import CORSMiddleware

# Create FastAPI application instance
app = FastAPI(
    title="Mealbot",
    description="A meal pairing and scheduling service",
    version="1.0.0",
)

# Register CORS middleware
app.add_middleware(CORSMiddleware)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}
