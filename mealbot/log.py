"""Logging helpers (migrated from log.go).

Provides structured logging and response-writing helpers equivalent to the
Go Logrus-based helpers: LogAndWriteErr, LogAndWrite, etc.
"""

import json
import logging

from flask import make_response

logger = logging.getLogger("mealbot")


def str_to_bytes(message):
    """Serialize a string into a JSON {"Message": "..."} response body.

    Equivalent to Go's server.StrToBytes().
    """
    return json.dumps({"Message": message})


def err_to_bytes(err):
    """Serialize an error/exception into a JSON {"Message": "..."} response body.

    Equivalent to Go's server.ErrToBytes().
    """
    return json.dumps({"Message": str(err)})


def log_and_write_err(err, status, function):
    """Log an error and return a Flask response with the given status code.

    Equivalent to Go's LogAndWriteErr.
    """
    logger.error("function=%s status=%d error=%s", function, status, err)
    response = make_response(err_to_bytes(err), status)
    response.headers["Content-Type"] = "application/json"
    return response


def log_and_write(data, status, function):
    """Log a debug message and return a Flask response with the given data.

    Equivalent to Go's LogAndWrite.
    """
    logger.debug("function=%s status=%d", function, status)
    response = make_response(data, status)
    response.headers["Content-Type"] = "application/json"
    return response


def log_and_write_status_bad_request(err, function):
    """Return a 400 Bad Request response with error details."""
    return log_and_write_err(err, 400, function)


def log_and_write_status_internal_server_error(err, function):
    """Return a 500 Internal Server Error response with error details."""
    return log_and_write_err(err, 500, function)
