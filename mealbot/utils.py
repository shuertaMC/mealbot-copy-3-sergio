"""
Query parameter helpers and response utilities.

Ported from utils.go and vendor/github.com/johnamadeo/server/response.go.
Provides helper functions for extracting URL query parameters from Flask
requests and for producing JSON response bodies in the {"Message": "..."} format.
"""

import json

from flask import request


def get_query_param(key):
    """
    Get a single query parameter value from the current Flask request.

    Mirrors Go's getQueryParam: returns an error if the key is missing
    or if multiple values are provided for the same key.

    Args:
        key: The query parameter name.

    Returns:
        Tuple of (value, error_message). On success, error_message is None.
        On failure, value is None and error_message describes the issue.
    """
    values = request.args.getlist(key)
    if len(values) == 0 or len(values) > 1:
        return None, f"Request query parameters must contain {key}"
    return values[0], None


def get_query_params(keys):
    """
    Get multiple query parameter values from the current Flask request.

    Mirrors Go's getQueryParams: returns an error if any key is missing
    or has multiple values.

    Args:
        keys: List of query parameter names.

    Returns:
        Tuple of (values_list, error_message). On success, error_message is None.
        On failure, values_list is an empty list and error_message describes the issue.
    """
    values = []
    for key in keys:
        vals = request.args.getlist(key)
        if len(vals) == 0 or len(vals) > 1:
            return [], f"Request query parameters does not contain {key}"
        values.append(vals[0])
    return values, None


def str_to_bytes(message):
    """
    Convert a string message to a JSON byte string with {"Message": "..."} format.

    Mirrors Go's server.StrToBytes.

    Args:
        message: The string message.

    Returns:
        JSON string with the message wrapped in a Message object.
    """
    return json.dumps({"Message": message})


def err_to_bytes(err):
    """
    Convert an error to a JSON byte string with {"Message": "..."} format.

    Mirrors Go's server.ErrToBytes.

    Args:
        err: The error (string or Exception).

    Returns:
        JSON string with the error message wrapped in a Message object.
    """
    return json.dumps({"Message": str(err)})
