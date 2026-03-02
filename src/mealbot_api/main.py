"""FastAPI application factory and ASGI entrypoint.

This module creates the FastAPI application with:
- CORS middleware matching Go's cors.go behavior
- Request ID middleware for log correlation
- Organization management routes (Milestone 1)
- Static file serving for privacy.html and sample.csv
- CLI argument handling stubs for 'pair' and 'migrate' subcommands
"""

import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

from infra.logging import RequestIDMiddleware, setup_logging
from mealbot_api.routes import orgs


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Sets up:
    - Structured JSON logging
    - CORS middleware (reflecting Origin, allowing Auth/Content-Type headers)
    - Request ID middleware
    - Organization routes (/orgs, /org, /crossmatchtrait)
    - Static file serving at root path
    """
    # Initialize structured logging
    setup_logging()

    app = FastAPI(
        title="Mealbot API",
        description="Meal pairing service",
        version="0.1.0",
    )

    # CORS middleware matching Go's GetCorsHandler behavior:
    # - Reflects the request Origin (allow_origins=["*"])
    # - Allows Authorization, Content-Type, Origin, Accept, token headers
    # - Allows GET, POST, DELETE methods
    # - Handles OPTIONS preflight automatically
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["GET", "POST", "DELETE"],
        allow_headers=[
            "Authorization",
            "Content-Type",
            "Origin",
            "Accept",
            "token",
        ],
    )

    # Request ID middleware for log correlation
    app.add_middleware(RequestIDMiddleware)

    # Register organization routes (Milestone 1)
    app.include_router(orgs.router)

    # Mount static files at root path with lower priority than API routes
    # This matches Go's: serveMux.Handle("/", http.FileServer(http.Dir("./static")))
    # Static files are served at /<filename> (e.g., /privacy.html, /sample.csv)
    static_dir = Path(__file__).resolve().parent.parent.parent / "static"
    if static_dir.is_dir():
        app.mount("/", StaticFiles(directory=str(static_dir)), name="static")

    return app


def cli_main() -> None:
    """Handle CLI arguments for 'pair' and 'migrate' subcommands.

    Mirrors the Go main() function's argument handling:
    - 'pair': runs the pairing scheduler (stub for Milestone 4)
    - 'migrate': runs the migration to last_round_with (stub for Milestone 4)
    """
    args = sys.argv
    if len(args) == 2:
        if args[1] == "pair":
            print("Pairing scheduler stub - will be implemented in Milestone 4")
            return
        elif args[1] == "migrate":
            print("Migration stub - will be implemented in Milestone 4")
            return
        else:
            print(f"argument '{args[1]}' not recognized")
            return

    # No CLI args: start the web server
    import uvicorn

    from infra.config import get_settings

    settings = get_settings()
    uvicorn.run(
        "mealbot_api.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=True,
    )


# Create the ASGI app instance for uvicorn
app = create_app()


if __name__ == "__main__":
    cli_main()
