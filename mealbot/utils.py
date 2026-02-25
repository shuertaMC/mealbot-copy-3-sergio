"""
Query parameter and general helpers.

Migrated from: utils.go

Provides utility functions for extracting and validating query
parameters from Flask requests, mirroring the Go getQueryParam
and getQueryParams functions.
"""

from flask import request


def get_query_param(key):
    """
    Extract a single query parameter value from the current request.

    Equivalent to Go's getQueryParam. Returns the value for the given key,
    or raises ValueError if the parameter is missing or has multiple values.

    Args:
        key: The query parameter name to extract.

    Returns:
        The string value of the query parameter.

    Raises:
        ValueError: If the parameter is missing or has multiple values.
    """
    values = request.args.getlist(key)
    if len(values) == 0 or len(values) > 1:
        raise ValueError(
            f"Request query parameters must contain {key}"
        )
    return values[0]


def get_query_params(keys):
    """
    Extract multiple query parameter values from the current request.

    Equivalent to Go's getQueryParams. Returns a list of values
    corresponding to the given keys, in order.

    Args:
        keys: A list of query parameter names to extract.

    Returns:
        A list of string values, one per key, in the same order.

    Raises:
        ValueError: If any parameter is missing or has multiple values.
    """
    values = []
    for key in keys:
        params = request.args.getlist(key)
        if len(params) == 0 or len(params) > 1:
            raise ValueError(
                f"Request query parameters does not contain {key}"
            )
        values.append(params[0])
    return values
