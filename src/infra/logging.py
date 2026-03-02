"""Structured JSON logging setup and request ID middleware.

Provides:
- JSON-format structured logging with timestamp, level, logger, message, request_id
- Request ID middleware that generates a UUID for each incoming request
- Context variable for propagating request ID to log records
"""

import json
import logging
import uuid
from contextvars import ContextVar
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

# Context variable to hold the current request ID
request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)


class JSONFormatter(logging.Formatter):
    """Format log records as JSON objects for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, Any] = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add request_id if available
        req_id = request_id_ctx.get()
        if req_id:
            log_entry["request_id"] = req_id

        # Add function name if set
        if hasattr(record, "function_name"):
            log_entry["function"] = record.function_name

        # Add status if set
        if hasattr(record, "status_code"):
            log_entry["status"] = record.status_code

        # Add exception info if present
        if record.exc_info and record.exc_info[1]:
            log_entry["exception"] = str(record.exc_info[1])

        return json.dumps(log_entry)


def setup_logging(level: int = logging.INFO) -> None:
    """Configure the root logger with JSON formatting."""
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers to avoid duplicate output
    root_logger.handlers.clear()
    root_logger.addHandler(handler)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware that generates a unique request ID for each incoming request.

    The request ID is stored in a context variable and can be accessed via
    ``request_id_ctx.get()``. It is also added to the response headers as
    ``X-Request-ID``.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Use incoming X-Request-ID header if present, otherwise generate one
        req_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request_id_ctx.set(req_id)

        response = await call_next(request)
        response.headers["X-Request-ID"] = req_id

        return response


def get_logger(name: str) -> logging.Logger:
    """Return a logger with the given name."""
    return logging.getLogger(name)
