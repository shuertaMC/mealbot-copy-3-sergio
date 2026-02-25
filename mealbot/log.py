"""
Logging helpers.

Migrated from: log.go

Provides structured logging helpers that mirror the Go Logrus-based
helpers. Each function logs the event and returns a Flask response
with the appropriate status code and JSON body.

The Go code uses a {"Message": "..."} response format (via
server.ErrToBytes / server.StrToBytes). We preserve this exact format
for API backward compatibility.
"""

import logging

from flask import jsonify, make_response

logger = logging.getLogger("mealbot")


def str_to_response(message):
    """
    Convert a string message to a JSON response body.

    Equivalent to Go's server.StrToBytes: produces {"Message": "..."}

    Args:
        message: The string message to wrap.

    Returns:
        A dict matching the Go Message struct format.
    """
    return {"Message": message}


def err_to_response(err):
    """
    Convert an error/exception to a JSON response body.

    Equivalent to Go's server.ErrToBytes: produces {"Message": "..."}

    Args:
        err: An exception or error string.

    Returns:
        A dict matching the Go Message struct format.
    """
    return {"Message": str(err)}


def log_and_write_err(err, status, function):
    """
    Log an error and return a Flask response with the given status code.

    Equivalent to Go's LogAndWriteErr.

    Args:
        err: The error (exception or string) to log and return.
        status: HTTP status code.
        function: Name of the calling function (for structured logging).

    Returns:
        A Flask Response with JSON body {"Message": "..."} and the given status.
    """
    logger.error(
        "Error in %s: %s",
        function,
        str(err),
        extra={"status": status, "function": function},
    )
    response = make_response(jsonify(err_to_response(err)), status)
    return response


def log_and_write(data, status, function):
    """
    Log a success response and return a Flask response.

    Equivalent to Go's LogAndWrite.

    Args:
        data: The response data (dict or string).
              If a string, it will be wrapped in {"Message": "..."} format.
              If a dict, it will be returned as-is as JSON.
        status: HTTP status code.
        function: Name of the calling function (for structured logging).

    Returns:
        A Flask Response with the appropriate JSON body and status.
    """
    logger.debug(
        "Response from %s: status=%d",
        function,
        status,
        extra={"function": function},
    )
    if isinstance(data, str):
        response = make_response(jsonify(str_to_response(data)), status)
    else:
        response = make_response(jsonify(data), status)
    return response


def log_and_write_status_bad_request(err, function):
    """
    Log an error and return a 400 Bad Request response.

    Equivalent to Go's LogAndWriteStatusBadRequest.

    Args:
        err: The error to log and return.
        function: Name of the calling function.

    Returns:
        A Flask Response with 400 status.
    """
    return log_and_write_err(err, 400, function)


def log_and_write_status_internal_server_error(err, function):
    """
    Log an error and return a 500 Internal Server Error response.

    Equivalent to Go's LogAndWriteStatusInternalServerError.

    Args:
        err: The error to log and return.
        function: Name of the calling function.

    Returns:
        A Flask Response with 500 status.
    """
    return log_and_write_err(err, 500, function)
