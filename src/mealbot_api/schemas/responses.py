"""Response models matching the Go application's response format.

The Go application wraps string responses in a Message struct:
    type Message struct { Message string }

This produces JSON like: {"Message": "Successfully created new organization"}

These helpers ensure the Python API returns the exact same format.
"""

import logging
from typing import Any

from fastapi import Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from infra.logging import request_id_ctx

logger = logging.getLogger(__name__)


class MessageResponse(BaseModel):
    """Standard message response matching Go's Message struct.

    Note: The field name is capitalized 'Message' to match the Go struct's
    JSON serialization (Go uses PascalCase by default for exported fields).
    """

    Message: str


def message_response(message: str, status_code: int = 200) -> JSONResponse:
    """Return a JSONResponse with the standard Message format.

    Args:
        message: The message string to wrap.
        status_code: HTTP status code for the response.

    Returns:
        JSONResponse with {"Message": "<message>"} body.
    """
    return JSONResponse(
        content={"Message": message},
        status_code=status_code,
    )


def error_response(error: str | Exception, status_code: int = 500) -> JSONResponse:
    """Return an error JSONResponse with the standard Message format.

    Matches Go's LogAndWriteErr behavior: logs the error and returns
    {"Message": "<error>"} with the given status code.

    Args:
        error: The error message or exception.
        status_code: HTTP status code for the response.

    Returns:
        JSONResponse with {"Message": "<error>"} body.
    """
    error_msg = str(error)
    return JSONResponse(
        content={"Message": error_msg},
        status_code=status_code,
    )


def log_and_error(
    error: str | Exception,
    status_code: int,
    function: str,
) -> JSONResponse:
    """Log an error and return an error response.

    Equivalent to Go's LogAndWriteErr function.
    """
    error_msg = str(error)
    logger.error(
        error_msg,
        extra={"function_name": function, "status_code": status_code},
    )
    return error_response(error_msg, status_code)


def log_and_respond(
    data: Any,
    status_code: int,
    function: str,
) -> JSONResponse:
    """Log a successful response and return it.

    Equivalent to Go's LogAndWrite function.
    For structured data (dicts, lists), returns as-is.
    For MessageResponse-like data, wraps appropriately.
    """
    logger.debug(
        f"status={status_code}",
        extra={"function_name": function, "status_code": status_code},
    )
    return JSONResponse(content=data, status_code=status_code)
