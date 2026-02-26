"""
Logging helpers.

Ported from log.go. Provides convenience functions for logging and writing
HTTP responses, wrapping Python's logging module.
"""

import json
import logging

from flask import Response

logger = logging.getLogger(__name__)


def log_and_write_err(err, status, function):
    """
    Log an error and return a Flask Response with the error message as JSON.

    Mirrors Go's LogAndWriteErr: logs the error with structured fields,
    then writes a {"Message": "..."} JSON body with the given HTTP status.

    Args:
        err: The error (string or Exception).
        status: HTTP status code.
        function: Name of the calling function for log context.

    Returns:
        Flask Response object.
    """
    error_msg = str(err)
    logger.error(
        "Error in %s (status=%d): %s",
        function,
        status,
        error_msg,
    )
    body = json.dumps({"Message": error_msg})
    return Response(body, status=status, content_type="application/json")


def log_and_write(data, status, function):
    """
    Log a successful operation and return a Flask Response.

    Mirrors Go's LogAndWrite: logs at debug level with structured fields,
    then writes the provided bytes/data with the given HTTP status.

    Args:
        data: Response body (bytes or string). If bytes, used as-is.
        status: HTTP status code.
        function: Name of the calling function for log context.

    Returns:
        Flask Response object.
    """
    logger.debug("Success in %s (status=%d)", function, status)
    if isinstance(data, bytes):
        body = data
    else:
        body = data
    return Response(body, status=status, content_type="application/json")


def log_and_write_status_bad_request(err, function):
    """
    Log and return a 400 Bad Request response.

    Mirrors Go's LogAndWriteStatusBadRequest.
    """
    return log_and_write_err(err, 400, function)


def log_and_write_status_internal_server_error(err, function):
    """
    Log and return a 500 Internal Server Error response.

    Mirrors Go's LogAndWriteStatusInternalServerError.
    """
    return log_and_write_err(err, 500, function)
