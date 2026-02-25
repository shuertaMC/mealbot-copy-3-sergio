"""Query parameter and general helpers (migrated from utils.go)."""

from flask import request


def get_query_param(key):
    """Extract a single query parameter from the current Flask request.

    Returns a tuple of (value, error_message).
    If the parameter is missing, returns (None, error_message).

    Equivalent to Go's getQueryParam.
    """
    value = request.args.get(key)
    if value is None:
        return None, f"Request query parameters must contain {key}"
    return value, None


def get_query_params(keys):
    """Extract multiple query parameters from the current Flask request.

    Returns a tuple of (values_list, error_message).
    If any parameter is missing, returns (None, error_message).

    Equivalent to Go's getQueryParams.
    """
    values = []
    for key in keys:
        value = request.args.get(key)
        if value is None:
            return None, f"Request query parameters does not contain {key}"
        values.append(value)
    return values, None
